# X++ Performance Optimization Guide

## Set-Bsed Operations
One of the most critical performance optimizations in X++ is the use of set-based operations (`insert_recordset`, `update_recordset`, `delete_from`) instead of row-by-row iteration.

### `insert_recordset`
Copies data from one or more tables directly into another table in a single database round-trip.

```xpp
// BAD: Loop and insert
while select SourceTable
{
    targetTable.clear();
    targetTable.Field1 = SourceTable.Field1;
    targetTable.insert();
}

// GOOD: insert_recordset
insert_recordset targetTable (Field1, Field2)
    select Field1, Field2 from SourceTable
    where SourceTable.Criteria == 'Value';
```

### `update_recordset`
Updates multiple records in a single statement.

```xpp
// GOOD: update_recordset
update_recordset salaryTable
    setting Pay = Pay * 1.05
    where salaryTable.Rating == 'Excellent';
```

## Caching Strategies

### SysGlobalObjectCache (SGOC)
Use `SysGlobalObjectCache` for data that is expensive to calculate, infrequently changed, and shared across user sessions. It is stored in the AOS memory.

```xpp
// Key structure: [Scope, Key, Value]
SysGlobalObjectCache sgoc = classFactory.globalObjectCache();
container key = [curExt(), 'MyKey'];
container value = sgoc.find('MyScope', key);

if (value == conNull())
{
    // ... expensive calculation ...
    value = ['CalculatedValue'];
    sgoc.insert('MyScope', key, value);
}
```

### Context Caching
For request-scoped caching (e.g., within a specific batch job or OData call), consider using a singleton or the `Context` object pattern to avoid recalculating values within the same execution context.

## Query Optimization
- **Covering Indices**: Ensure your queries select only fields that are part of an index to allow index-only scans.
- **TraceParser**: Always use Trace Parser to identify `Table Scans` and high-latency SQL statements.
- **Query Plan**: Use SQL Server Management Studio (SSMS) to analyze execution plans for generated SQL.
