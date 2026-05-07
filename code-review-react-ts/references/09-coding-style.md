# Category 9: Coding Style — 建議與 Review Comment

> 章節由「修改成本由低到高」排列：上方多為重命名／改型別即可解決，下方為較大的 API 結構重塑。

---

## 🟢 簡單：重命名 / 改型別即可

### Red Flag: Boolean Prop 命名缺少語意前綴

讀 prop 看不出是 yes/no 還是值，要點進去看才知道。

```typescript
// ❌ QUESTION: 看不出是 boolean
<Modal open={true} disabled loading />
<Form valid submitted />

// ✅ APPROVE: 用 is / has / should 前綴
<Modal isOpen isDisabled isLoading />
<Form isValid hasBeenSubmitted shouldAutoFocus />
```

**例外：** 鏡射原生 HTML 屬性時保留原名（`disabled`、`required`、`checked`、`open`）以維持一致性。

**Review comment：** 「`open` 看不出是 boolean 還是值，建議用 `isOpen`。除非是直接對應到原生 HTML 屬性。」

---

### Red Flag: Callback Prop 命名不像事件

事件 callback 應以 `on` 開頭，且讀起來像自然英文。

```typescript
// ❌ QUESTION: 不像事件、語意模糊
<Slider change={...} clicked={...} valueHandler={...} />

// ✅ APPROVE: on + 事件名，讀起來自然
<Slider onValueChange={...} onClick={...} onCommit={...} />

// 內部實作的 handler 用 handle 前綴區分
function MyComp() {
  const handleValueChange = (v) => {...}
  return <Slider onValueChange={handleValueChange} />
}
```

**Review comment：** 「callback prop 慣例是 `on*`（如 `onValueChange`），呼叫端讀起來才像在訂閱事件。元件內部的 handler 可用 `handle*` 前綴區分。」

---

### Red Flag: Redundant Prop Naming（Contextual Props）

Prop 名稱重複了元件本身的 context，造成讀起來囉嗦。

```typescript
// ❌ QUESTION: 名稱重複 component context
<Dialog isDialogOpen={isDialogOpen} dialogTitle="Confirm" />
<Button buttonColor="red" buttonSize="lg" />

// ✅ APPROVE: 使用 component context 提供的簡潔命名
<Dialog isOpen={isDialogOpen} title="Confirm" />
<Button color="red" size="lg" />
```

**原則：** 在元件邊界內，周邊 context 已足以說明意義；prop 名應對「該元件」有意義，而非對外部呼叫端有意義。CSS variable 與 design token 同理。

**Review comment：** 「`dialogTitle` 在 `Dialog` 內已重複了 context，建議改為 `title`，呼叫端 `<Dialog title={...} />` 會更清楚。」

---

### Red Flag: Prop 型別過寬（缺少 Specificity）

用 `string`、`number` 接受其實只有少數有效值的輸入，呼叫端拿不到 autocomplete，也容易拼錯。

```typescript
// ❌ QUESTION: string 太寬
type Props = {
  size: string         // 其實只接受 "sm" | "md" | "lg"
  align: string        // "left" | "center" | "right"
  status: string       // "idle" | "loading" | "success" | "error"
  iconName: string     // 來自 icon set 的有限名稱
}

// ✅ APPROVE: union literal
type Props = {
  size: "sm" | "md" | "lg"
  align: "left" | "center" | "right"
  status: "idle" | "loading" | "success" | "error"
  iconName: keyof typeof iconRegistry
}

// ✅ APPROVE: template literal 表達結構化字串
type Spacing = `${0 | 1 | 2 | 4 | 8}px` | `${number}rem`
type ColorToken = `--color-${string}`
```

**Review comment：** 「`size: string` 實際只有 sm/md/lg，建議改 `'sm' | 'md' | 'lg'`，呼叫端會拿到 autocomplete，也排除拼錯。」

---

### Red Flag: 自訂元件未繼承原生 HTML Props

包裝原生元素的 component 沒繼承原生 props，導致呼叫端無法傳 `aria-*`、`data-*`、`onClick`、`className` 等基本屬性。

```typescript
// ❌ QUESTION: 只暴露自定義 props，原生屬性全被擋掉
type ButtonProps = {
  variant: "primary" | "secondary"
  size: "sm" | "md" | "lg"
}

function Button({ variant, size }: ButtonProps) {
  return <button className={cn(variant, size)} />
}
// 呼叫端無法傳 onClick、aria-label、type="submit"…

// ✅ APPROVE: 繼承原生 props，再覆蓋 / 新增語意化的
type ButtonProps = React.ComponentProps<"button"> & {
  variant?: "primary" | "secondary"
  size?: "sm" | "md" | "lg"
}

function Button({ variant, size, className, ...rest }: ButtonProps) {
  return <button className={cn(variant, size, className)} {...rest} />
}
```

**Review comment：** 「`Button` 沒繼承 `React.ComponentProps<'button'>`，呼叫端傳不了 `onClick`、`type='submit'`、`aria-label`。建議用 `React.ComponentProps<'button'> & { variant, size }`。」

