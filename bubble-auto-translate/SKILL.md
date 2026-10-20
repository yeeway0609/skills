---
name: bubble-auto-translate
description: 透過 iPhone Mirroring 自動按 Bubble（DEAR U bubble／泡泡）聊天室的翻譯鈕：從目前位置往下翻到底，回頭檢查一遍，最後停回起點。
disable-model-invocation: true
---

# bubble-auto-translate

透過 Mac 的 iPhone Mirroring 操作使用者的 iPhone，在 Bubble 聊天室把每則訊息旁的灰色翻譯鈕（圓形、A＋環形箭頭）按掉；按了鈕就消失，訊息下方出現譯文。

語言是固定的，不看畫面猜，也不問使用者確認：

- **原文**：韓文，偶爾夾英文。其他語言不支援。
- **譯文**：繁體中文。只有使用者呼叫這個 skill 時另外指定譯文語言（例如英文、日文、簡中），才在跑 `probe.py` 時加上 `PH_BUBBLE_TARGET=<Vision 語言代碼>`（`en-US`、`ja-JP`、`zh-Hans`）。
- **只讀白色訊息泡泡**：錨點文字只取白色泡泡內的字，照片、貼圖上的字一律略過，不需要翻譯也不參與判斷。

只支援 macOS ＋ iPhone（iPhone Mirroring）：腳本用 macOS 的 Quartz 與 Vision 判讀畫面，按鈕、彈窗與燈箱的判斷條件也都是在 iOS 版 Bubble 上量的。使用者用的是 Android、雲端手機，或不是 Mac，就直接告知不支援，結束這個 skill。

以下 `<skill>` 指這個 skill 的資料夾（載入時顯示的 base directory）。所有腳本都在 phone-harness 裡執行，並用 `PH_BUBBLE_DIR` 告訴腳本自己在哪：

```bash
S="<skill>/scripts"
PH_BUBBLE_DIR="$S" phone-harness < "$S/probe.py"
```

## 步驟

### 1. 確認 phone-harness

執行 `command -v phone-harness`。

- 有路徑：往下一步。
- 沒有：請使用者安裝並設定好再回來，附上這些指令（使用者可以在 Claude Code 輸入 `! <指令>` 直接執行）：
  ```bash
  uv tool install phone-harness      # 沒有 uv 就用 pipx install phone-harness
  phone-harness doctor ios           # 檢查 iPhone Mirroring 與權限，照它的訊息處理
  ```
  需求：macOS 15 以上、iOS 18 以上、所在地區可以使用 iPhone Mirroring，終端機要有「螢幕錄製」與「輔助使用」權限。設定問題的完整說明在 https://github.com/ShawnPana/phone-harness/blob/main/install.md 。已測試版本：phone-harness 0.3.2。

裝好後執行 `phone-harness config get platform`，確認 phone-harness 要操作的是 iPhone：

- 印出 `"ios"`：往下一步。
- 其他值（例如 `"android"`）：腳本會去操作那台裝置，用的卻是 iOS 的判斷條件，可能點錯地方。問使用者要用的是不是 Mac 上 iPhone Mirroring 連著的 iPhone：是的話，請使用者執行 `phone-harness config set platform ios`；不是的話，告知不支援，結束這個 skill。

完成條件：`command -v phone-harness` 印出路徑，`phone-harness config get platform` 印出 `"ios"`。

### 2. 取得使用者授權

在執行任何 phone-harness 腳本之前（`probe.py` 也會截圖），先把下面三點告訴使用者，詢問是否同意，並等使用者明確回答同意。同一段對話裡同意一次即可，中斷後接續不用再問。

1. **截屏檢測**：Bubble 每偵測到一次截圖，就會跳出「截屏檢測」警告。這個流程每頁都要截圖，並會代替使用者按下警告裡的「我同意上述內容」，一次流程會按上百次。
2. **帳號風險**：自動截圖與自動操作可能違反 Bubble 的使用條款，App 可能記錄截圖行為。這是非官方工具，風險由使用者自行承擔。
3. **隱私**：截圖只存在這台 Mac 的暫存資料夾，OCR 在本機執行，腳本結束時一律刪除截圖。對話紀錄裡只會出現起點附近的幾行訊息文字（當作找回起點的錨點）。

使用者回答同意，才往下走。回答不同意或沒有正面回答，就停在這裡，結束這個 skill。

### 3. 確認畫面已就緒

