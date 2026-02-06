# X++ Transactions (ttsBegin / ttsCommit)

## How tts works
- `ttsBegin` increments `ttsLevel`
- `ttsCommit` decrements `ttsLevel`
- The database commit happens when `ttsLevel` returns to 0
- Exceptions usually trigger rollback of the open transaction scope

## Pattern: Transaction wrapper
```xpp
ttsBegin;
try
{
    // do work
    ttsCommit;
}
catch (Exception::Error)
{
    ttsAbort;
    throw;
}
```

## Pattern: Nested tts (what actually happens)
```xpp
ttsBegin; // level 1
    ttsBegin; // level 2
    // ...
    ttsCommit; // back to level 1
ttsCommit; // commit at level 0
```

## Common mistakes
- Catching exceptions and not rethrowing (silently swallowing failures)
- Calling ttsCommit without a matching ttsBegin