---

## 🟡 中等：小幅 API / 型別調整

### Red Flag: Multiple Boolean Flags = Impossible States（Enum Props）

用多個 boolean 表達互斥狀態，會出現不該存在的組合（例如同時 primary 又 secondary）。

```typescript
// ❌ BLOCK: 互斥但型別允許 <Button isPrimary isSecondary isDanger />
type ButtonProps = {
  isPrimary?: boolean
  isSecondary?: boolean
  isDanger?: boolean
}

// ✅ APPROVE: enum 取代 boolean 群
type ButtonProps = {
  variant?: "primary" | "secondary" | "danger"
}

// ✅ APPROVE: 允許 preset + 自訂值（hybrid）
type ButtonProps = {
  color?: "accent" | "warning" | (string & {})
}
```

**好處：**
- 消除不可能的組合
- IDE autocomplete 更好
- 可直接映射為 `data-variant` attribute 寫 CSS

**Review comment：** 「`isPrimary` / `isSecondary` 互斥，但目前型別允許同時為 true。建議合併為 `variant: 'primary' | 'secondary'`，由型別系統排除無效狀態。」

---

### Red Flag: Boolean Prop Bloat（Derived Props）

每多一個行為就加一個 boolean，導致 props 越長越大，且常與既有 prop 重複表達。

```typescript
// ❌ QUESTION: isClosable 其實可由 onClose 是否存在推導
type DialogProps = {
  isOpen: boolean
  isClosable: boolean
  onClose?: () => void
}

// ✅ APPROVE: 由既有 prop 推導
type DialogProps = {
  isOpen: boolean
  onClose?: () => void // 提供 = 可關閉
}

function Dialog({ isOpen, onClose }: DialogProps) {
  const isClosable = Boolean(onClose)
  // ...
}
```

**Review comment：** 「`isClosable` 與 `onClose` 表達相同意圖。建議移除 `isClosable`，以 `onClose` 是否存在來推導，避免兩者不一致的狀態（`isClosable=true` 卻沒有 `onClose`）。」

---

### Red Flag: 用泛型 children 取代命名 Render Prop

要把內部狀態（例如 list 的 `index`、`isSelected`）傳給呼叫端時，用沒有語意的 `children` 函數，呼叫端不知道參數是什麼。

```typescript
// ❌ QUESTION: 通用 children function，不知道參數意義
<List items={items}>
  {(item, idx, isSelected) => <Row .../>}
</List>

// ✅ APPROVE: 命名 render prop，意圖明確
<List
  items={items}
  renderItem={(item, { index, isSelected }) => (
    <Row key={item.id} item={item} highlighted={isSelected} />
  )}
/>
```

**何時用 render prop（vs compound component）：**
- 呼叫端只需要客製單一部位 → render prop（`renderItem`）較輕量
- 呼叫端需要組合多個獨立部位 → compound component 較合適

**Review comment：** 「目前 `children` function 簽名不易辨識；建議改 `renderItem(item, { index, isSelected })`，命名清楚也能用 JSDoc 標示每個參數。」

---

### Red Flag: 互相依賴的 Props 用普通 Union

某些 prop 只在特定 variant 下才有意義，但型別把它們列成可選，TypeScript 阻擋不了無效組合。

```typescript
// ❌ BLOCK: 型別允許 <Avatar variant="initials" src="..." />
type AvatarProps = {
  variant: "image" | "initials" | "icon"
  src?: string       // 只有 variant="image" 用
  initials?: string  // 只有 variant="initials" 用
  icon?: ReactNode   // 只有 variant="icon" 用
}

// ✅ APPROVE: discriminated union
type AvatarProps =
  | { variant: "image"; src: string }
  | { variant: "initials"; initials: string }
  | { variant: "icon"; icon: ReactNode }

function Avatar(props: AvatarProps) {
  if (props.variant === "image") return <img src={props.src} />
  if (props.variant === "initials") return <span>{props.initials}</span>
  return <span>{props.icon}</span>
}
```

**Review comment：** 「`src` / `initials` / `icon` 只在對應 variant 下有效，但目前型別允許混用。建議改 discriminated union，由 TypeScript 排除無效組合。」

---

### Red Flag: 共生型別未用 Generic 串連

`value` / `onChange` / `options` 內含的型別應該連動，但目前各自寫死，呼叫端拿到 `any` 或要手動 cast。

```typescript
// ❌ QUESTION: 型別斷裂
type SelectProps = {
  options: { label: string; value: string }[]
  value: string
  onChange: (v: string) => void
}
// 若 value 是 number 或物件，整個型別都崩

// ✅ APPROVE: 用 generic 連動
type SelectProps<T> = {
  options: { label: string; value: T }[]
  value: T
  onChange: (v: T) => void
}

function Select<T>(props: SelectProps<T>) { /* ... */ }

// 呼叫端：T 自動推論
<Select
  options={[{ label: "A", value: 1 }, { label: "B", value: 2 }]}
  value={1}                          // T 推論為 number
  onChange={(v) => console.log(v)}   // v: number
/>
```

