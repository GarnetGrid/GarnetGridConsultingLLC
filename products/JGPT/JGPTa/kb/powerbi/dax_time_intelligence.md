# DAX Time Intelligence Patterns

## Base measures first (recommended)
```dax
[Sales] = SUM('FactSales'[SalesAmount])
```

## YTD / QTD / MTD
```dax
[Sales YTD] = TOTALYTD([Sales], 'DateTable'[Date])
[Sales QTD] = TOTALQTD([Sales], 'DateTable'[Date])
[Sales MTD] = TOTALMTD([Sales], 'DateTable'[Date])
```

## Same period last year
```dax
[Sales SPLY] =
CALCULATE(
    [Sales],
    SAMEPERIODLASTYEAR('DateTable'[Date])
)
```

## Prior month
```dax
[Sales Prior Month] =
CALCULATE(
    [Sales],
    DATEADD('DateTable'[Date], -1, MONTH)
)
```

## Trailing 12 months (TTM)
```dax
[Sales TTM] =
VAR EndDate = MAX('DateTable'[Date])
RETURN
CALCULATE(
    [Sales],
    DATESINPERIOD('DateTable'[Date], EndDate, -12, MONTH)
)
```

## Rolling N days (example 30)
```dax
[Sales Rolling 30D] =
VAR EndDate = MAX('DateTable'[Date])
RETURN
CALCULATE(
    [Sales],
    DATESINPERIOD('DateTable'[Date], EndDate, -30, DAY)
)
```

## Common mistakes
- Using fact table dates in time intelligence functions (prefer DateTable[Date]).
- Missing a continuous Date table (gaps can break time functions).
