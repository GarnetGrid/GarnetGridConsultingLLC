# Time Intelligence: Beyond the Basics

## 1. The Standard Pattern (Built-in)
Use these ONLY if you have a standard Gregorian calendar (Jan 1 - Dec 31).
Requires:
- A dedicated `Date` table.
- "Mark as Date Table" enabled.

```dax
Sales YTD = TOTALYTD( [Sales Amount], 'Date'[Date] )
Sales YoY % = 
VAR CurrentSales = [Sales Amount]
VAR LastYearSales = CALCULATE( [Sales Amount], SAMEPERIODLASTYEAR( 'Date'[Date] ) )
RETURN
    DIVIDE( CurrentSales - LastYearSales, LastYearSales )
```

---

## 2. The Custom Calendar (4-4-5 / Fiscal)
Standard functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`) **FAIL** on custom fiscal calendars (e.g., Retail 4-4-5).
You MUST use "Filter Safe" patterns based on your Date table columns (`FiscalYear`, `FiscalWeek`).

### Custom YTD Pattern
```dax
Sales Fiscal YTD = 
VAR MaxDate = MAX( 'Date'[Date] )
VAR MaxYear = MAX( 'Date'[Fiscal Year] )
RETURN
    CALCULATE(
        [Sales Amount],
        'Date'[Fiscal Year] = MaxYear,
        'Date'[Date] <= MaxDate
    )
```

### Custom Previous Year Pattern
Do NOT use `DATEADD`. Match on Week Number.
```dax
Sales Fiscal PY = 
VAR CurrentYear = MAX( 'Date'[Fiscal Year] )
VAR CurrentWeek = MAX( 'Date'[Fiscal Week Number] )
RETURN
    CALCULATE(
        [Sales Amount],
        'Date'[Fiscal Year] = CurrentYear - 1,
        'Date'[Fiscal Week Number] = CurrentWeek,
         // Handle Max Date inside the week if necessary
        ALLEXCEPT( 'Date', 'Date'[DayOfWeek] ) 
    )
```

---

## 3. Semi-Additive Measures (Inventory)
Inventory balances are not summed over time. You take the LAST value.

```dax
Inventory Balance = 
VAR LastVisibleDate = MAX( 'Date'[Date] )
RETURN
    CALCULATE(
        SUM( 'Inventory'[Quantity] ),
        LASTDATE( 'Date'[Date] )
    )
```
**Better (faster)**:
```dax
Inventory Balance = 
VAR LastVisibleDate = MAX( 'Date'[Date] )
RETURN
    CALCULATE(
        SUM( 'Inventory'[Quantity] ),
        'Date'[Date] = LastVisibleDate
    )
```

---

## 4. Date Table Requirements
Your Date table MUST have:
1. `Date` (Type: Date, unique)
2. `Year` (Int)
3. `MonthNo` (Int)
4. `MonthYear` (String, Sort By MonthNo)
5. `FiscalYear` (Int)
6. `FiscalPeriod` (Int)
7. `IsWorkingDay` (Boolean) - Crucial for "Sales per Working Day" analysis.
