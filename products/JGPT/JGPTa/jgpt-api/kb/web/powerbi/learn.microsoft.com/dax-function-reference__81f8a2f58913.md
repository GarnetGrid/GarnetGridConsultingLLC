# DAX function reference

**Source:** https://learn.microsoft.com/en-us/dax/dax-function-reference
**Captured:** 2026-02-02
**Domain:** powerbi

The DAX function reference provides detailed information including syntax, parameters, return values, and examples for each of the over 250 functions used in Data Analysis Expression (DAX) formulas.

Important

Not all DAX functions are supported or included in earlier versions of Power BI Desktop, Analysis Services, and Power Pivot in Excel.

## In this section

[New DAX functions](new-dax-functions) - These functions are new or are existing functions that have been significantly updated.

[Aggregation functions](aggregation-functions-dax) - These functions calculate a (scalar) value such as count, sum, average, minimum, or maximum for all rows in a column or table as defined by the expression.

[Date and time functions](date-and-time-functions-dax) - These functions in DAX are similar to date and time functions in Microsoft Excel. However, DAX functions are based on the datetime data types used by Microsoft SQL Server.

[Filter functions](filter-functions-dax) - These functions help you return specific data types, look up values in related tables, and filter by related values. Lookup functions work by using tables and relationships between them. Filtering functions let you manipulate data context to create dynamic calculations.

[Financial functions](financial-functions-dax) - These functions are used in formulas that perform financial calculations, such as net present value and rate of return.

[INFO functions](info-functions-dax) - These functions return metadata about your semantic model, such as the tables, columns, relationships, and calculation DAX formulas. They can help you understand and document the model. They are based on the library of [Dynamic Management Views (DMVs) in Analysis Services](/en-us/analysis-services/instances/use-dynamic-management-views-dmvs-to-monitor-analysis-services), which have been modified to work as DAX functions.

[Information functions](information-functions-dax) - These functions look at a table or column provided as an argument to another function and returns whether the value matches the expected type. For example, the ISERROR function returns `TRUE` if the value you reference contains an error.

[Logical functions](logical-functions-dax) - These functions return information about values in an expression. For example, the `TRUE` function lets you know whether an expression that you are evaluating returns a `TRUE` value.

[Math and Trig functions](math-and-trig-functions-dax) - Mathematical functions in DAX are similar to Excel's mathematical and trigonometric functions. However, there are some differences in the numeric data types used by DAX functions.

[Other functions](other-functions-dax) - These functions perform unique actions that cannot be defined by any of the categories most other functions belong to.

[Parent and Child functions](parent-and-child-functions-dax) - These functions help users manage data that is presented as a parent/child hierarchy in their data models.

[Relationship functions](relationship-functions-dax) - These functions are for managing and utilizing relationships between tables. For example, you can specify a particular relationship to be used in a calculation.

[Statistical functions](statistical-functions-dax) - These functions calculate values related to statistical distributions and probability, such as standard deviation and number of permutations.

[Table manipulation functions](table-manipulation-functions-dax) - These functions return a table or manipulate existing tables.

[Text functions](text-functions-dax) - With these functions, you can return part of a string, search for text within a string, or concatenate string values. Additional functions are for controlling the formats for dates, times, and numbers.

[Time intelligence functions](time-intelligence-functions-dax) - These functions help you create calculations that use built-in knowledge about calendars and dates. By using time and date ranges in combination with aggregations or calculations, you can build meaningful comparisons across comparable time periods for sales, inventory, and so on.

## Related content
