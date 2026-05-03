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
