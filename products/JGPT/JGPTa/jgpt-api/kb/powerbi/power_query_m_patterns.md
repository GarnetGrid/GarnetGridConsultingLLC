# Power Query (M) Patterns

## Incremental Refresh (folding-friendly)
Prereqs:
- Parameters: RangeStart / RangeEnd (DateTime)
- Filter uses those parameters on a Date/DateTime column

```powerquery
let
    Source = Sql.Database(ServerName, DatabaseName),
    Sales = Source{[Schema="dbo",Item="FactSales"]}[Data],
    Filtered =
        Table.SelectRows(
            Sales,
            each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd
        )
in
    Filtered
```

## Query folding checklist
- Apply filters early
- Avoid non-foldable custom columns before filters
- Prefer Table.SelectRows for simple filters
