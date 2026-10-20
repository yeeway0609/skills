# task: Bubble 聊天室：從目前位置往下逐頁按翻譯鈕，檢查一遍，再回到起點
# step: 翻譯 → 回起點檢查 → 回起點 → 刪截圖
#
# 用法（先跑過 probe.py；PH_BUBBLE_DIR 指向這個 scripts 資料夾）：
#   PH_BUBBLE_DIR=<skill>/scripts phone-harness < <skill>/scripts/translate_all.py
# 環境變數：
#   PH_BUBBLE_START=HH:MM  中斷後接續：起點改用這個時間，不從目前畫面讀
#   PH_BUBBLE_ANCHOR=a|b   起點錨點（開始時印出的那行），搭配 START 或 GOTO，避免跨日停錯
#   PH_BUBBLE_GOTO=HH:MM   只捲回這個時間，不翻譯
import os, shutil, sys, time

sys.dont_write_bytecode = True                              # 不在 skill 資料夾留下 __pycache__
sys.path.insert(0, os.environ.get("PH_BUBBLE_DIR") or sys.exit("要設定 PH_BUBBLE_DIR=<skill>/scripts"))
import bubble, detect
from bubble import P, anchors_from, capture, dismiss_pending, find_anchor, fmt, hhmm, ocr, rel, rtap, scroll_once, times


def pinned_misses(last, found):
    """上一輪由下往上按的鈕，除了最下面那顆，其餘這輪又出現、而且一起往上移了同一段距離：
    畫面黏在聊天底部，展開最下面那則的譯文把上面的訊息往上推，其餘幾下都點空了。
    回傳點空的數量；不是這種情況回傳 0。"""
    rest = sorted(last, key=lambda f: f[1])[:-1]         # 最下面那顆最先按，一定點中
    dys = []
    for x, y in rest:
        ys = [fy for fx, fy in found if abs(fx-x) < 0.012 and fy < y - 0.006]
        if not ys:
            return 0
        dys.append(y - max(ys))
    if not dys or max(dys) - min(dys) > 0.006:
        return 0
    return len(rest)


def tap_page(p, skip=(), last=()):
    """按下這頁的翻譯鈕；skip 是上一頁按過卻沒消失的位置，不再重按，last 是上一輪按過的位置。
    平常由下往上按：譯文只會把下面的訊息往下推。黏在聊天底部時相反，譯文把上面的訊息往上推，
    要由上往下按；黏住與否看上一輪點空的鈕（pinned_misses），不另外截圖。
    回傳 (按過的位置, 上一輪點空的數量)。"""
    found = [(c["cx"]/c["W"], c["cy"]/c["H"]) for c in detect.buttons(p)]
    found = [(fx, fy) for fx, fy in found if not any(abs(fx-x) < 0.012 and abs(fy-y) < 0.006 for x, y in skip)]
    missed = pinned_misses(last, found)
    dismiss_pending()
    for x, y in sorted(found, key=lambda f: f[1] if missed else -f[1]):
        rtap(x, y); time.sleep(0.7)
    return found, missed


def sweep_down(label, step, last=()):
    """往下逐頁按；捲動後畫面連續 2 次沒變就是到底，不管有沒有按到鈕
    （底部有個像翻譯鈕、按了不會消失的東西，用「沒鈕可按」判斷會卡在底部）。
    last 是進來前那頁按過的位置（起點頁），用來判斷起點頁是不是黏在底部。"""
    total, prev, still, tapped = 0, None, 0, list(last)
    for page in range(1, 300):
        p = capture("page.png")
        sig = detect.profile(p)
        unchanged = prev is not None and detect.same_screen(sig, prev)
        still = still + 1 if unchanged else 0
        if still >= 2:
            print(f"{label}：捲動後畫面連續 {still} 次沒變，到底了", flush=True)
            dismiss_pending()
            return total
        tapped, missed = tap_page(p, skip=tapped if unchanged else (), last=tapped)
        total += len(tapped) - missed                     # 點空的上一輪多算了，這輪補按時扣回
        note = f"；黏在底部，上一輪點空 {missed} 個，改由上往下按" if missed else ""
        print(f"{label} 第 {page} 頁：按了 {len(tapped)} 個（累計 {total}）{note}", flush=True)
        prev = sig
        scroll_once(P["page"] if tapped else step)        # 這頁有按鈕就退回保守捲動
    return total


