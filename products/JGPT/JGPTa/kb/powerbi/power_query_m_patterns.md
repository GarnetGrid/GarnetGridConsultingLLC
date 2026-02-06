# Power Query (M) Patterns

## Pattern: Parameterized SQL query (folding-friendly)
```powerquery
let
    Source = Sql.Database(ServerName, DatabaseName),
    Sales = Source{[Schema="dbo",Item="FactSales"]}[Data],
    Filtered = Table.SelectRows(Sales, each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd)
in
    Filtered
```

## Query folding checklist
- Keep filtering steps early
- Avoid custom columns that call non-foldable functions before filters
- Prefer Table.SelectRows over complex transformations before filtering

## Incremental Refresh prerequisites
- Parameters: RangeStart / RangeEnd (DateTime)
- Filter must use those parameters on a Date/DateTime column
