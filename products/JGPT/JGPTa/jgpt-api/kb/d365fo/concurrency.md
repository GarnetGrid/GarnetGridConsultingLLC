# X++ Concurrency & Transactions

D365FO uses **Optimistic Concurrency Control (OCC)**. This means records are not locked when read. They are only checked for modification when an update is attempted.

## Transaction Keywords

- `ttsbegin`: Starts a transaction.
- `ttscommit`: Commits the transaction.
- `ttsabort`: Aborts (rolls back) the transaction.

**Rule**: Every `ttsbegin` must have a matching `ttscommit`.

## Access Levels
- `forupdate`: Selects a record for update. This does NOT lock the record immediately in SQL, but it signals intent.
- `optimisticlock` (default): The system checks the `RecVersion` field on update. If it changed since select, an `UpdateConflict` exception is thrown.
- `pessimisticlock`: Forces a DB lock (e.g., `UPDLOCK`) immediately upon select. Use sparingly.

## Handling Update Conflicts
Because of OCC, you must handle `UpdateConflict` and `Deadlock` exceptions, typically with a retry loop.

```xpp
// Standard Retry Pattern
int retryCount = 0;

try
{
    ttsbegin;
    
    select forupdate myTable where myTable.Id == '123';
    myTable.Status = 'Processed';
    myTable.update();
    
    ttscommit;
}
catch (Exception::UpdateConflict)
{
    if (retryCount < 3)
    {
        retryCount++;
        retry;
    }
    else
    {
        throw Exception::UpdateConflict;
    }
}
catch (Exception::Deadlock)
{
    retry; // Infinite retry for deadlocks is sometimes acceptable, or limit it.
}
```

## Post-Transaction Logic
If you need to perform an action *only* after the transaction successfully commits (e.g., sending an API call), use the `Application::setAfterCommit` delegate or the `TransactionCompleted` event. **Never** make external API calls inside a `ttsbegin`/`ttscommit` block, as it holds the DB transaction open longer than necessary and cannot be rolled back if the commit fails.
