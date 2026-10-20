"""probe.py 與 translate_all.py 共用：手機操作、OCR、時間與錨點。

座標一律用視窗比例 (rx, ry)，點擊前才換成螢幕座標：視窗會移動，而截圖可能是
point 或 Retina 解析度，比例在兩者之間都成立。
"""
import json, os, re, tempfile, time
from difflib import SequenceMatcher

import Vision
from Foundation import NSURL
from phone_harness.helpers import find_window, screenshot, scroll, tap

import detect

SHOTS = os.path.join(tempfile.gettempdir(), "bubble-auto-translate")
PARAMS = os.path.join(tempfile.gettempdir(), "bubble-auto-translate-params.json")
BACK = (28/326, 97/720)     # 照片燈箱左上角返回；在一台手機上量的，頂部安全區不同的機型可能要調

# 預設值；probe.py 量過後寫進 PARAMS，load_params() 讀回來覆寫
P = {
    "agree": (0.497, 0.656),            # 截屏檢測彈窗的同意鈕
    "langs": ["ko-KR", "zh-Hant", "en-US"],
    "page": 1.2,                        # 翻譯時每頁只捲一次，約三分之一畫面；連續捲會累積慣性漏按
    "check": 1.8,                       # 檢查時每頁捲一次，約三分之二畫面
    "seek": 2.5,                        # 往上找起點，往上不會漏按
    "fine": 0.8,                        # 回起點的微調
}


def load_params():
    if not os.path.exists(PARAMS):
        raise SystemExit(f"找不到 {PARAMS}：先跑 probe.py 量這台手機的參數")
    with open(PARAMS) as f:
        P.update(json.load(f))
    detect.configure(P)
    return P


def save_params(params):
    with open(PARAMS, "w") as f:
        json.dump(params, f, ensure_ascii=False, indent=2)


# --- 手機操作 ---

def rtap(rx, ry):
    """視窗比例座標點擊。tap_image_point()、screen_info()、wait_stable()、screen()
    都會自己截圖、多帶出一個截屏檢測彈窗，所以只用 find_window() + tap()。"""
    w = find_window()
    tap(w["x"] + rx*w["w"], w["y"] + ry*w["h"])


def shot(name):
    os.makedirs(SHOTS, exist_ok=True)
    return screenshot(os.path.join(SHOTS, name))


def handle(st):
    """畫面不是聊天室時把它關掉：彈窗按同意，燈箱按返回。"""
    rtap(*(P["agree"] if st == "dialog" else BACK)); time.sleep(1.3)


def capture(name):
    """截到可用的聊天畫面。燈箱已關時再按返回會退出聊天室，所以先截圖確認才按。"""
    for _ in range(10):
        p = shot(name); st = detect.state(p)
        if st == "chat":
            return p
        handle(st)
    raise RuntimeError("回不到聊天畫面")


def dismiss_pending():
    """乾淨畫面截一次圖，約 0.5 秒後跳一個彈窗；彈窗顯示中再截圖不會多跳。
    所以等 1.5 秒截圖確認真的是彈窗才按，避免盲按點到照片。"""
    for _ in range(4):
        time.sleep(1.5)
        st = detect.state(shot("chk.png"))
        if st != "chat":
            handle(st)
            if st == "dialog":
                return


def scroll_once(amount, direction="down"):
    """每頁只捲一次：連續多次 scroll 慣性會累加、捲過頭漏按。"""
    scroll(direction, amount=amount); time.sleep(1.5)


# --- OCR ---

def ocr(p, langs=None, bubbles_only=False):
    """回傳 [(text, ry)]，ry 是行中心在視窗內的高度比例（0 在上）。
    一定要指定語言：不指定時 Vision 會把韓文讀成亂碼。
    bubbles_only：只留白色訊息泡泡裡的行，照片、貼圖上的字和聊天背景上的時間都不算。"""
    h = Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_(p), {})
    r = Vision.VNRecognizeTextRequest.alloc().init()
    r.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    r.setRecognitionLanguages_(langs or P["langs"])
    r.setUsesLanguageCorrection_(False)
    ok, err = h.performRequests_error_([r], None)
    if not ok:
        raise RuntimeError(f"OCR 失敗（語言 {langs or P['langs']}）：{err}")
    img = detect.load(p) if bubbles_only else None
    out = []
    for o in r.results() or []:
        b = o.boundingBox()                                 # Vision 的原點在左下
        top = 1 - b.origin.y - b.size.height
        if img and not detect.in_white_bubble(img, (b.origin.x, top, b.origin.x + b.size.width, top + b.size.height)):
            continue
        out.append((str(o.topCandidates_(1)[0].string()), top + b.size.height/2))
    return out


PM = re.compile(r"\b[Pp]\.?[Mm]\b|오후|午後|下午|晚上")
AM = re.compile(r"\b[Aa]\.?[Mm]\b|오전|午前|上午|早上")


def times(lines):
    """OCR 行裡的時間，回傳分鐘數（0～1439）。手機設成 12 小時制時，
    同一行的上午／下午標記（AM、오후、午後、下午⋯⋯）換算成 24 小時。"""
    out = []
    for text, _ in lines:
        for hh, mm in re.findall(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", text):
            hh, mm = int(hh), int(mm)
            if hh >= 24 or mm >= 60:
                continue
            if PM.search(text) and hh < 12:
                hh += 12
            elif AM.search(text) and hh == 12:
                hh = 0
            out.append(hh*60 + mm)
    return out


def anchors_from(lines):
    """起點畫面最上面 3 行訊息文字當錨點：按翻譯只會在下方加譯文，原文不變。
    lines 要用 ocr(p, bubbles_only=True)，照片上的字不能當錨點。
    符號、數字佔超過四分之一的行多半是 OCR 讀錯或介面文字，回頭找時比對不到，不拿來當錨點。"""
    msg = sorted((ry, t.strip()) for t, ry in lines
                 if 0.17 < ry < 0.94 and sum(ch.isalpha() for ch in t) >= 4
                 and sum(ch.isalpha() or ch.isspace() for ch in t.strip()) >= 0.75 * len(t.strip()))
    return [t for _, t in msg[:3]]


def find_anchor(lines, anchors):
    """畫面上和錨點相符的那一行的 ry；沒有就回傳 None。"""
    for a in anchors:
        for t, ry in lines:
            if SequenceMatcher(None, a, t.strip()).ratio() >= 0.8:
                return ry
    return None


def rel(t, start):
    """t 相對起點的分鐘差，跨午夜也正確（假設在 ±12 小時內）。"""
    d = (t - start) % 1440
    return d - 1440 if d > 720 else d


def hhmm(s):
    hh, mm = map(int, s.split(":"))
    return hh*60 + mm


def fmt(m):
    return f"{m//60:02d}:{m%60:02d}"
