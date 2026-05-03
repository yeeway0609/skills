# Category 8: Testing — 解法與 Review Comment

## Red Flag: Untestable Code

```typescript
// ❌ QUESTION: Hard to test - API call inside component
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
  }, [userId]);

  return <div>{user?.name}</div>;
}

// ✅ APPROVE: Extract hook - easy to test
function useUser(userId: string) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
  }, [userId]);

  return user;
}

function UserProfile({ userId }: { userId: string }) {
  const user = useUser(userId);
  return <div>{user?.name}</div>;
}
```

**Review comment：** 建議抽出 hook/函數以便撰寫單元測試。

---

## Red Flag: Missing Critical Tests

```typescript
// Component that handles payments
function CheckoutForm() {
  const handleSubmit = async (data) => {
    await processPayment(data);
    await createOrder(data);
    await sendConfirmation(data);
  };

  return <form onSubmit={handleSubmit}>...</form>;
}

// ❌ QUESTION: Where are the tests?
// No tests for:
// - Payment processing
// - Error handling
// - Edge cases
```

**Review comment 範本：**

```
⚠️ This component handles payment processing but I don't see tests. Could we add:

1. Test successful payment flow
2. Test payment failure handling
3. Test validation errors
4. Test edge cases (e.g., network timeout)

Payment code should have high test coverage.
```
