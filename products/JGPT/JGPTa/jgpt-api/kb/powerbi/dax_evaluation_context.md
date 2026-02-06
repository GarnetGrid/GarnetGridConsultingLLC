# DAX Evaluation Context: The "Senior" Guide

## 1. The Two Contexts
If you don't understand this, you don't know DAX.

### Row Context
- **Definition**: "Current Row". Exists **ONLY** in Calculated Columns and Iterators (`SUMX`, `FILTER`).
- **Does NOT** filter the data model.
- **Example**: `Price * Quantity` inside a calculated column works because of Row Context.

### Filter Context
- **Definition**: The set of active filters at the moment of calculation.
- **Sources**: Visuals (Slicers, Axes), `CALCULATE`, `CALCULATETABLE`.
- **Propagates**: Flows "downhill" through relationships (1 side filters * side).

---

## 2. Context Transition
The most common source of bugs.
**Definition**: When Row Context is transformed into Filter Context.
**Trigger**: Invoked automatically by `CALCULATE`.

### The Hidden Calculate
Writing `[Measure]` is actually `CALCULATE( [Measure] )`. This forces Context Transition.

### Classic Error: "Total is Wrong"
```dax
// WRONG: Iterating without Context Transition
SUMX( Sales, Sales[Quantity] * DISTINCTCOUNT( Sales[Product] ) ) 
// Returns SUM(Quantity) * 1 for every row, then sums it up. 
// Because DISTINCTCOUNT sees ALL products (no filter context from the row).
```

### The Fix
```dax
// CORRECT: Wrap in CALCULATE to turn the current row's ID into a filter
SUMX( Sales, Sales[Quantity] * CALCULATE( DISTINCTCOUNT( Sales[Product] ) ) )
```

---

## 3. Evaluation Order (The Algorithm)
1. **Initial Filter Context**: Slicers, Rows, Columns in the visual.
2. **CALCULATE Modifiers**: `ALL`, `REMOVEFILTERS`, `KEEPFILTERS` applied.
3. **CALCULATE Filters**: New filters added/overwritten.
4. **Relationship Propagation**: Filters flow down 1->* relationships.
5. **Expression Evaluation**: The math runs against the final filtered subset.

---

## 4. `KEEPFILTERS`
Essential for "Ad-Hoc" filtering without removing external filters.

```dax
// Standard: Replaces "Red" filter with "Blue"
CALCULATE( [Sales], Product[Color] = "Blue" )

// KeepFilters: Intersects. Returns (Existing Filter AND "Blue")
CALCULATE( [Sales], KEEPFILTERS( Product[Color] = "Blue" ) )
```
