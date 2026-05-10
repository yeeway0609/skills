---
name: code-review-react-ts
license: MIT
description: 依優先順序整理的 TypeScript React code review 指引。著重型別安全、React 慣例、效能、安全性、架構、無障礙、錯誤處理與測試。先掃描程式碼找出問題，再從 references/ 取得解法與 review comment 範本。
metadata:
  source:
    - https://cant-maintain.saschb2b.com/learn
    - https://devouringdetails.com/resources/react-handbook
    - https://dev.to/tarunmj6/code-review-for-typescript-react-what-to-look-for-41nl
---

## 使用情境與工作流程

1. **第一階段（發現問題）**：用本 skill 的檢查清單掃描給定的 React/TypeScript 程式碼，列出「可能有的問題」與所屬類別。
2. **第二階段（解法與 comment）**：針對每個發現的問題，**讀取 `references/` 資料夾內對應檔案**，取得該問題的建議解法與 review comment 範本，再產出具體的優化建議或評論。

本 skill 主體只保留「要檢查什麼」；具體的程式範例、解法與 review comment 皆在 **`references/`** 下，需要時再讀取以節省 token。

---

## 審查優先順序（從上到下）

| 優先級             | 內容                                                  |
| ----------------- | ---------------------------------------------------- |
| **High（必修）**   | Security、Type safety、Logic bugs、Performance         |
| **Medium（應修）** | Architecture、Accessibility、Tests、Error handling     |
| **Low（建議）**    | Coding style / API 設計偏好（見第 9 類）、命名、小優化       |
| **忽略**           | 純個人風格、團隊未共識的偏好、bikeshedding                 |

先處理高優先級，再往下。若先評論縮排再談型別安全，順序就錯了。

---

## 檢查清單（發現問題用）

掃描時對照下列 red flags。**若發現某項，請讀取對應的 reference 檔案取得解法與 review comment。**

### 1. Type Safety（高） → `references/01-type-safety.md`

- [ ] Type assertions（`as`）無合理理由
- [ ] 缺少 null/undefined 檢查
- [ ] 型別縮窄不正確（例如只靠 `if (value)` 無法縮窄 union）

### 2. React Patterns（高） → `references/02-react-patterns.md`

- [ ] 違反 Rules of Hooks（條件/迴圈內呼叫 hook）
- [ ] useEffect/useCallback 依賴陣列不完整
- [ ] 造成不必要的 re-render（inline 函數/物件）
- [ ] 由 props 衍生的 state 未同步
- [ ] 直接 mutate state

### 3. Performance（高） → `references/03-performance.md`

- [ ] 在 render 中做昂貴計算（未 useMemo）
- [ ] 整包匯入大型套件（如 `import _ from 'lodash'`）
- [ ] 列表用 index 當 key 或沒有 key
- [ ] 高頻互動（mousemove、拖拉、動畫）用 setState 觸發 re-render，且該值不需被其他元件讀取（應改用 useRef 直接寫 DOM）

### 4. Security（高） → `references/04-security.md`

- [ ] 潛在 XSS（未 sanitize 的 `dangerouslySetInnerHTML`）
- [ ] 敏感資料外洩（硬編碼 key、log 密碼等）
- [ ] 未經編碼的使用者輸入用於 API（如 query 字串）

### 5. Architecture（中） → `references/05-architecture.md`

- [ ] God component（單一元件過大、職責過多）
- [ ] Prop drilling 過深
- [ ] 業務邏輯與 UI 混在元件內

### 6. Accessibility（中） → `references/06-accessibility.md`

- [ ] 缺少語意化 HTML（例如用 div 當按鈕）
- [ ] 僅圖示按鈕缺少 ARIA 或可見文字
- [ ] 可互動元素無法用鍵盤操作

### 7. Error Handling（中） → `references/07-error-handling.md`

- [ ] Promise 未處理 rejection（無 .catch / try-catch）
- [ ] catch 後靜默吞錯、未回饋使用者

### 8. Testing（中） → `references/08-testing.md`

- [ ] 邏輯/API 寫在元件內難以測試
- [ ] 關鍵流程（如支付）缺少對應測試

### 9. Coding Style / API Design（低，建議性） → `references/09-coding-style.md`

> 非 red flag，採用與否不影響正確性。以 🟡 SUGGESTION 提出，作者可不採納。

由上而下：修改成本由低到高（重命名 → 改型別 → API 重塑）。

🟢 簡單（重命名 / 改型別即可）

- [ ] Boolean prop 缺少 `is` / `has` / `should` 前綴（除非鏡射原生 HTML 屬性）
- [ ] Callback prop 沒用 `on*` 命名（如 `change` 而非 `onChange`、`onValueChange`）
- [ ] Prop 名稱重複 component context（`<Dialog isDialogOpen />`、`<Button buttonColor />`）
- [ ] Prop 型別過寬（用 `string` 但實際只接受少數值，應改 union literal / template literal）
- [ ] 包裝原生 HTML 元素的元件沒繼承 `React.ComponentProps<'tag'>`，導致 `onClick` / `aria-*` / `className` 無法傳入

🟡 中等（小幅 API / 型別調整）

- [ ] 用多個互斥 boolean 表達狀態，產生不可能的組合（建議改 enum / variant）
- [ ] 新增 boolean prop 表達其實可由既有 prop 推導的行為（如 `isClosable` 與 `onClose` 並存）
- [ ] Render prop 用泛用 `children` function，不知道參數意義（建議命名 `renderItem(item, state)`）
- [ ] Variant-dependent props 用普通 optional union，型別允許不可能組合（建議改 discriminated union）
- [ ] `value` / `onChange` / `options` 等共生型別寫死，未用 generic 連動推論

🔴 較大（API 結構重塑）

- [ ] 自訂表單元件只支援 controlled 或只支援 uncontrolled（應鏡射原生 `value` / `defaultValue`）
- [ ] 元件已累積 4+ 個 boolean / className prop 控制內部部位（建議考慮 compound component）
- [ ] 把 UI 結構塞進 data array 設定（如 `items={[{label, icon, submenu...}]}`），失去 JSX 表達力

---

## Review 原則（撰寫 comment 時參考）

- **用問句取代命令：** 「Could we use useMemo here?」而非「Use useMemo.」
- **說明原因：** 不只說「加 error handling」，要說「若 API 失敗使用者不知道，建議用 toast 改善 UX」。
- **提供選項：** 例如「(1) 抽成 custom hook (2) 用 React Query 做 cache」。
- **標示嚴重度：**
  - 🔴 BLOCKING：例如 XSS、嚴重型別/邏輯錯誤
  - 🟡 SUGGESTION：可優化（如 useMemo）
  - 🟢 PRAISE：值得肯定的寫法
- **專注：** Type safety、React 規則、效能、安全、架構。
- **忽略：** 個人風格、主觀偏好、bikeshedding。

---

## 總結

- **掃描階段**：用上面清單找出問題與類別，不在此處展開程式碼與長篇解法。
- **產出階段**：對每個問題開啟對應的 `references/XX-...md`，依其內容產出解法與 review comment。
