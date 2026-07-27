# Category 10: Conventions — 宣告順序 / 命名 / JSX Prop 排序

## 宣告順序

檔案層級: `Imports → Types/Interfaces → Constants → Component`

元件內部:
```tsx
export function MyComponent({ ... }: Props) {
  // 1. Pure hooks（useNavigate、useContext）
  // 2. Local states（useState、useRef）
  // 3. Stateful hooks（依賴 props or state 的 hook）
  // 4. Derived values（從 props/state/query data 計算）
  // 5. Handlers / callbacks
  // 6. Effects（useEffect、useLayoutEffect）
  // 7. return JSX / return values
}
```

## 命名

| 場景 | 規則 | 範例 |
|------|------|------|
| 變數 / 函式 | `camelCase` | `userName`, `fetchData` |
| 常數 | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 元件 | `PascalCase`，名稱與資料夾同名，放 `index.tsx` | `UserCard/index.tsx` |
| Custom hook | `use` 前綴，放 `hooks/` 或同層 `useXxx.ts` | `useAuth`, `useDebounce` |
| 元件內部事件 handler | `handle{Action}` | `handleClickDelete` |
| 父層傳入的 callback prop | `on{Action}` | `onDelete` |
| Boolean 變數 / state | `is` / `has` / `can` 前綴 | `isLoading`, `hasError`, `canSubmit` |

## JSX Prop 排序

屬性超過 2 個時換行，每行一個 prop，依下列順序排列：

| 順序 | 分組 | 典型屬性 |
|------|------|----------|
| 1 | React 特殊 props | `key`, `ref` |
| 2 | 樣式 | `className`, `style` |
| 3 | 識別 / a11y | `id`, `role`, `aria-*`, `data-*` |
| 4 | 靜態元件型態 / 變體 | `variant`, `size`, `type` |
| 5 | 動態狀態旗標 | `disabled`, `required`, `open`, `readOnly` |
| 6 | 主資料綁定 | `value`, `defaultValue`, `checked`, `files` |
| 7 | 顯示內容 / 文案 | `placeholder`, `label`, `src`, `href`, `title` |
| 8 | 結構性 slot | `icon`, `render`, `trailingIcon`, `leadingIcon` |
| 9 | 事件處理 | `onChange`, `onClick`, `on*` |
| 10 | 透傳 | `{...rest}` |

核心邏輯：**從靜到動、從元件本體到互動** -- 先描述「是什麼」（1-4 身份/外觀/型態）、再講「裡面裝什麼」（5-8 資料/狀態/顯示/結構）、最後綁「對外怎麼互動」（9-10 事件/透傳），`{...rest}` 一定最末，避免明確 prop 被隱式覆寫。範例如下：

```tsx
<Input
  ref={inputRef}
  className="w-full"
  id="email"
  type="email"
  required
  value={email}
  placeholder={t('emailHint')}
  leadingIcon={<MailIcon />}
  onChange={setEmail}
  {...rest}
/>
```

**例外**：構造短小、一眼讀完的 JSX（例如 `<img src={src} alt={alt} {...props} />`）可由開發者自行決定是否套用拆行，可讀性優先於形式上的合規。
