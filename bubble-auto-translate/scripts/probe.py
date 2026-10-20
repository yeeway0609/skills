# task: Bubble 聊天室自動翻譯：先量這台手機的參數
# step: 截圖量彈窗按鈕、背景、捲動幅度，寫進參數檔；不按任何翻譯鈕
#
# 用法（PH_BUBBLE_DIR 指向這個 scripts 資料夾）：
#   PH_BUBBLE_DIR=<skill>/scripts phone-harness < <skill>/scripts/probe.py
# 環境變數：
#   PH_BUBBLE_TARGET=<Vision 語言代碼>  譯文語言，預設 zh-Hant（繁中）；例如 en-US、ja-JP、zh-Hans
# 最後一行是 RESULT：
#   RESULT ok                    參數已存，可以開始翻譯
#   RESULT background            聊天背景太暗、太花或是圖片，請使用者換淺色純色背景
#   RESULT not-chat              畫面不在聊天室
import os, shutil, sys, time

sys.dont_write_bytecode = True                              # 不在 skill 資料夾留下 __pycache__
sys.path.insert(0, os.environ.get("PH_BUBBLE_DIR") or sys.exit("要設定 PH_BUBBLE_DIR=<skill>/scripts"))
import bubble, detect
from bubble import P

# 原文只有韓文（偶爾夾英文），譯文預設繁中。語言固定，不看畫面猜：
# 照片、貼圖上的字會讓自動偵測多出泰文、日文等，OCR 語言越多越容易讀錯
TARGET = os.environ.get("PH_BUBBLE_TARGET") or "zh-Hant"
LANGS = list(dict.fromkeys(["ko-KR", TARGET, "en-US"]))


def first_chat_shot():
    """回傳乾淨的聊天截圖與同意鈕位置。乾淨畫面截一次圖約 0.5 秒後才跳彈窗，
    所以拿到聊天畫面後再等一下截第二張，在彈窗上量同意鈕的位置並按掉。"""
    agree = None
    for _ in range(6):
        p = bubble.shot("probe.png")
        btn = detect.dialog_button(p)
        if btn:
            agree = btn; bubble.rtap(*btn); time.sleep(1.3)
            continue
        if detect.state(p) == "viewer":
            return None, agree
        time.sleep(1.5)
        btn = detect.dialog_button(bubble.shot("probe-dialog.png"))
        if btn:
            agree = btn; bubble.rtap(*btn); time.sleep(1.3)
        return p, agree
    return None, agree


def measure_scroll(p0):
    """捲一次 page，比對前後畫面，算出內容移動了聊天區的幾成，再捲回來。
    往回多捲一點：停得比原位置高只是多翻幾則，停得低會漏掉起點上方的訊息。"""
    before = detect.profile(p0)
    bubble.scroll_once(P["page"])
    after = detect.profile(bubble.capture("probe-after.png"))
    bubble.dismiss_pending()
    bubble.scroll_once(P["page"] * 1.15, "up")
    bubble.capture("probe-back.png"); bubble.dismiss_pending()
    if detect.same_screen(before, after):
        return None, "捲動後畫面沒變（可能已在最底部），沿用預設捲動量"
    f = detect.shift(before, after)
    if f is None:
        return None, "比對不出捲動距離，沿用預設捲動量"
    return f, None


def main():
    ensure_device()
    w = find_window()
    p, agree = first_chat_shot()
    if p is None:
        print("RESULT not-chat"); return
    W, H, _ = detect.load(p)
    params = dict(P)
    if agree:
        params["agree"] = [round(agree[0], 3), round(agree[1], 3)]
    params["langs"] = LANGS
    bubble.P.update(params); detect.configure(params)

    bg = detect.background(p)
    n_btn = len(detect.buttons(p))
    n_msg = sum(1 for _, ry in bubble.ocr(p, bubbles_only=True) if 0.17 < ry < 0.94)

    print(f"視窗 {w['w']}×{w['h']} pt，截圖 {W}×{H} px")
    print(f"截屏檢測同意鈕：{params['agree'] if agree else '沒看到彈窗，沿用預設 ' + str(P['agree'])}")
    print(f"背景：亮度 {bg['lum']}，飽和度 {bg['sat']}，主色佔 {bg['share']:.0%}，{'可用' if bg['ok'] else '不可用'}")
    print(f"這頁偵測到翻譯鈕 {n_btn} 個")
    print(f"OCR 語言：{LANGS}（原文韓文、英文，譯文 {TARGET}）")
    print(f"白色訊息泡泡內讀到 {n_msg} 行文字（照片、貼圖上的字不算）")
    if not bg["ok"]:
        print("RESULT background"); return

    f, note = measure_scroll(p)
    if f:
        k = min(1.5, max(0.5, 0.33 / f))      # 讓翻譯時每頁約捲聊天區的三分之一
        for key in ("page", "check", "seek", "fine"):
            params[key] = round(P[key] * k, 2)
        print(f"捲動 {P['page']} 移動聊天區 {f:.0%}，調整後每頁捲 {params['page']}")
    else:
        print(note)
    bubble.save_params(params)
    print(f"參數已存到 {bubble.PARAMS}")
    print("RESULT ok")


try:
    main()
finally:
    shutil.rmtree(bubble.SHOTS, ignore_errors=True)       # 截圖一律刪除