需要的畫面：iPhone Mirroring 已連上，Bubble 聊天室停在要開始翻譯的位置，畫面上看得到至少一個時間戳記。

先用不截圖的方式查連線狀態：

```bash
phone-harness <<'PY'
print(connection_state())
PY
```

- 印出 `ready`，或使用者已經說過畫面準備好了：直接往下一步。畫面若其實不在聊天室，下一步的 `probe.py` 會回報 `RESULT not-chat`，到時再處理。
- 其他狀態：請使用者打開 iPhone Mirroring，進入聊天室並停在要開始的位置，等使用者說好了再往下。

不論哪種情況，都順帶提醒使用者把滑鼠移離 Mirroring 視窗；滑鼠停在視窗上會讓 Mirroring 斷線。這只是提醒，不用等使用者回覆。

### 4. 量手機參數

```bash
PH_BUBBLE_DIR="$S" phone-harness < "$S/probe.py"
```

`probe.py` 只截圖、按掉截屏檢測彈窗、往下捲一頁再捲回來，不會按翻譯鈕。它量的是這台手機的同意鈕位置、聊天背景、捲一次實際移動多少，連同固定的 OCR 語言存進參數檔給 `translate_all.py` 讀。依最後一行處理：

- `RESULT ok`：用一兩句話帶過參數摘要，**不要停下來問使用者確認，直接進下一步**。翻譯鈕偵測到 0 個也照樣開始：這頁可能都翻過了，翻譯階段會逐頁再找。
- `RESULT background`：聊天背景太暗、是圖片或花紋，翻譯鈕抓不到，OCR 也容易讀錯。最常見的原因是聊天室還在用藝人設定的原生背景，這類背景多半是圖片。請使用者到這個聊天室的背景設定，改選設定裡提供的淺色純色選項（例如米色）；手機若是深色模式，也先改成淺色。換好後重跑這一步。
- `RESULT not-chat`：畫面停在照片或別的頁面。請使用者回到聊天室，重跑這一步。
- 腳本報錯：照下方「中斷與錯誤」處理。

完成條件：輸出 `RESULT ok`。

### 5. 翻譯

放背景執行，並把進度行轉述給使用者：

```bash
PH_BUBBLE_DIR="$S" phone-harness < "$S/translate_all.py"
```

開頭會印出起點時間和「起點錨點」那一行，記下來，中斷後接續要用。流程是：往下逐頁按翻譯鈕到底 → 回到起點 → 再往下檢查一遍、補按漏掉的 → 回到起點。

完成條件：輸出 `DONE 翻譯 N 個，檢查補按 M 個，已回到起點 HH:MM`。

### 6. 回報

告訴使用者翻譯了幾個、檢查時補按幾個、最後停在哪個時間。補按多於 0 表示翻譯階段有漏按，要特別說明。整輪翻譯加補按都是 0 個時，提醒使用者：如果畫面上其實有灰色翻譯鈕，代表偵測條件跟這台手機對不上。

## 中斷與錯誤

- **Mirroring 斷線或手機被解鎖**（錯誤含 `iPhone Mirroring is not connected`、`iPhone in Use` 等）：停下來，轉述錯誤訊息，請使用者照訊息處理（常見原因是滑鼠移到 Mirroring 視窗上，或拿起手機解鎖）。使用者說好了再接續。
- **接續**：用原本的起點時間和錨點重跑，不要用當下畫面當新起點。參數檔還在，不用重跑 `probe.py`：
  ```bash
  PH_BUBBLE_START=23:47 PH_BUBBLE_ANCHOR='錨點1|錨點2' PH_BUBBLE_DIR="$S" phone-harness < "$S/translate_all.py"
  ```
- **只捲回某個時間**：
  ```bash
  PH_BUBBLE_GOTO=23:47 PH_BUBBLE_ANCHOR='錨點1|錨點2' PH_BUBBLE_DIR="$S" phone-harness < "$S/translate_all.py"
  ```
- 沒有錨點時（`PH_BUBBLE_ANCHOR` 省略）只能靠時間回起點，聊天跨日可能停在錯的那一天，要告訴使用者。
- **連續好幾頁都是「按了 0 個」，但使用者說畫面上明明有鈕**：停下來，請使用者確認背景是淺色純色，重跑 `probe.py`。
- **換了手機、改了 Mirroring 視窗大小、換了聊天背景**：重跑 `probe.py`。
