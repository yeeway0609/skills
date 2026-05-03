# Category 1: Type Safety — 解法與 Review Comment

## Red Flag: Type Assertions (`as`) Without Justification

```typescript
// ❌ QUESTION: Why is this safe?
const value = unknownData as ComplexType

// ❌ BLOCK: Lying to TypeScript
const response = await fetch("/api/user")
const user = (await response.json()) as User // What if server returns different shape?

// ✅ APPROVE: Runtime validation
import { z } from "zod"

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
})

const response = await fetch("/api/user")
const data = await response.json()
const user = UserSchema.parse(data) // Throws if invalid
```

**Review comment 範本：**

```
🤔 This type assertion looks risky. Can we add runtime validation?

const UserSchema = z.object({...});
const user = UserSchema.parse(data);

Or if we're confident about the API shape, add a comment explaining why the assertion is safe.
```

---

## Red Flag: Missing Null/Undefined Checks

```typescript
// ❌ BLOCK: Potential null reference error
function UserProfile({ user }: { user: User | null }) {
  return <div>{user.name}</div>; // Crashes if user is null
}

// ❌ QUESTION: Is this safe?
const firstUser = users[0];
console.log(firstUser.name); // What if array is empty?

// ✅ APPROVE: Proper null handling
function UserProfile({ user }: { user: User | null }) {
  if (!user) return <div>No user found</div>;
  return <div>{user.name}</div>;
}

const firstUser = users[0];
if (firstUser) {
  console.log(firstUser.name);
}

// Or use optional chaining
console.log(users[0]?.name);
```

**Review comment：** 指出可能 null/undefined 的存取，建議加上防禦性檢查或 early return。

---

## Red Flag: Improper Type Narrowing

```typescript
// ❌ QUESTION: This doesn't narrow the type
function processValue(value: string | number) {
  if (value) {
    // Doesn't narrow
    return value.toFixed(2) // Error: string doesn't have toFixed
  }
}

// ✅ APPROVE: Proper type guard
function processValue(value: string | number) {
  if (typeof value === "number") {
    return value.toFixed(2)
  }
  return value
}
```

**Review comment：** 說明 `if (value)` 無法縮窄 union，建議用 typeof/type guard。
