# Modeling: Star Schema Rules

## Rule of thumb
- Facts: lots of rows, numeric measures, foreign keys
- Dimensions: descriptive attributes, used on slicers and axes

## Relationship best practices
- Dimensions → Facts (single direction)
- Avoid bi-directional unless you have a specific reason
- Prefer a single Date table

## Role-playing dimensions (multiple dates)
If fact has OrderDate and ShipDate, you can:
- Use one Date table + inactive relationship + USERELATIONSHIP in measures, OR
- Duplicate Date table into DateOrder / DateShip (clearer, slightly heavier)

Example measure using inactive relationship:
```dax
[Sales by Ship Date] =
CALCULATE(
    [Sales],
    USERELATIONSHIP('DateTable'[Date], 'FactSales'[ShipDate])
)
```

## Anti-patterns
- Snowflake schema (dims pointing to dims) unless needed
- Many-to-many relationships as a default
- Bi-directional everywhere
