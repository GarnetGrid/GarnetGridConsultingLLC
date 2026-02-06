# X++ Select Patterns & Query Optimization

## Core Philosophy
In D365FO, every database round-trip is expensive. The "Senior Developer" approach prioritizes **set-based operations** first, **optimized formatting** second, and **row-by-row** logic only as a last resort.

---

## 1. The `while select` statement

### Best Practices
- **Always specify field lists**: Never use `select *` (i.e., just `select custTable`). It fetches all fields, bloating SQL traffic.
- **Use `firstOnly`** when you only need existence checks or a single record.
- **Use `optimisticLock`** for high-throughput tables to prevent blocking.

### Anti-Pattern vs. Senior Pattern

❌ **Junior Approach (N+1 Problem):**
```xpp
while select custTable
{
    // Round-trip for every customer!
    select firstOnly custGroup where custGroup.CustGroup == custTable.CustGroup;
    this.process(custGroup);
}
```

✅ **Senior Approach (Joins & Set-Based):**
```xpp
while select custTable
    join custGroup
    where custTable.CustGroup == custGroup.CustGroup
{
    // Fetched in a single efficient query
    this.process(custGroup);
}
```

---

## 2. Advanced Keywords

### `forceSelectOrder`
Forces the SQL query optimizer to use the order of fields in the index. Use sparingly and only when SQL analysis proves the optimizer is picking a bad plan.
```xpp
select forceSelectOrder tableId index MyIndex;
```

### `optimisticLock` vs `pessimisticLock`
- **Optimistic (Default in most cases)**: Checks version update at commit time.
- **Pessimistic (`forupdate`)**: Locks the record immediately. Use for mission-critical serial transactions (e.g., number sequence generation).

### `crossCompany`
Allows querying across DataAreaIds.
```xpp
// Efficiently find a customer across all legal entities
CustTable custTable;
container conCompanies = ['USMF', 'DAT']; 

// Specific companies
while select crossCompany : conCompanies custTable 
    where custTable.AccountNum == '1001'
{
    // ...
}
```

---

## 3. High-Performance Read Techniques

### `Query::insert_recordset` (Ad-hoc)
When you need to copy data from one table to another without looping.

```xpp
insert_recordset myStagingTable (TargetField1, TargetField2)
    select SourceField1, SourceField2 from mySourceTable
    where mySourceTable.Status == Status::Open;
```

### `update_recordset`
Bulk updates. 100x faster than while select for update.

```xpp
update_recordset myTable
    setting Status = Status::Closed
    where myTable.CreatedDate < systemDateGet() - 30;
```

---

## 4. Troubleshooting Performance

1.  **Trace Parser**: The ultimate truth. Look for "Inclusive Duration" on SQL tab.
2.  **SQL Insights**: Use LCS SQL Insights to find missing indexes.
3.  **Blocking**: If `forupdate` is held too long (e.g., user interaction inside a transaction), it causes table locks. **NEVER** put user dialogs inside `ttsBegin/ttsCommit`.

