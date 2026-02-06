# Variables in DAX - SQLBI

**Source:** https://www.sqlbi.com/articles/variables-in-dax/
**Captured:** 2026-02-03
**Domain:** powerbi

Variables were introduced in DAX in 2015 and so far, they have proven to be the best enhancement of the DAX language ever. When presented with the concept of variables, most newbies focus on performance improvement, thinking that you introduce variables in your code mainly to obtain better performance. Although variables can improve performance, performance is a minor advantage. There are several more important considerations that should encourage any DAX developer to make extensive use of variables. In this article we share a few considerations, along with best practices about variables and DAX.

Let us start with the syntax. You can define a variable in any DAX expression by using VAR followed by RETURN. In one or several VAR sections, you individually declare the variables needed to compute the expression; in the RETURN part you provide the expression itself.

This simple formula includes the definition of two variables:

```
VAR SalesAmount =
    SUMX ( Sales, Sales[Quantity] * Sales[Net Price] )
VAR NumCustomer =
    DISTINCTCOUNT ( Sales[CustomerKey] )
RETURN
    DIVIDE ( SalesAmount, NumCustomer )
```

The *SalesAmount* variable contains the dollar amount of sales computed through [SUMX](https://dax.guide/sumx/?aff=sqlbi), whereas the *NumCustomer* variable contains the number of customers, as the [DISTINCTCOUNT](https://dax.guide/distinctcount/?aff=sqlbi) of *Sales[CustomerKey]*.

The two variables are used in the RETURN part, where we divide one by the other. The result of the entire expression is the RETURN part.

You can think about a variable as a name for an expression. The term “variable” itself is somewhat misleading – a DAX variable cannot change its value, as the name would suggest. **A DAX variable is indeed a constant**, meaning that it is a name for the value computed by the definition of the variable.

Each set of VAR / RETURN can include multiple variables, you can have any number of VAR for one RETURN. Moreover, the definition of a variable can reference other variables provided that the other variables have been defined beforehand – either within the same block or in an outer block. As this last statement suggests, VAR statements can be nested. For example, the previous expression can be written by using more variables in the following, quite verbose way:

Measure in Sales table

```
SalesPerCustomer :=
VAR SalesAmount =
    SUMX (
        Sales,
        VAR Quantity = Sales[Quantity]
        VAR Price = Sales[Net Price]
        RETURN
            Quantity * Price
    )
VAR NumCustomer =
    DISTINCTCOUNT ( Sales[CustomerKey] )
RETURN
    DIVIDE (
        SalesAmount,
         NumCustomer
    )
```

The *Quantity* and *Price* variables are not really useful in this example. Yet they help show that you can define variables anywhere in a DAX formula. The VAR / RETURN set replaces an expression, so it can be used wherever an expression is allowed. This is not a very common technique. Mostly, you will see a DAX formula containing an initial set of variable declarations, followed by a single RETURN statement. Regardless, there are cases where for rather complex code the generous use of VAR / RETURN comes handy.

Variables are useful for several reasons:

* **Readability of the code.** By assigning a name to an expression you are effectively adding descriptive information to your code, making it easier to read it.
* **Split of the execution into logical steps.** Our brain processes expressions containing variables better, because variables provide execution steps. In the previous code, you might think that *SalesAmount* is computed first, then *NumCustomer,* and finally the result. Despite this not being true, variables still help read and understand the code.
* **Easier debugging of the code.** You can inspect the value of variables using professional debuggers, like the Tabular Editor 3 debugger, or you can return the value of a variable in a complex measure to inspect the intermediate evaluations.
* **Better performance.** Using variables, you instruct the DAX optimizer on which parts of the entire expression can be computed once and saved for later use. The value of a variable is computed only once, whereas repeating the same sub-expression in multiple places does not guarantee a unique execution of that piece of code.

Though newbies do not use a lot of variables, seasoned DAX developers get used to starting most measures with VAR! The reason is that any non-trivial measure requires different steps and by splitting the entire calculation into steps, they can better focus on simpler problems. In terms of mindset, it really makes a difference to start thinking about a complex calculation with this sentence: “First, I need a variable with this value, then I will focus on the next steps”.

We could provide tons of examples of code that is more readable with variables than without variables. Nonetheless, those would be just ad-hoc examples. We think that the best way to appreciate how much we at SQLBI value the relevance of variables, is to browse our articles. We use variables everywhere, for very good reasons.

One important detail about variables, though not clear at first sight, is that variables can contain tables too. While it is intuitive to consider a variable for a scalar value, it is less intuitive to also consider variables when wanting to store tables.

Look for example at the following piece of DAX code:

Measure in Sales table

```
Best Product Sales  := 
VAR BestProducts = TOPN ( 10, Product, [Sales Amount] )
VAR SalesOfBestProducts = 
    SUMX ( 
        BestProducts,
        SUMX ( 
            RELATEDTABLE ( Sales ), 
            Sales[Quantity] * Product[Unit Price] 
        )
    )
RETURN
    SalesOfBestProducts
```

There are several important considerations to be made about this small piece of code.

The first is that you read it as two separate steps: you would think DAX first computes the *BestProducts* variable, and then performs an iteration over its content while computing the second variable, *SalesOfBestProducts*. As we said, this is not true; DAX uses a different execution pattern. Nonetheless, it helps understand the flow.

The *BestProducts* variable contains the result of [TOPN](https://dax.guide/topn/?aff=sqlbi), which is a table. *BestProducts* contains the top 10 products ordered by *Sales Amount*. *BestProducts* is a table variable.

During the evaluation of the *SalesOfBestProducts* variable, the measure iterates over *BestProducts*. Then, for each row of *BestProducts* the measure scans the related sales, during the [SUMX](https://dax.guide/sumx/?aff=sqlbi) over [RELATEDTABLE](https://dax.guide/relatedtable/?aff=sqlbi). [RELATEDTABLE](https://dax.guide/relatedtable/?aff=sqlbi) requires relationships to be in place in order to work. As a matter of fact, a variable containing a table inherits the relationships of the base tables of the columns it contains. Because *BestProducts* contains rows from *Product*, it inherits the relationship between *Product* and *Sales*. Hence, [RELATEDTABLE](https://dax.guide/relatedtable/?aff=sqlbi) works just fine.

The second, non-trivial consideration is that the innermost [SUMX](https://dax.guide/sumx/?aff=sqlbi) computes *Sales[Quantity]* times *Product[Unit Price]*. *Sales* is in the row context, introduced by the innermost [SUMX](https://dax.guide/sumx/?aff=sqlbi). *Product* seems to not be in the row context – the outermost [SUMX](https://dax.guide/sumx/?aff=sqlbi) is iterating *BestProducts*. It would seem intuitive to refer to the *Unit Price* column in *BestProducts* as *BestProducts[Unit Price]*. Unfortunately, this syntax is not available. In order to reference a column inside a variable, you need to reference the column name with the base table prefix. Hence, instead of using *BestProducts[Unit Price]*, you need to use *Product[Unit Price]*.

In the very special case where a column belongs to a variable but is created inside the measure, say by using [ADDCOLUMNS](https://dax.guide/addcolumns/?aff=sqlbi), then you cannot specify a table name. This is the only case where our very strict rules about readability allow the developer to reference a column without the table name prefixed, rather than using the formally corrected but less readable syntax *”[column]* using an empty table name as a prefix.

The last important details about variables is that they represent a certain value when they are defined, and they are never computed again after. In our courses we assist with countless questions from DAX developers that do not understand why replacing an expression with a variable changes the result. Consider for example the following measure:

Measure in Sales table

```
Pct := 
DIVIDE ( 
    SUMX ( Sales, Sales[Quantity] * Sales[Net Price] ),
    CALCULATE ( 
        SUMX ( Sales, Sales[Quantity] * Sales[Net Price] ),
        ALL ( Product )
    )
)
```

The [SUMX](https://dax.guide/sumx/?aff=sqlbi) expression appears twice, identical. It looks like a good candidate for a variable. Unfortunately, it is not. If you change the code by introducing a variable, the measure computes an incorrect result:

Measure in Sales table

```
Pct (Wrong) :=
VAR SalesAmount =
    SUMX (
        Sales,
        Sales[Quantity] * Sales[Net Price]
    )
RETURN
    DIVIDE (
        SalesAmount,
        CALCULATE (
            SalesAmount,
            ALL ( Product )
        )
    )
```

*PCT (Wrong)* returns a constant value of 1. The reason is that the *SalesAmount* variable is computed once and never again. It does not matter that the second reference to *SalesAmount* is inside a [CALCULATE](https://dax.guide/calculate/?aff=sqlbi) that removes the filter from *Product*. Its value has already been computed and it does not change depending on the filter context. You can replace subexpressions with variables, but only if you checked that the subexpressions are computed in the same filter context.

During our courses, when it is time to talk about variables, we provide a simple rule: whenever you are in doubt about whether to define a variable or not, define the variable. The answer to the question: “is it better to write the code or use a variable here?” should always be to create a variable.

There are some very specific scenarios where a variable can actually negatively impact performance, because it sometimes forces an [eager evaluation](https://www.sqlbi.com/articles/understanding-eager-vs-strict-evaluation-in-dax/) of conditional statements. These are rare, so our suggestion to new DAX developers remains to use as many variables as you can. Over time, your future self will thank you because you used so many variables and made the code so much easier to read.

## Articles in the DAX 101 series
