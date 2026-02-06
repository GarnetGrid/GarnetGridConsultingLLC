# DAX Measure Design Patterns

## Pattern: DIVIDE with safe blank handling
```dax
[Margin %] =
DIVIDE([Profit], [Sales])
```

## Pattern: Avoid recomputed totals in Matrix (ISINSCOPE)
```dax
[Sales (Matrix Safe)] =
IF(
    ISINSCOPE('DimProduct'[ProductName]),
    [Sales],
    SUMX(VALUES('DimProduct'[ProductName]), [Sales])
)
```

## Pattern: CALCULATE filters (keep them simple)
```dax
[Sales Online] =
CALCULATE(
    [Sales],
    'DimChannel'[Channel] = "Online"
)
```

## Pattern: “As of” logic with variables
```dax
[Sales As Of] =
VAR Cutoff = MAX('DateTable'[Date])
RETURN
CALCULATE(
    [Sales],
    FILTER(ALL('DateTable'[Date]), 'DateTable'[Date] <= Cutoff)
)
```

## Common mistakes
- Overusing iterators (SUMX/FILTER) when a simple SUM would do.
- Using SELECTEDVALUE without a default → returns BLANK unexpectedly.
- Complex FILTER over big fact tables: try filtering dimensions instead.
