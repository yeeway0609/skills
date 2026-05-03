# Category 7: Error Handling — 解法與 Review Comment

## Red Flag: Unhandled Promise Rejections

```typescript
// ❌ QUESTION: What if this fails?
useEffect(() => {
  fetchData().then(setData)
}, [])

// ✅ APPROVE: Error handling
useEffect(() => {
  fetchData()
    .then(setData)
    .catch((error) => {
      console.error("Failed to fetch data:", error)
      setError(error)
    })
}, [])

// ✅ BETTER: Async/await with try-catch
useEffect(() => {
  async function loadData() {
    try {
      const data = await fetchData()
      setData(data)
    } catch (error) {
      console.error("Failed to fetch data:", error)
      setError(error)
    }
  }

  loadData()
}, [])
```

**Review comment：** 指出失敗時使用者無從得知，建議補上 catch 與錯誤呈現。

---

## Red Flag: Silent Failures

```typescript
// ❌ BLOCK: Errors disappear
try {
  await updateUser(userId, data)
} catch (error) {
  // Nothing happens - user thinks it worked!
}

// ✅ APPROVE: Show error to user
try {
  await updateUser(userId, data)
  toast.success("Profile updated")
} catch (error) {
  toast.error("Failed to update profile")
  console.error(error)
}
```

**Review comment：** 標註 catch 空實作會讓使用者以為成功，建議至少 toast + console.error。
