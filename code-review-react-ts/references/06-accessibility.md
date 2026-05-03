# Category 6: Accessibility — 解法與 Review Comment

## Red Flag: Missing Semantic HTML

```typescript
// ❌ QUESTION: Not accessible
function Button({ onClick, label }) {
  return (
    <div onClick={onClick} className="button">
      {label}
    </div>
  );
}

// ✅ APPROVE: Proper semantics
function Button({ onClick, label }) {
  return <button onClick={onClick}>{label}</button>;
}
```

**Review comment：** 建議改用語意化標籤以利無障礙與 SEO。

---

## Red Flag: Missing ARIA Labels

```typescript
// ❌ QUESTION: Screen reader won't know what this is
<button onClick={handleClose}>
  <X /> {/* Icon only */}
</button>

// ✅ APPROVE: Accessible
<button onClick={handleClose} aria-label="Close dialog">
  <X />
</button>

// ✅ ALSO GOOD: Visible text
<button onClick={handleClose}>
  <X />
  <span>Close</span>
</button>
```

**Review comment：** 指出螢幕報讀無法辨識圖示按鈕，建議加 aria-label 或可見文字。

---

## Red Flag: Keyboard Navigation Issues

```typescript
// ❌ QUESTION: Can't navigate with keyboard
<div onClick={handleClick}>Click me</div>

// ✅ APPROVE: Keyboard accessible
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Click me
</div>

// ✅ BETTER: Use button element
<button onClick={handleClick}>Click me</button>
```

**Review comment：** 建議改為 button 或補齊鍵盤事件，讓鍵盤可操作。
