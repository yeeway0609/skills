---
name: code-review-react-ts
description: 依優先順序整理的 TypeScript React code review 指引。著重型別安全、React 慣例、效能、安全性、架構、無障礙、錯誤處理與測試。先掃描程式碼找出問題，再從 references/ 取得解法與 review comment 範本。
metadata:
  source:
    - https://cant-maintain.saschb2b.com/learn
    - https://devouringdetails.com/resources/react-handbook
    - https://dev.to/tarunmj6/code-review-for-typescript-react-what-to-look-for-41nl
---

## 流程

1. 用下方清單掃描問題 → 記下類別
2. 開對應 `references/XX.md` → 取解法與 comment 範本

## 檢查清單

| 優先 | 類別 | Red flags | Reference |
|------|------|-----------|-----------|
| 高 | Type Safety | `as` 無故、缺 null 檢查、縮窄錯誤 | `01-type-safety.md` |
| 高 | React Patterns | Hook 規則違反、deps 不完整、inline re-render、state mutate | `02-react-patterns.md` |
| 高 | Performance | render 內昂貴計算、整包 import、index key、高頻 setState | `03-performance.md` |
| 高 | Security | 未 sanitize innerHTML、hardcode key、未編碼用戶輸入 | `04-security.md` |
| 中 | Architecture | God component、prop drilling、邏輯混 UI | `05-architecture.md` |
| 中 | Accessibility | 語意化 HTML、ARIA、鍵盤操作 | `06-accessibility.md` |
| 中 | Error Handling | 未處理 rejection、吞錯不回饋 | `07-error-handling.md` |
| 中 | Testing | 難測邏輯、關鍵流程缺測試 | `08-testing.md` |
| 低 | Coding Style | Boolean/callback 命名、prop 型別過寬、互斥 boolean | `09-coding-style.md` |
| 低 | Conventions | 宣告順序、命名慣例、JSX prop 排序 | `10-conventions.md` |

> High 必修 → Medium 應修 → Low 建議性（🟡 SUGGESTION，作者可不採納）→ 忽略純個人風格

## Review Comment 原則

- 問句 > 命令：「Could we use useMemo here?」
- 說明原因 + 提供選項（不只說「加 error handling」）
- 🔴 BLOCKING（XSS、型別/邏輯錯誤）・🟡 SUGGESTION（可優化）・🟢 PRAISE
