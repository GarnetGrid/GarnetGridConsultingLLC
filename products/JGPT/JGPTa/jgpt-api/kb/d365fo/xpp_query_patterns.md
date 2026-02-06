# X++ Query Patterns

## Pattern: Select with join
```xpp
CustTable cust;
DirPartyTable party;

select firstOnly cust
    join party
        where party.RecId == cust.Party
        && cust.AccountNum == _accountNum;
```

## Pattern: while select (iterate)
```xpp
SalesTable st;
while select st
    where st.SalesStatus == SalesStatus::Backorder
{
    // work
}
```

## Pattern: QueryBuildDataSource for dynamic filters
```xpp
Query q = new Query();
QueryBuildDataSource qbds = q.addDataSource(tableNum(SalesTable));
qbds.addRange(fieldNum(SalesTable, SalesStatus)).value(queryValue(SalesStatus::Backorder));
QueryRun qr = new QueryRun(q);
while (qr.next())
{
    SalesTable st = qr.get(tableNum(SalesTable));
}
```

## Common mistakes
- Using `firstOnly` unintentionally and missing rows
- Not using `queryValue()` for ranges
