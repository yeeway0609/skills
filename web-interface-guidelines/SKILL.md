---
name: web-interface-guidelines
description: 在實作或檢視網頁介面時，對照 raunofreiberg/interfaces《Web Interface Guidelines》繁中版的一組實務準則，讓互動、視覺與無障礙等細節更符合「好介面」期待。
metadata:
  source: https://github.com/raunofreiberg/interfaces
---

# Web Interface Guidelines

本文件列出一些能讓（網頁）**介面變好**的細節，**並非窮舉**。這是一份會依經驗**持續更新**的文件。其中有些項目可能帶有主觀性，但大多數適用於所有網站。

本文**刻意不重複** [WAI-ARIA](https://www.w3.org/TR/wai-aria-1.1/) 規格內容，但仍可能點出部分無障礙相關準則。歡迎貢獻：編輯[此檔案](https://github.com/raunofreiberg/interfaces/blob/main/README.md)並提交 pull request。

## Interactivity

- 點擊輸入欄位的 label 應讓該輸入欄位取得焦點
- 輸入欄位應包在 `<form>` 內，以便按下 Enter 送出
- 輸入欄位應使用適當的 `type`，例如 `password`、`email` 等
- 多數情況下，輸入欄位應停用 `spellcheck` 與 `autocomplete` 屬性
- 適當時，輸入欄位應透過 `required` 屬性善用 HTML 表單驗證
- 輸入欄位的前綴與後綴裝飾（例如圖示）應以絕對定位疊在文字輸入框上並配合 padding，而非擺在旁邊，且點擊時應讓輸入欄位取得焦點
- 切換開關（Toggles）應立即生效，無需再經確認
- 送出後應停用按鈕，以避免重複的網路請求
- 可互動元素應對其內層內容停用 `user-select`
- 裝飾性元素（光暈、漸層等）應停用 `pointer-events`，以免攔截事件
- 垂直或水平列表中的可互動元素之間不應有無法點擊的空白；應改為增加它們的 `padding`

## Typography

- 字體應套用 `-webkit-font-smoothing: antialiased` 以提升易讀性
- 字體應套用 `text-rendering: optimizeLegibility` 以提升易讀性
- 字體應依內容、字母表或相關語言進行子集化（subset）
- 在 hover 或選取狀態下不應改變字重，以免版面位移
- 不應使用低於 400 的字重
- 中等尺寸的標題一般以字重 500–600 看起來最佳
- 使用 CSS [`clamp()`](https://developer.mozilla.org/en-US/docs/Web/CSS/clamp) 流暢調整數值，例如標題的 `font-size`：`clamp(48px, 5vw, 72px)`
- 在適用情況下應使用 `font-variant-numeric: tabular-nums` 套用等寬數字（tabular figures），特別是在表格中，或在不希望版面位移的情況（例如計時器）
- 在 iOS 的橫向模式下，使用 `-webkit-text-size-adjust: 100%` 避免文字意外縮放

## Motion

- 切換主題時，不應觸發元素上的 transition 與動畫 [^1]
- 互動動畫的持續時間不應超過 200ms，才會感覺即時
- 動畫數值應與觸發元素的尺寸成比例：
  - 不要將對話框從 scale 0 動到 1；改為淡入透明度並從約 0.8 縮放
  - 按鈕按下時不要從 1 縮到 0.8，而是約 0.96、0.9 之類
- 頻繁且新鮮感低的操作應避免多餘動畫：[^2]
  - 開啟右鍵選單
  - 從列表刪除或新增項目
  - 對瑣碎按鈕 hover
- 循環播放的動畫在畫面上不可見時應暫停，以減輕 CPU 與 GPU 負載
- 導向頁內錨點時使用 `scroll-behavior: smooth`，並保留適當的偏移量

## Touch

- 觸控按下時不應顯示 hover 狀態，請使用 `@media (hover: hover)` [^3]
- 輸入欄位字體不應小於 16px，以免 iOS 在聚焦時放大畫面
- 觸控裝置上不應自動聚焦輸入欄位，否則會開啟鍵盤並遮住畫面
- 在 `<video />` 標籤套用 `muted` 與 `playsinline` 以便在 iOS 自動播放
- 對實作平移與縮放手勢的自訂元件停用 `touch-action`，以免與縮放、捲動等原生行為互相干擾
- 以 `-webkit-tap-highlight-color: rgba(0,0,0,0)` 停用 iOS 預設的點擊高亮，但務必改以合適的替代視覺回饋

## Optimizations

- `filter` 與 `backdrop-filter` 若使用過大的 `blur()` 數值可能很慢
- 對填滿的矩形做縮放與模糊會造成色帶（banding），請改用放射狀漸層（radial gradients）
- 僅在必要時少量使用 `transform: translateZ(0)` 啟用 GPU 繪製，以改善效能不佳的動畫
- 針對效能不佳的捲動動畫，僅在動畫進行期間切換 `will-change` [^4]
- 在 iOS 上自動播放過多影片會拖垮裝置；請暫停或卸載畫面外的影片
- 對可即時寫入 DOM 的數值，可用 ref 繞過 React 的 render 生命週期直接提交 [^5]
- [偵測並適應](https://github.com/GoogleChromeLabs/react-adaptive-hooks)使用者裝置的硬體與網路能力

## Accessibility

- 停用的按鈕不應有 tooltip，否則無法被無障礙使用 [^6]
- 焦點環（focus rings）應使用 box shadow，而非無法配合圓角的 outline [^7]
- 可循序聚焦列表中的元素應能以 <kbd>↑</kbd> <kbd>↓</kbd> 導覽
- 可循序聚焦列表中的元素應能以 <kbd>⌘</kbd> <kbd>Backspace</kbd> 刪除
- 若要按下後立即開啟，下拉選單應在 `mousedown` 觸發，而非 `click`
- 使用內含可依 `prefers-color-scheme` 配合系統主題的 style 標籤之 SVG favicon
- 僅有圖示的可互動元素應定義明確的 `aria-label`
- 由 hover 觸發的 tooltip 不應包含可互動內容
- 圖片應一律以 `<img>` 呈現，以利螢幕閱讀器與從右鍵選單複製
- 以 HTML 構成的插圖應有明確的 `aria-label`，而不要向螢幕閱讀器朗讀原始 DOM 樹
- 漸層文字在 `::selection` 狀態應取消漸層
- 使用巢狀選單時，使用「預測錐（prediction cone）」避免滑鼠移經其他元素時誤關閉選單

## Design

- 樂觀地在本地更新資料，若伺服器錯誤則回滾並給予回饋
- 認證導向應在 client 載入前於伺服器端完成，以避免 URL 變更不順暢
- 以 `::selection` 設定文件選取狀態的樣式
- 回饋應相對於觸發來源呈現：
  - 複製成功時顯示短暫的行內勾選，而非通知
  - 表單錯誤時標示相關輸入欄位
- 空狀態應提示建立新項目，並可選附範本

[^1]: 在深色與淺色模式之間切換時，會觸發本來給明確互動（如 hover）用的元素 transition。可[暫時停用 transition](https://paco.me/writing/disable-theme-transitions) 以避免此情況。若使用 Next.js，可使用 [next-themes](https://github.com/pacocoursey/next-themes)，其內建避免此問題。

[^2]: 這屬於品味問題，但有些互動在沒有動效時感覺更好。例如 macOS 原生右鍵選單僅在關閉時有動畫、開啟時沒有，因為使用頻率很高。

[^3]: 多數觸控裝置在按下時會短暫閃現 hover 狀態，除非明確僅為指標裝置定義 [`@media (hover: hover)`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/hover)。

[^4]: 僅將 [`will-change`](https://developer.mozilla.org/en-US/docs/Web/CSS/will-change) 作為最後手段以改善效能。預先大量套用在元素上以求效能，可能適得其反。

[^5]: 這點可能有爭議，但有時直接操作 DOM 是有益的。例如，不必在每次 wheel 事件都依賴 React re-render，而可在 ref 中追蹤增量，並在 callback 中直接更新相關元素。

[^6]: 停用的按鈕不會出現在 DOM 的 tab 順序中，因此 tooltip 永遠不會被鍵盤使用者聽見，他們也不會知道按鈕為何停用。

[^7]: 截至 2023 年，Safari 在自訂 outline 樣式時不會將元素的 border radius 納入考量。[Safari 16.4](https://developer.apple.com/documentation/safari-release-notes/safari-16_4-release-notes) 已支援 outline 沿著圓角。但仍請記得，不是所有人都會立即更新作業系統。
