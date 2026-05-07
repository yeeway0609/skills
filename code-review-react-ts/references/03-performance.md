# Category 3: Performance — 解法與 Review Comment

## Red Flag: Expensive Operations in Render

```typescript
// ❌ QUESTION: This runs on every render
function Component({ items }: { items: Item[] }) {
  const sorted = items
    .filter(item => item.active)
    .sort((a, b) => b.priority - a.priority)
    .map(item => ({ ...item, formatted: formatItem(item) }));

  return <List items={sorted} />;
}

// ✅ APPROVE: Memoized computation
function Component({ items }: { items: Item[] }) {
  const sorted = useMemo(() =>
    items
      .filter(item => item.active)
      .sort((a, b) => b.priority - a.priority)
      .map(item => ({ ...item, formatted: formatItem(item) })),
    [items]
  );

  return <List items={sorted} />;
}
```

**Review comment：** 指出該計算在每次 render 執行，建議用 useMemo 並列出正確 deps。

---

## Red Flag: Large Bundle Imports

```typescript
// ❌ QUESTION: Importing entire library
import _ from "lodash" // Bundles all of lodash
import * as dateFns from "date-fns" // Bundles all of date-fns

_.debounce(fn, 100)
dateFns.format(date, "yyyy-MM-dd")

// ✅ APPROVE: Import only what you need
import debounce from "lodash/debounce"
import { format } from "date-fns"

debounce(fn, 100)
format(date, "yyyy-MM-dd")
```

**Review comment：** 說明 `import _ from 'lodash'` 會打包整包，建議只 import 用到的函數。

---

## Red Flag: Inefficient List Rendering

```typescript
// ❌ BLOCK: Missing keys or bad keys
items.map((item, index) => (
  <Item key={index} {...item} /> // Index as key is bad
));

items.map(item => (
  <Item {...item} /> // No key at all
));

// ✅ APPROVE: Stable, unique keys
items.map(item => (
  <Item key={item.id} {...item} />
));
```

**Review comment：** 指出 key=index 或缺少 key 的影響，建議改用穩定 id。

---

## Red Flag: 高頻互動仍走 React State / Reconciliation

拖拉、滾動、滑鼠跟隨、動畫等每秒觸發數十次的互動，若用 `useState` 觸發 re-render，會造成 jank；若 state 又不需要影響其他 UI，更是浪費。

```typescript
// ❌ QUESTION: 每次 mousemove 都 setState → 整棵子樹 re-render
function Tracker() {
  const [pos, setPos] = useState({ x: 0, y: 0 })

  return (
    <div
      onMouseMove={(e) => setPos({ x: e.clientX, y: e.clientY })}
      style={{ transform: `translate(${pos.x}px, ${pos.y}px)` }}
    />
  )
}

// ✅ APPROVE: 用 ref 直接寫 DOM，不觸發 re-render
function Tracker() {
  const ref = useRef<HTMLDivElement>(null)

  return (
    <div
      ref={ref}
      onMouseMove={(e) => {
        if (ref.current) {
          ref.current.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`
        }
      }}
    />
  )
}
```

**何時適用：**
- 該值「只影響自身視覺」，不需要其他元件知道
- 觸發頻率極高（mousemove、scroll、resize、animation frame）
- 動畫、拖拉、手勢函式庫的內部實作

**何時不適用：** 該值需要被其他元件讀取、需要進入 React 條件渲染、或需要可被測試斷言時，仍應用 state。

**Review comment：** 「這個 `mousemove` handler 每次都 `setState` 觸發整個子樹 re-render，但 `pos` 只用於自身 `transform`。建議改用 `useRef` 直接寫 DOM style，避開 reconciliation。」
