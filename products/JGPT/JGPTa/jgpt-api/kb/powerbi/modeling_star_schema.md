# Power BI Data Modeling: Star Schema & Relationships

## The Golden Rule: Star Schema or Burst
In Power BI, the **Star Schema** is not just a suggestion—it is the engine of performance. 90% of DAX complexity comes from a bad data model.

### 1. The Rules of Engagement
1.  **Fact Tables** contain numbers (Transactions).
2.  **Dimension Tables** contain text (Attributes).
3.  **Relationships** are always **One-to-Many** from Dimension to Fact.
4.  **Filters** flow **downhill** (from 1 side to * side).

### 2. Forbidden Patterns ⛔
#### The "Bi-Directional" Trap
DO NOT enable "Both" direction relationships unless absolutely necessary (e.g., bridging a many-to-many via a bridge table).
**Why?**
- It introduces ambiguity in filter paths.
- It kills performance by forcing dimension filtering on massive fact tables.
- It enables "Context Transition" where you don't expect it.

**The Fix:**
Use `CROSSFILTER` in DAX if you need to filter a dimension by a fact for a *specific measure*.
```dax
Active Customers = 
CALCULATE(
    COUNTROWS(Customer),
    CROSSFILTER(Sales[CustomerKey], Customer[CustomerKey], Both)
)
```

#### The "Snowflake" Drift
Avoid chaining dimensions (DimProduct -> DimCategory -> DimSubCategory).
**The Fix:**
Collapse specific attributes into the main Dimension table. Power BI handles wide tables (100+ columns) in VertiPaq efficiently. Joins are expensive; column compression is cheap.

### 3. Handling Many-to-Many (M2M)
Direct M2M relationships (e.g., Sales to Budget on granularity) are risky.
**The "Bridge Table" Pattern**:
1.  Create a distinct table of common keys (e.g., `BridgeAccount`, `BridgeDate`).
2.  Relate Fact 1 (Sales) to Bridge (Many-to-One).
3.  Relate Fact 2 (Budget) to Bridge (Many-to-One).
4.  Filters flow from Bridge -> Facts.

### 4. Auto-Date Time: The Silent Killer
**ALWAYS** disable "Auto Date/Time" in Options.
**Why?**
- It creates a hidden calculated table for *every* date column relationships.
- It bloats file size by 20-50%.
- It prevents standard time intelligence optimization.
**The Fix:**
Use a single, explicit `Date` dimension table marked as a "Date Table".

### 5. Key Columns
- **Hide key columns** (e.g., `CustomerKey`, `ProductKey`) from the Report View. Users should filter by `Customer Name`, not `CustomerKey`.
- Keys are for joining, not for viewing.
