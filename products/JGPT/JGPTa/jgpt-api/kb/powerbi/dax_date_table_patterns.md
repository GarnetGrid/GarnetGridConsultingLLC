# DAX Date Table Patterns

## Pattern: Date table from Fact min/max (preferred)
**Use when:** You have a fact table with a date column and want the date table range to match real data.

```dax
DateTable =
VAR _MinDate =
    MINX(
        ALL ( 'FactTable' ),
        'FactTable'[FactDateColumn]
    )
VAR _MaxDate =
    MAXX(
        ALL ( 'FactTable' ),
        'FactTable'[FactDateColumn]
    )
RETURN
ADDCOLUMNS(
    CALENDAR( _MinDate, _MaxDate ),
    "Year", YEAR([Date]),
    "QuarterNum", QUARTER([Date]),
    "Quarter", "Q" & QUARTER([Date]),
    "MonthNum", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "MonthYear", FORMAT([Date], "MMM YYYY"),
    "YearMonthKey", YEAR([Date]) * 100 + MONTH([Date]),
    "Day", DAY([Date]),
    "DayOfWeekNum", WEEKDAY([Date], 2),
    "DayOfWeek", FORMAT([Date], "ddd"),
    "IsWeekend", WEEKDAY([Date], 2) > 5,
    "ISOWeekNum", WEEKNUM([Date], 21)
)
```

**Common mistakes**
- Using `MIN('FactTable'[FactDateColumn])` directly (context-dependent). Prefer `MINX(ALL())` / `MAXX(ALL())`.
- Forgetting to **Mark as date table** (Model view → select DateTable → Mark as date table).
- Setting bi-directional relationships by default (usually keep single direction DateTable → Fact).

## Pattern: Date table with fixed range (fallback)
```dax
DateTable =
VAR StartDate = DATE(2018,1,1)
VAR EndDate   = TODAY() + 365
RETURN
ADDCOLUMNS(
    CALENDAR(StartDate, EndDate),
    "Year", YEAR([Date]),
    "MonthNum", MONTH([Date]),
    "MonthYear", FORMAT([Date], "MMM YYYY")
)
```

## Pattern: Fiscal year starting July
```dax
"FiscalYear", YEAR([Date]) + IF(MONTH([Date]) >= 7, 1, 0),
"FiscalMonthNum", MOD(MONTH([Date]) + 5, 12) + 1
```

## Relationship checklist
- DateTable[Date] → Fact[Date] (Many-to-one, single direction)
- All time intelligence should use DateTable[Date]
