# Category 5: Architecture & Design — 解法與 Review Comment

## Red Flag: God Components

```typescript
// ❌ QUESTION: 500+ lines, does everything
function Dashboard() {
  // Fetches 10 different data sources
  // Handles authentication
  // Manages complex state
  // Renders everything

  return (
    <div>
      {/* 400 lines of JSX */}
    </div>
  );
}

// ✅ APPROVE: Decomposed
function Dashboard() {
  return (
    <DashboardLayout>
      <DashboardHeader />
      <DashboardStats />
      <DashboardCharts />
      <DashboardActivity />
    </DashboardLayout>
  );
}
```

**Review comment 範本：**

```
💡 This component is doing a lot. Consider breaking it into smaller components:

- DashboardHeader (user info, navigation)
- DashboardStats (metrics cards)
- DashboardCharts (visualizations)
- DashboardActivity (recent activity)

Each can manage its own data fetching and state.
```

---

## Red Flag: Prop Drilling

```typescript
// ❌ QUESTION: Passing props through 5 levels
function App() {
  const user = useAuth();
  return <Layout user={user} />;
}

function Layout({ user }) {
  return <Sidebar user={user} />;
}

function Sidebar({ user }) {
  return <Navigation user={user} />;
}

function Navigation({ user }) {
  return <UserMenu user={user} />;
}

function UserMenu({ user }) {
  return <div>{user.name}</div>;
}

// ✅ APPROVE: Context or custom hook
const UserContext = createContext<User | null>(null);

function App() {
  const user = useAuth();
  return (
    <UserContext.Provider value={user}>
      <Layout />
    </UserContext.Provider>
  );
}

function UserMenu() {
  const user = useContext(UserContext);
  return <div>{user?.name}</div>;
}
```

**Review comment：** 建議用 Context 或 hook 取代多層傳遞。

---

## Red Flag: Mixed Concerns

```typescript
// ❌ QUESTION: Business logic in component
function ProductList() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        // Complex business logic
        const processed = data
          .filter(p => p.stock > 0)
          .map(p => ({
            ...p,
            discountedPrice: calculateDiscount(p),
            shipping: calculateShipping(p),
            taxes: calculateTaxes(p),
          }))
          .sort((a, b) => b.popularity - a.popularity);

        setProducts(processed);
      });
  }, []);

  return <div>{/* render */}</div>;
}

// ✅ APPROVE: Extract to custom hook
function useProducts() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        const processed = processProducts(data);
        setProducts(processed);
      });
  }, []);

  return products;
}

// Business logic in pure function (testable!)
function processProducts(products: Product[]): ProcessedProduct[] {
  return products
    .filter(p => p.stock > 0)
    .map(p => ({
      ...p,
      discountedPrice: calculateDiscount(p),
      shipping: calculateShipping(p),
      taxes: calculateTaxes(p),
    }))
    .sort((a, b) => b.popularity - a.popularity);
}

function ProductList() {
  const products = useProducts();
  return <div>{/* render */}</div>;
}
```

**Review comment：** 建議把資料與業務邏輯抽到 hook/純函數，方便測試與重用。
