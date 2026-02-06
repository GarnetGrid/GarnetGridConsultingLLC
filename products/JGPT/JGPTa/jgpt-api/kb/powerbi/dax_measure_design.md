# DAX Measure Design Patterns

## Pattern: DIVIDE (safe)
```dax
[Margin %] = DIVIDE([Profit], [Sales])
```

## Pattern: Correct totals in Matrix (ISINSCOPE)
```dax
[Sales (Matrix Safe)] =
IF(
    ISINSCOPE('DimProduct'[ProductName]),
    [Sales],
    SUMX(VALUES('DimProduct'[ProductName]), [Sales])
)
```

## Pattern: CALCULATE filter on dimension (preferred)
```dax
[Sales Online] =
CALCULATE(
    [Sales],
    'DimChannel'[Channel] = "Online"
)
```

## Pattern: “As of” (cutoff date)
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
- Overusing SUMX/FILTER on big fact tables when simple aggregation works.
- SELECTEDVALUE without default returning BLANK.
- Filtering facts when you can filter dimensions.
