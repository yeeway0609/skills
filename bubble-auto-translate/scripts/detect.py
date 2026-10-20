"""Bubble 聊天室截圖的像素判讀：翻譯鈕、畫面狀態、背景、捲動比對。

門檻是在寬約 326px 的截圖上量出來的。phone-harness 平常給 point 解析度的截圖，
視窗在別的桌面空間時會退回 Retina（2 倍），iPhone 型號不同視窗寬度也不同，
所以每張圖都用 s = 寬 / 326 換算尺寸類門檻；顏色門檻不隨尺寸變。
只用 Quartz 讀像素，phone-harness 的 Python 就能直接跑。
"""
import math

import Quartz
from Foundation import NSURL

REF_W = 326
AGREE_Y = 0.656     # 截屏檢測彈窗藍色按鈕的高度比例；probe.py 量出這台手機的值後由 configure() 覆寫


def configure(params):
    global AGREE_Y
    AGREE_Y = params.get("agree", (0, AGREE_Y))[1]


def load(p):
    src = Quartz.CGImageSourceCreateWithURL(NSURL.fileURLWithPath_(p), None)
    img = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    W, H = Quartz.CGImageGetWidth(img), Quartz.CGImageGetHeight(img)
    ctx = Quartz.CGBitmapContextCreate(None, W, H, 8, W*4, Quartz.CGColorSpaceCreateDeviceRGB(),
                                       Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextDrawImage(ctx, Quartz.CGRectMake(0, 0, W, H), img)
    return W, H, bytes(Quartz.CGBitmapContextGetData(ctx).as_buffer(W*H*4))


def _px(buf, W, H, rx, ry):
    i = (min(int(H*ry), H-1)*W + min(int(W*rx), W-1))*4
    return buf[i], buf[i+1], buf[i+2]


def _is_blue(r, g, b):
    return b > r + 60 and b > 150


def state(p):
    """'dialog'（截屏檢測彈窗）、'viewer'（照片燈箱，頂端全黑）或 'chat'。
    彈窗看按鈕的藍色像素而不是 OCR：介面語言不同時文字會變，顏色不變。"""
    W, H, buf = load(p)
    if all(_is_blue(*_px(buf, W, H, rx, AGREE_Y)) for rx in (0.2, 0.3, 0.7, 0.8)):
        return "dialog"
    if all(sum(_px(buf, W, H, rx, 0.135)) < 120 for rx in (0.3, 0.5, 0.7)):
        return "viewer"
    return "chat"


def dialog_button(p):
    """截屏檢測彈窗藍色寬按鈕的中心 (rx, ry)；畫面上沒有就回傳 None。

    找畫面中段藍色像素橫跨超過一半寬度的列，取這些列的中心。
    不靠固定座標，所以不同 iPhone 的版面也找得到。藍色區塊要像按鈕一樣矮，
    才不會把聊天裡的藍天照片當成按鈕點下去（誤點照片會開燈箱）。
    """
    W, H, buf = load(p)
    s = W / REF_W
    rows = []
    for y in range(int(H*0.35), int(H*0.9)):
        xs = [x for x in range(0, W, 2) if _is_blue(*_px(buf, W, H, x/W, y/H))]
        if len(xs)*2 > W*0.5:
            rows.append((y, min(xs), max(xs)))
    if not rows:
        return None
    ys = [r[0] for r in rows]
    if not (20*s <= max(ys)-min(ys)+1 <= 70*s):
        return None
    x0, x1 = min(r[1] for r in rows), max(r[2] for r in rows)
    return ((x0+x1)/2/W, (min(ys)+max(ys))/2/H)


def background(p):
    """聊天背景主色的亮度、飽和度、佔比，以及翻譯鈕偵測能不能用（ok）。

    翻譯鈕是中灰色圓，偵測靠「灰圓上半圈外面是亮背景」：背景要夠亮、接近無彩、
    是大片純色。深色模式、深色或圖片背景會讓鈕抓不到，OCR 也容易讀錯。
    """
    W, H, buf = load(p)
    counts = {}
    total = 0
    for y in range(int(H*0.2), int(H*0.9), 4):
        for x in range(int(W*0.05), int(W*0.95), 4):
            i = (y*W+x)*4
            key = (buf[i]//8, buf[i+1]//8, buf[i+2]//8)
            counts[key] = counts.get(key, 0) + 1
            total += 1
    (r, g, b), n = max(counts.items(), key=lambda kv: kv[1])
    r, g, b = r*8+4, g*8+4, b*8+4
    lum, sat, share = (r+g+b)//3, max(r, g, b)-min(r, g, b), n/total
    return {"lum": lum, "sat": sat, "share": round(share, 2),
            "ok": lum >= 222 and sat <= 40 and share >= 0.35}


def in_white_bubble(img, box, pad=6):
    """OCR 文字框（比例座標 x0, y0, x1, y1，原點在左上）是否在白色訊息泡泡裡。

    看文字框左右兩側外推 pad 的直線：泡泡內距比這寬，所以落在泡泡的白底上。
    只看左右不看上下：多行訊息的上下緊貼著別行文字，會被字形誤判成非白。
    聊天背景（米色等）亮度約 233，照片底色不一，都會被 245 的門檻排除。
    img 是 load() 的結果，同一張圖的每一行共用，不重複解碼。
    """
    W, H, buf = img
    s = W / REF_W
    x0, y0, x1, y1 = box
    ya, yb = int(y0*H), int(y1*H)
    pts = [(int(x), y) for x in (x0*W - pad*s, x1*W + pad*s)
           for y in range(ya, yb+1, max(1, (yb-ya)//6))]
    pts = [(x, y) for x, y in pts if 0 <= x < W and 0 <= y < H]
    if not pts:
        return False
    white = 0
    for x, y in pts:
        r, g, b = _px(buf, W, H, x/W, y/H)
        if (r+g+b)//3 >= 245 and max(r, g, b)-min(r, g, b) <= 10:
            white += 1
    return white >= 0.85*len(pts)


def _gray_blobs(W, H, buf, s, lo=150, hi=218, maxsat=28, x0=0.15, y0=0.13, y1=0.95):
    """低飽和度中灰像素的連通區塊。

    maxsat 28：米色聊天背景下翻譯鈕會帶黃，飽和度 22～25；設 18 時一顆都抓不到。
    米色背景本身亮度約 232，已被 hi 排除。
    """
    mask = bytearray(W*H)
    for y in range(int(H*y0), int(H*y1)):
        for x in range(int(W*x0), W-int(8*s)):
            i = (y*W+x)*4
            r, g, b = buf[i], buf[i+1], buf[i+2]
            if lo <= (r+g+b)//3 <= hi and max(r, g, b)-min(r, g, b) <= maxsat:
                mask[y*W+x] = 1
    seen = bytearray(W*H)
    out = []
    for start in range(W*H):
        if not mask[start] or seen[start]:
            continue
        st = [start]; seen[start] = 1; xs = []; ys = []
        while st:
            k = st.pop(); x, y = k % W, k//W; xs.append(x); ys.append(y)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (y+dy)*W+x+dx
                    if 0 <= n < W*H and mask[n] and not seen[n]:
                        seen[n] = 1; st.append(n)
        out.append({"cx": (max(xs)+min(xs))/2, "cy": (max(ys)+min(ys))/2,
                    "w": max(xs)-min(xs)+1, "h": max(ys)-min(ys)+1, "n": len(xs), "W": W, "H": H})
    return out


def buttons(p):
    """翻譯鈕：約 17px（以 326 寬計）的灰色實心圓，上半圈外面是聊天背景。

    只看上半圈：正下方是灰色時間戳記、右邊可能有已讀數字「1」，看整圈會把真的鈕濾掉。
    上半圈要求亮背景，是為了排除照片裡的灰色區塊（誤點照片會開燈箱）。
    """
    W, H, buf = load(p)
    s = W / REF_W
    out = []
    for c in _gray_blobs(W, H, buf, s):
        if not (11*s <= c["w"] <= 19*s and 15*s <= c["h"] <= 19*s
                and abs(c["w"]-c["h"]) <= 3*s and c["n"] >= 25*s*s):
            continue
        if not (H*0.17 < c["cy"] < H*0.94):            # 頂端標題列、底部被切到的不算
            continue
        ring = []
        for k in range(1, 6):
            a = math.pi + k*math.pi/6
            x, y = int(c["cx"] + 13*s*math.cos(a)), int(c["cy"] + 13*s*math.sin(a))
            if 0 <= x < W and 0 <= y < H:
                i = (y*W+x)*4
                ring.append((buf[i]+buf[i+1]+buf[i+2])//3)
        if ring and min(ring) > 205:
            out.append(c)
    return out


def profile(p, y0=0.17, y1=0.93, rows=400):
    """聊天區每一列的深色像素比例，用來比對兩張截圖是不是同一個畫面、捲了多少。

    取比例並重新取樣成固定列數，Retina 與一般截圖才能互相比較。
    """
    W, H, buf = load(p)
    m, step = int(10*W/REF_W), max(1, W // REF_W)
    cols = range(m, W-m, step)
    out = []
    for k in range(rows):
        y = int(H*(y0 + (y1-y0)*k/rows))
        dark = sum(1 for x in cols if buf[(y*W+x)*4] + buf[(y*W+x)*4+1] + buf[(y*W+x)*4+2] < 300)
        out.append(dark / len(cols))
    return out


def same_screen(a, b):
    return sum(abs(x-y) for x, y in zip(a, b)) / len(a) < 0.005


def shift(before, after, max_frac=0.6):
    """往下捲之後，內容往上移了聊天區高度的幾成；比對不出來回傳 None。

    重疊太少時差異容易碰巧很小，所以位移上限 0.6，且差異相近時取最小的位移。
    捲動距離不會剛好落在取樣列上，文字邊緣總有些差異，所以用「明顯低於一般位移的差異」
    判斷對上了，而不是要求差異接近 0。
    """
    n = len(before)
    diffs = [(k, sum(abs(x-y) for x, y in zip(before[k:], after[:n-k])) / (n-k))
             for k in range(1, int(n*max_frac))]
    ds = sorted(d for _, d in diffs)
    best_d, median = ds[0], ds[len(ds)//2]
    if best_d > 0.15 * median:                  # 合成圖實測：對上約 0.02～0.07，不相干畫面約 0.28 以上
        return None
    return next(k for k, d in diffs if d <= best_d*1.1 + 0.001) / n
