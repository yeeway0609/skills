# Category 2: React Patterns — 解法與 Review Comment

## Red Flag: Breaking Rules of Hooks

```typescript
// ❌ BLOCK: Conditional hook usage
function Component({ condition }: { condition: boolean }) {
  if (condition) {
    const data = useFetch("/api/data") // Hooks must be unconditional
  }
}

// ❌ BLOCK: Hook in loop
function Component({ items }: { items: Item[] }) {
  return items.map((item) => {
    const data = useFetch(item.url) // Can't call hooks in loops
  })
}

// ✅ APPROVE: Hooks at top level
function Component({ condition }: { condition: boolean }) {
  const data = useFetch(condition ? "/api/data" : null)

  if (!condition) return null
  // Use data
}
```

**Review comment：** 標註違反 Rules of Hooks，請將 hook 移到頂層並用參數控制行為。

---

## Red Flag: Missing Dependencies in useEffect/useCallback

```typescript
// ❌ BLOCK: Stale closure bug
function Component({ userId }: { userId: string }) {
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetchUser(userId).then(setUser)
  }, []) // Missing userId dependency!

  // User won't update when userId changes
}

// ✅ APPROVE: Correct dependencies
useEffect(() => {
  fetchUser(userId).then(setUser)
}, [userId])

// ✅ ALSO GOOD: Acknowledge ESLint disable
useEffect(() => {
  // Only fetch on mount, ignoring userId changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  fetchUser(userId).then(setUser)
}, [])
```

**Review comment 範本：**

```
⚠️ `userId` is used in the effect but not in the dependency array. This means the effect won't re-run when `userId` changes, causing stale data.

Add `userId` to dependencies:
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]);
```

---

## Red Flag: Unnecessary Re-renders

```typescript
// ❌ QUESTION: This re-renders on every parent render
function Parent() {
  return (
    <Child
      onClick={() => console.log('clicked')}
      style={{ margin: 10 }}
      config={{ theme: 'dark' }}
    />
  );
}

const Child = React.memo(({ onClick, style, config }) => {
  // Child re-renders every time because new objects/functions
});

// ✅ APPROVE: Stable references
function Parent() {
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  const style = useMemo(() => ({ margin: 10 }), []);

  const config = useMemo(() => ({ theme: 'dark' }), []);

  return <Child onClick={handleClick} style={style} config={config} />;
}

// ✅ EVEN BETTER: Move static data outside component
const STYLE = { margin: 10 };
const CONFIG = { theme: 'dark' };

function Parent() {
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  return <Child onClick={handleClick} style={STYLE} config={CONFIG} />;
}
```

**Review comment：** 指出每次 render 都建立新的 function/object 導致 memo 失效，建議 useCallback/useMemo 或外提常數。

---

## Red Flag: State Derived from Props

```typescript
// ❌ QUESTION: This gets out of sync
function Component({ initialCount }: { initialCount: number }) {
  const [count, setCount] = useState(initialCount);

  // If initialCount changes, count stays the same!
  return <div>{count}</div>;
}

// ✅ APPROVE: Use the prop directly
function Component({ count }: { count: number }) {
  return <div>{count}</div>;
}

// ✅ OR: Use key to reset state when prop changes
<Component key={initialCount} initialCount={initialCount} />

// ✅ OR: Sync with useEffect (if you must)
function Component({ initialCount }: { initialCount: number }) {
  const [count, setCount] = useState(initialCount);

  useEffect(() => {
    setCount(initialCount);
  }, [initialCount]);

  return <div>{count}</div>;
}
```

**Review comment：** 說明 prop 變了但 state 不會更新會造成不同步，建議用 prop 直接或 key 重置。

---

## Red Flag: Mutating State Directly

```typescript
// ❌ BLOCK: Direct mutation
function Component() {
  const [items, setItems] = useState<Item[]>([])

  const addItem = (item: Item) => {
    items.push(item) // Mutation!
    setItems(items) // React won't detect the change
  }
}

// ✅ APPROVE: Immutable update
const addItem = (item: Item) => {
  setItems([...items, item])
}

// ✅ APPROVE: Functional update
const addItem = (item: Item) => {
  setItems((prev) => [...prev, item])
}
```

**Review comment：** 標註直接改 state 會讓 React 偵測不到變更，請改為 immutable 更新。
