# Week-Based Time Intelligence in DAX

**Source:** https://www.sqlbi.com/articles/week-based-time-intelligence-in-dax/
**Captured:** 2026-02-02
**Domain:** powerbi

**UPDATE 2020-09-10**: **We published a new [DAX Pattern for week-based calculations](https://www.daxpatterns.com/week-related-calculations/) with new and more optimized DAX code.** Examples are available for both Power BI and Excel. While this article is still valid for the general concepts, we suggest you read the use the formulas in the [new pattern](https://www.daxpatterns.com/week-related-calculations/).

The [Time Intelligence functions in DAX](https://dax.guide/) (such as [TOTALYTD](https://dax.guide/totalytd/?aff=sqlbi), [SAMEPERIODLASTYEAR](https://dax.guide/sameperiodlastyear/?aff=sqlbi) and many others) assume that every day in a month belongs to the same quarter regardless of the year. This assumption is not valid in a week-based calendar: each quarter and each year might contain days that are not “naturally” related. For example, January 1st and January 2nd, 2011 belong to week 52 of year 2010, and the first week of 2011 starts on January 3rd. This approach is common in retail and manufacturing, which rely on 4-4-5, 5-4-4, and 4-5-4 calendars. By using 4-4-5 weeks in a quarter, you can easily compare uniform numbers between quarters — mainly because you have the same number of working days and weekends in each quarter. You can find further information about these calendars on Wikipedia ([4-4-5 calendar](http://en.wikipedia.org/wiki/4%E2%80%934%E2%80%935_calendar) and [ISO week date](http://en.wikipedia.org/wiki/ISO_week_date)).

The goal of this article is not to explain how to write a Calendar table. There are too many variations and custom rules for each business, but the DAX pattern to use is always the same and this is the topic discussed here. You can build your custom Calendar table in Excel, PowerPivot or SSAS Tabular, and it works automatically for simple aggregation. However, if you try to calculate YTD or YOY using Time Intelligence DAX functions, you get invalid results because the assumption made by these functions is no longer valid. Colin Banfield wrote a useful [Excel workbook to generate Calendar tables](https://www.sqlbi.com/broken/?url=http://www.powerpivotpro.com/2012/05/excel-5-calendar-date-table/). Darren Gosbell offers an interesting [Power Query script](https://www.sqlbi.com/broken/?url=http://geekswithblogs.net/darrengosbell/archive/2014/03/23/extending-the-powerquery-date-table-generator-to-include-iso-weeks.aspx) to generate a Calendar table.

DAX is a powerful language built on a very small number of basic functions. All existing Time Intelligence functions can be rebuilt in DAX using mainly the [CALCULATE](https://dax.guide/calculate/?aff=sqlbi), [FILTER](https://dax.guide/filter/?aff=sqlbi), and [VALUES](https://dax.guide/values/?aff=sqlbi) functions. With this in mind, you can build a calculation working on any custom Calendar table. Among the examples available for download at the end of this article is a sample ISO Calendar table. However, the DAX code can easily be adapted to any other custom Calendar table.

Let’s start with an easy translation of a Time Intelligence function into the corresponding DAX calculation. You can compute YTD using the [TOTALYTD](https://dax.guide/totalytd/?aff=sqlbi) function:

```
Cal YTD :=
TOTALYTD (
    SUM ( Sales[Sales Amount] ),
    Dates[Date]
)
```

In reality, this corresponds to the following [CALCULATE](https://dax.guide/calculate/?aff=sqlbi) statement:

```
Cal YTD:=
CALCULATE (
    SUM( Sales[Sales Amount] ),
    DATESYTD ( Dates[Date] )
)
```

The [DATESYTD](https://dax.guide/datesytd/?aff=sqlbi) function returns a table containing a list of dates. If DAX did not have [DATESYTD](https://dax.guide/datesytd/?aff=sqlbi), you might obtain the same result by writing a [FILTER](https://dax.guide/filter/?aff=sqlbi) that returns all the days of the year before:

```
Cal YTD :=
IF (
    HASONEVALUE ( Dates[Calendar Year] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL ( Dates ),
            Dates[Calendar Year] = VALUES ( Dates[Calendar Year] )
                && Dates[Date] <= MAX ( Dates[Date] )
        )
    ),
    BLANK ()
)
```

By examining the function above, you can understand why the calculation does not work on a week-based calendar. January 1st is included into the year before, and the existing filter condition would fail this check. You cannot use the optional parameter of [DATESYTD](https://dax.guide/datesytd/?aff=sqlbi) specifying the last day of a year to fix that, because typically the last day of the year is different each year. In the following picture, you see that the result shown in column *Cal YTD* is wrong. The first week of ISO Year 2011 inaccurately contains the first two days of January 2011, which in reality belongs to the ISO Year 2010. Column *Iso YTD* is correct.

[![pivot-ytd](https://cdn.sqlbi.com/wp-content/uploads/pivot-ytd_thumb.png "pivot-ytd")](https://cdn.sqlbi.com/wp-content/uploads/pivot-ytd.png)

However, in order to obtain the desired result you can simply replace the test over column *Year* in the previous formula. The following is the definition of the *Iso YTD* measure, which you have seen used in the pivot table.

```
Iso YTD :=
IF (
    HASONEVALUE ( Dates[ISO Year] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL( Dates ),
            Dates[ISO Year] = VALUES ( Dates[ISO Year] )
                && Dates[Date] <= MAX ( Dates[Date] )
        )
    ),
    BLANK ()
)
```

You can use the same technique to write the quarter-to-date (QTD), month-to-date (MTD) and week-to-date (WTD) calculations.

```
Iso QTD :=
IF (
    HASONEVALUE ( Dates[ISO Year] )
        && HASONEVALUE (Dates[ISO Quarter] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL ( Dates ),
            Dates[ISO Year] = VALUES ( Dates[ISO Year] )
                && Dates[ISO Quarter] = VALUES ( Dates[ISO Quarter] )
                && Dates[Date] <= MAX ( Dates[Date] )
        )
    ),
    BLANK ()
)

Iso MTD :=
IF (
    HASONEVALUE ( Dates[ISO Year] )
        && HASONEVALUE (Dates[ISO Month Number] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL ( Dates ),
            Dates[ISO Year] = VALUES ( Dates[ISO Year] )
                && Dates[ISO Month Number] = VALUES ( Dates[ISO Month Number] )
                && Dates[Date] <= MAX ( Dates[Date] )
        )
    ),
    BLANK ()
)

Iso WTD :=
IF (
    HASONEVALUE ( Dates[ISO Year] )
        && HASONEVALUE (Dates[ISO Week Number] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL ( Dates ),
            Dates[ISO Year] = VALUES ( Dates[ISO Year] )
                && Dates[ISO Week Number] = VALUES ( Dates[ISO Week Number] )
                && Dates[Date] <= MAX ( Dates[Date] )
        )
    ),
    BLANK ()
)
```

Another common calculation is the year-over-year (YOY). In order to achieve that, you need to calculate the same period the year before. This is the Time Intelligence calculation available in DAX for regular calendars, based on the [SAMEPERIODLASTYEAR](https://dax.guide/sameperiodlastyear/?aff=sqlbi) function:

```
Cal PY :=
CALCULATE (
    SUM ( Sales[Sales Amount] ),
    SAMEPERIODLASTYEAR ( Dates[Date] )
)
```

Behind the scenes, [SAMEPERIODLASTYEAR](https://dax.guide/sameperiodlastyear/?aff=sqlbi) iterates all the dates that have the same day and month from the previous year. This assumption is not valid in a week-based calendar, because the last day of each year (and of each period) can be different between different years. In the following picture, you see that *Cal YOY* returns a wrong value for ISO Week 09 in 2012, whereas *Iso YOY* displays the correct value.

[![pivot-yoy](https://cdn.sqlbi.com/wp-content/uploads/pivot-yoy_thumb.png "pivot-yoy")](https://cdn.sqlbi.com/wp-content/uploads/pivot-yoy.png)

In order to write a simple DAX calculation for the Iso YOY measure, you need to create a column in the Calendar table that simplifies the required DAX code. This column contains the number of days elapsed so far in the current ISO year for each date. Something like that:

[![isocalendar](https://cdn.sqlbi.com/wp-content/uploads/isocalendar_thumb.png "isocalendar")](https://cdn.sqlbi.com/wp-content/uploads/isocalendar.png)

By using this column, writing the previous year calculation is simple. You just have to check that the ISO Year Day Number column is the same between different years. You might notice the same expression in two of the [CONTAINS](https://dax.guide/contains/?aff=sqlbi) function’s arguments: the second argument defines the column checked for each row of the table passed as the first argument, whereas the third argument is an expression resolved in a scalar value before the [CONTAINS](https://dax.guide/contains/?aff=sqlbi) function is called. Thus, the measure executes such expression in the row context defined by the outer [FILTER](https://dax.guide/filter/?aff=sqlbi) function. You might easily get confused by that syntax!

```
Iso PY :=
IF (
    HASONEVALUE ( Dates[ISO Year] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL ( Dates ),
            Dates[ISO Year Number] = VALUES ( Dates[ISO Year Number] ) - 1
                && CONTAINS(
                    VALUES ( Dates[ISO Year Day Number] ),
                    Dates[ISO Year Day Number],
                    Dates[ISO Year Day Number] )
        )
    ),
    BLANK ()
)
```

At this point, writing the year-over-year (YOY) calculation is simple:

```
Iso YOY := [Sales] - [Iso PY]

Iso YOY % := IF ( [Iso PY] <> 0, [Iso YOY] / [Iso PY], BLANK () )
```

Finally, if you want to calculate the previous-year-to-date value simply merge the two techniques presented in this article. Use the *ISO Year Day Number* column (instead of using the date) in order to identify the corresponding day from the previous year as the last of the days to consider in the calculation.

```
Iso PYTD :=
IF (
    HASONEVALUE ( Dates[ISO Year] ),
    CALCULATE (
        SUM ( Sales[Sales Amount] ),
        FILTER (
            ALL ( Dates ),
            Dates[ISO Year Number] = VALUES ( Dates[ISO Year Number] ) - 1
                && Dates[ISO Year Day Number] <= MAX ( Dates[ISO Year Day Number] )
        )
    ),
    BLANK ()
)
```

You can build many other calculations on a Calendar. In this article, you have seen the more important techniques needed to write Time Intelligence calculations over week-based calendars. You can also use the same techniques on any custom calendar, creating the columns (such as *ISO Year Day Number*) that can help you in writing a simple DAX formula.

The ZIP demo file you can download below includes two examples, one for Excel 2010 and the other for Excel 2013.
