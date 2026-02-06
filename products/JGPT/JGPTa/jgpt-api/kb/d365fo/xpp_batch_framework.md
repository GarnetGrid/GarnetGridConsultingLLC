# X++ Batch Framework & Async Processing

## 1. SysOperationFramework vs RunBaseBatch
- **SysOperationFramework (MVC)**: The modern standard. Separates UI (Controller), Contract (Data), and Logic (Service). Mandatory for highly scalable processes.
- **RunBaseBatch**: Legacy. Harder to serialize, harder to extend. Avoid for new code.

---

## 2. Reliable Batch Patterns

### Top-Picking Pattern (Concurrent Processing)
To run multiple batch tasks in parallel on the same table (scaling out):
1. Use `optimisticLock`.
2. Select `firstOnly` with `forUpdate`.
3. Check `RecVersion` equality at commit.

```xpp
// Service Class Method
public void processNextItem()
{
    MyStagingTable staging;
    
    ttsbegin;
    // Find next unprocessed record - locking immediately to prevent race conditions
    select firstOnly pessimisticLock staging
        where staging.Status == Status::Ready;
    
    if (staging)
    {
        staging.Status = Status::Processing;
        staging.update();
        ttscommit; // Release lock quickly
        
        // Do heavy lifting outside the lock
        this.doHeavyWork(staging);
    }
    else
    {
        ttscommit;
    }
}
```

### Batch Bundling (Performance)
Instead of creating 100,000 tasks (overhead!), bundle them.
- **Good**: 1 task processes 1000 items (Bundle Size).
- **Bad**: 1 task processes 1 item.

---

## 3. Retry Logic
Transient SQL errors (deadlocks) happen. Your batch job must handle them.

```xpp
try
{
    ttsbegin;
    // ... logic
    ttscommit;
}
catch (Exception::Deadlock)
{
    retry; // Infinite retry for deadlocks is standard X++ behavior, but dangerous.
           // Better: Use a counter to limit retries.
}
catch (Exception::UpdateConflict)
{
    if (xSession::currentRetryCount() < 5)
    {
        retry;
    }
    else
    {
        throw Exception::UpdateConflict;
    }
}
```

---

## 4. RunAsync
For real-time UI threading (e.g., "Export to Excel" without freezing the browser):
```xpp
Global::runAsync(
    classNum(MyService),
    staticMethodStr(MyService, longRunningMethod),
    [param1, param2],
    System.Threading.CancellationToken::None,
    classNum(MyCompleterClass),
    staticMethodStr(MyCompleterClass, callback)
);
```
**Warning**: `runAsync` is stateless. The user might close the browser. Do not rely on it for critical business updates (use Batch for that).