**Review comment：** 「`value` 與 `options[].value` 應同型別，目前都寫死 `string`。建議改 generic `<T>`，呼叫端的 value 型別會自動傳遞到 `onChange`。」

---

## 🔴 較大：API 結構重塑

### Red Flag: 自訂 Form 元件未支援 Controlled / Uncontrolled

只支援 `value` 不支援 `defaultValue`，或反過來，呼叫端被迫用不適合的模式（簡單表單也要寫 useState）。

```typescript
// ❌ QUESTION: 強制 controlled
type InputProps = { value: string; onChange: (v: string) => void }

// 呼叫端即使只是要簡單表單也要：
const [v, setV] = useState("")
<Input value={v} onChange={setV} />

// ✅ APPROVE: 鏡射原生 HTML，兩種模式都支援
type InputProps = {
  value?: string                    // controlled
  defaultValue?: string             // uncontrolled
  onChange?: (v: string) => void
}

function Input({ value, defaultValue, onChange }: InputProps) {
  const [internal, setInternal] = useState(defaultValue ?? "")
  const isControlled = value !== undefined
  const current = isControlled ? value : internal

  const handleChange = (next: string) => {
    if (!isControlled) setInternal(next)
    onChange?.(next)
  }
  // ...
}
```

**原則：** 對應到表單欄位、選擇器、開關等「有狀態」的元件，都應同時支援兩種模式，行為與原生 HTML 一致。

**Review comment：** 「目前只支援 controlled，呼叫端做簡單表單也得寫 useState。建議鏡射原生 HTML 的 `value` / `defaultValue` 雙模式，與 `<input>` 一致。」

---

### Red Flag: Configuration-heavy API（缺乏 Compound Components）

把所有變化用 props 控制，導致 prop 不斷增長（`hasArrow`、`separatorClassName`、`headerSlot`…），組合彈性差。

```typescript
// ❌ QUESTION: prop bloat、難以擴充
<Slides
  items={slides}
  hasArrow
  arrowClassName="..."
  separatorClassName="..."
  renderHeader={...}
  renderFooter={...}
/>

// ✅ APPROVE: compound component，將內部部位暴露出來
<Slides>
  <Slides.Header>...</Slides.Header>
  {slides.map(s => (
    <Slides.Slide key={s.id}>{s.content}</Slides.Slide>
  ))}
  <Slides.Arrow />
</Slides>

// 實作：
function Slides({ children }: { children: ReactNode }) { /* ... */ }
function Slide(props: SlideProps) { /* ... */ }
function Arrow() { /* ... */ }

export default Object.assign(Slides, { Slide, Header, Arrow })
```

**何時採用：**
- 元件有多個可選的內部部位（header、footer、arrow、separator…）
- 呼叫端常要客製排版或某個部位的樣式
- 出現第 4、5 個 boolean / className prop 來控制顯示時

**Review comment：** 「目前用 props 控制每個內部部位，已累積 N 個相關 prop。建議改為 compound component 把 `Slides.Slide`、`Slides.Arrow` 等暴露出來，呼叫端可直接組合，prop 表會大幅縮短。」

---

### Red Flag: Data-Driven over JSX Composition

把 UI 結構塞進資料物件，呼叫端失去 JSX 的表達力與彈性。

```typescript
// ❌ QUESTION: 全部用 config 表達 UI
<Menu
  items={[
    { label: "Edit", icon: "pencil", onClick: edit, disabled: !canEdit },
    { label: "Delete", icon: "trash", onClick: del, danger: true },
    { type: "separator" },
    { label: "Share", submenu: [...] },
  ]}
/>

// ✅ APPROVE: JSX 組合，直接傳屬性
<Menu>
  <Menu.Item icon="pencil" onClick={edit} disabled={!canEdit}>
    Edit
  </Menu.Item>
  <Menu.Item icon="trash" onClick={del} danger>
    Delete
  </Menu.Item>
  <Menu.Separator />
  <Menu.Sub label="Share">...</Menu.Sub>
</Menu>
```

**取捨：** Data-driven 較易做迴圈／序列化（例如從 API 渲染選單）；JSX-first 在可讀性、條件渲染、傳 ReactNode 子內容上勝出。多數內部 UI 元件偏好 JSX-first。

**Review comment：** 「目前 `items` 陣列把 UI 結構塞進資料，條件渲染與 ReactNode 子內容都得另開欄位。建議改為 `<Menu><Menu.Item /></Menu>` 的 JSX 組合，呼叫端可直接用 JSX 控制流。」

---

## 補充：Collection Management 的注意點

採用 compound component 時，父元件常需要知道子元件的狀態（例如鍵盤導航、第幾個 active）。處理動態 children unmount 與 register/unregister 不容易，可參考 Radix UI 的 `Collection` primitive 或類似工具，避免自己用 `Children.map` 硬刻（會在條件渲染、Fragment、巢狀時出問題）。