def at_start(lines, start, anchors):
    """是否到了起點那頁。有錨點：要看到錨點文字，且同頁有起點前後 30 分鐘內的時間
    （起點那則的時間戳記可能剛好被切在畫面外，所以不要求完全相同）。
    沒錨點（起點全是貼圖、照片）：退回只看時間，跨日可能停錯。"""
    ts = times(lines)
    if anchors:
        return find_anchor(lines, anchors) is not None and any(abs(rel(t, start)) <= 30 for t in ts)
    return bool(ts) and min(rel(t, start) for t in ts) <= 0


def go_to_start(start, anchors):
    """往上逐頁找起點，找到後往下微調，讓錨點停在畫面上方。
    整頁時間都早於起點就是捲過頭，掉頭往下；整頁都晚於起點再掉頭往上。每次掉頭捲動量減半，
    避免來回跳過起點頁。掉頭過代表起點就在附近，這時錨點認不出（OCR 讀錯）也照時間停：
    這頁的時間橫跨起點就算到了。"""
    direction, amount, turned = "up", P["seek"], False
    for _ in range(80):
        p = capture("seek.png"); lines = ocr(p); dismiss_pending()
        ds = [rel(t, start) for t in times(lines)]
        if at_start(lines, start, anchors) or (turned and ds and min(ds) <= 0 <= max(ds)):
            break
        want = "down" if ds and max(ds) < 0 else "up" if ds and min(ds) > 0 else direction
        if want != direction:
            direction, amount, turned = want, max(amount / 2, P["fine"]), True
        scroll_once(amount, direction)
    else:
        print("警告：找了 80 頁都沒找到起點，停在目前位置", flush=True)
        return
    for _ in range(6):
        ry = find_anchor(lines, anchors) if anchors else None
        ts = times(lines)
        if anchors and (ry is None or ry <= 0.35):
            break
        if not anchors and (not ts or min(rel(t, start) for t in ts) >= 0):
            break
        scroll_once(P["fine"])
        p = capture("seek.png"); lines = ocr(p); dismiss_pending()


def main():
    bubble.load_params()
    ensure_device()                                     # 斷線時在這裡就失敗，並帶出使用者要做的事
    given = [a for a in os.environ.get("PH_BUBBLE_ANCHOR", "").split("|") if a]
    goto = os.environ.get("PH_BUBBLE_GOTO")
    if goto:
        go_to_start(hhmm(goto), given)
        print(f"DONE 已回到 {goto}", flush=True)
        return

    p0 = capture("start.png")
    lines0 = ocr(p0)
    if os.environ.get("PH_BUBBLE_START"):                # 接續：目前畫面不是起點，起點與錨點由參數給
        start, anchors = hhmm(os.environ["PH_BUBBLE_START"]), given
    else:
        ts0 = times(lines0)
        if not ts0:
            raise SystemExit("起點畫面讀不到時間，請換一個有時間戳記的位置再開始")
        start = min(ts0, key=lambda t: rel(t, ts0[0]))  # 畫面上最早的時間
        anchors = anchors_from(ocr(p0, bubbles_only=True))
    print(f"起點時間 {fmt(start)}", flush=True)
    if anchors:
        print("起點錨點（接續時用 PH_BUBBLE_ANCHOR 傳回）：" + "|".join(anchors), flush=True)
    else:
        print("警告：起點沒有可辨識的訊息文字，回起點只能靠時間，跨日可能停錯", flush=True)
    tapped0, _ = tap_page(p0)
    n0 = len(tapped0)
    print(f"起點頁：按了 {n0} 個", flush=True)
    scroll_once(P["page"])

    t1 = sweep_down("翻譯", P["page"], tapped0)
    go_to_start(start, anchors)
    t2 = sweep_down("檢查", P["check"])
    go_to_start(start, anchors)
    print(f"DONE 翻譯 {n0 + t1} 個，檢查補按 {t2} 個，已回到起點 {fmt(start)}", flush=True)


try:
    main()
finally:
    shutil.rmtree(bubble.SHOTS, ignore_errors=True)       # 這次產生的截圖一律刪除
