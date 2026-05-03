# Category 4: Security — 解法與 Review Comment

## Red Flag: XSS Vulnerabilities

```typescript
// ❌ BLOCK: XSS vulnerability
function Comment({ comment }: { comment: string }) {
  return <div dangerouslySetInnerHTML={{ __html: comment }} />;
  // User can inject <script>alert('XSS')</script>
}

// ✅ APPROVE: Sanitize HTML
import DOMPurify from 'dompurify';

function Comment({ comment }: { comment: string }) {
  const sanitized = DOMPurify.sanitize(comment);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}

// ✅ BETTER: Use markdown or text
function Comment({ comment }: { comment: string }) {
  return <div>{comment}</div>; // React escapes by default
}
```

**Review comment：** 標註 XSS 風險，建議 sanitize 或改為文字顯示。

---

## Red Flag: Exposing Sensitive Data

```typescript
// ❌ BLOCK: Leaking API keys
const API_KEY = "sk-123456789" // Hardcoded in frontend
fetch(`https://api.com?key=${API_KEY}`)

// ❌ BLOCK: Logging sensitive data
console.log("User password:", password)
console.log("Credit card:", creditCard)

// ✅ APPROVE: Use environment variables (server-side)
// This should be in backend, not frontend
const response = await fetch("/api/proxy", {
  headers: { Authorization: "Bearer server-side-token" },
})

// ✅ APPROVE: Never log sensitive data
console.log("User logged in:", user.id) // ID only, no sensitive data
```

**Review comment：** 指出硬編碼或 log 敏感資料的風險，建議改為後端 proxy / 不 log。

---

## Red Flag: Insecure Data Handling

```typescript
// ❌ QUESTION: Is this input sanitized?
function SearchResults({ query }: { query: string }) {
  const results = await fetch(`/api/search?q=${query}`)
  // What if query contains SQL injection attempts?
}

// ✅ APPROVE: Use URL encoding
function SearchResults({ query }: { query: string }) {
  const encodedQuery = encodeURIComponent(query)
  const results = await fetch(`/api/search?q=${encodedQuery}`)
}
```

**Review comment：** 建議查詢參數等一律 encode，並檢查是否有其他未驗證輸入。
