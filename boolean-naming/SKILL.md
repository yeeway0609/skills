---
name: boolean-naming
description: "Naming booleans — variables, fields, props, predicate functions, boolean parameters. Use when naming or reviewing a boolean, designing a signature that takes a boolean argument, or meeting a vague name like `flag`, `done`, `status`, `active`."
---

# A boolean's name is a yes/no question

Read the name aloud: it must form a grammatical yes/no question. `isActive`, `hasPermission`, `shouldRetry` do; `active`, `permission`, `retry` don't. Everything below applies this one rule to variables, fields, props, parameters, and functions that return booleans.

## Prefix

The prefix is the first word, and it must agree with the word after it:

| Prefix | Asks about | Followed by | Example |
|--------|-----------|-------------|---------|
| `is` | state | adjective / participle | `isActive`, `isUserAuthenticated` |
| `has` | possession | noun | `hasAccess`, `hasValidSubscription` |
| `can` | capability / permission | bare verb | `canEdit` |
| `should` | recommended action | bare verb | `shouldRetry` |
| `was` / `did` | past event | past participle / bare verb | `wasProcessed`, `didSucceed` |

An ungrammatical question means the wrong prefix: `isAccess` → `hasAccess`, `hasActive` → `isActive`, `shouldValid` → `shouldValidate`. A buried prefix moves to the front: `userIsActive` → `isUserActive`.

Predicate functions follow the same table — the name is the question: `isValid()`, `hasAccess(user, resource)`, Go `IsEven(n)`. Verb names (`validate()`, `checkEven()`, `getStatus()`) read as actions and get renamed.

## Positive names

Name the positive state and negate at the use site: `isEnabled` with `if (!isEnabled)`, `isValid` with `if (!isValid)`. Names built on `isNot`, `hasNo`, `isDisabled`, `isInvalid` flip to their positive form.

**Boundary exception.** A negative name owned by an external contract — HTML `novalidate` / `disabled` / `readonly`, CLI `--no-color`, a payload's `is_not_eligible` — is converted once, at the boundary, and only the positive form travels inward:

```typescript
const shouldValidate = !noValidate;          // reading in
<form noValidate={!shouldValidate} />        // writing out
```

## One boolean, one question

A boolean answers one question for its whole lifetime.

- **Multi-purpose** — a boolean you explain with "and also" is several booleans. Name each, then compose: `const isReady = isConfigLoaded && isSocketConnected && isUserResolved;`
- **Drifting** — a variable reassigned to a new meaning mid-function (`found` → "subscribed" → "invoice sent") gets a new name at each change: `isUserFound`, `hasActiveSubscription`, `wasInvoiceSent`.

## Boolean trap

Judge a boolean parameter at the call site, with the definition out of view: `render(true)` is opaque. Fix in this order, taking the first that fits:

1. **Split the function** when the flag selects a behavior: `sortAscending()` / `sortDescending()`.
2. **Enum or union** when the flag names a mode that may grow: `render("dark")`.
3. **Options object** for several orthogonal flags: `createUser(name, email, { isAdmin: false, shouldSendWelcomeEmail: true })`.
4. **Keep the boolean** only when none fit: prefixed, and passed by keyword (Python `*` keyword-only, C# named arguments, Swift labels).

## Vague names

Replace with the specific condition being asked about:

- `flag`, `status`, `state`, `toggle`, `check` → `isDebugMode`, `isPending`, `isExpanded`, `hasErrors`
- `done` → `isUploadComplete`, `wasProcessed`
- `error`, `admin` (usually an object or ID) → `hasError`, `isAdmin` / `hasAdminRole`
- bare adjectives or participles (`active`, `loading`, `loggedIn`) → add the prefix
- `b`, `f`, `ok` → spell out the question

## Reviewing

Apply every section above to every boolean in scope — variables, fields, props, parameters, return values — and keep one name per concept across the codebase (`isActive` everywhere, never `active` in another file). Done when each boolean in scope has been checked against each section.
