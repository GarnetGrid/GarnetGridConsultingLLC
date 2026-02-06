# Data Entities & DMF Optimization

## 1. OData vs. DMF (Package API)
The strict rule for D365FO integration architecture:
- **OData**: Real-time, small volume (1-100 records). CRUD operations. Slow.
- **DMF (Package API)**: Batch, high volume (>1000 records). Asynchronous. Fast.

### OData Anti-Pattern
Looping through 50,000 records via OData GET/POST calls. This will throttle the environment and likely time out.
**Fix**: Use the **Recurring Integrations** or **Data Package API** to export/import a CSV/ZIP file.

---

## 2. Entity Performance Tuning

### `Set-Based` Operations
Data entities normally process row-by-row. To enable fast SQL bulk inserts:
1. Properties: Set `Enable Set Based SQL Operations` = **Yes**.
2. Avoid `postLoad()`: Logic in `postLoad` forces row-by-row execution.

### Virtual Fields (Computed vs. Virtual)
- **Computed Column (Faster)**: A T-SQL view column. Calculated directly in SQL Server. efficient.
    - Use for string manipulation, simple joins.
    - *Example*: Concatenating First + Last Name.
- **Virtual Field (Slower)**: Calculated in X++ (`postLoad`).
    - Use only if business logic requires X++ libraries (e.g., number sequence, tax engine).

### `insertEntityDataSource`
Override `insertEntityDataSource` instead of `mapEntityToDataSource` for cleaner control over field mapping during imports.

---

## 3. High-Performance Export
For millions of records (e.g., BYOD, Azure Data Lake):
- **Incremental Push**: Enable "Change Tracking" on the entity.
- **Entity Store**: For PowerBI analytics, use Aggregate Measurements (Entity Store) instead of standard Data Entities. It pushes data to `AxDW` (optimized Columnstore indices).

---

## 4. Dual Write & Virtual Entities
- **Dual Write**: Synchronous. If F&O fails, Dataverse fails (and vice versa). High latency impact.
- **Virtual Entities**: No data replication. Dataverse "sees" F&O data live. Preferred for creating Power Apps on top of F&O logic without duplicating data.

---

## 5. Security & Keys
- **Public Collection Name**: Must be unique.
- **Primary Key**: The Entity Key must strictly match the unique index of the underlying root table. Mismatches cause duplicate errors during staging-to-target.
