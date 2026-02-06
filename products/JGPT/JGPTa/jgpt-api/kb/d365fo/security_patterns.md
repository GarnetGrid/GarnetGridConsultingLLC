# D365FO Security Patterns: XDS & Role-Based Architecture

## The Gold Standard: Security Matches Code
In D365FO, security is not an afterthought; it is code.
**Best Practice**: Every new Menu Item must have a corresponding new Privilege.

### 1. The Hierarchy of Power
1.  **Role** (Job Title): "Accounts Payable Clerk". Contains Duties.
2.  **Duty** (Business Process): "Maintain Vendors". Contains Privileges.
3.  **Privilege** (Action): "View Vendor Details". Contains Entry Points (Permissions).
4.  **Permission** (Grain): Read/Update/Create/Delete access to a Table or Field.

**Rule**: NEVER assign Privileges directly to Roles. Always use Duties as the grouping layer.
**Why?** It makes SoD (Segregation of Duties) reporting possible.

### 2. Extensible Data Security (XDS)
Standard security hides menus. XDS hides **rows**.
Use XDS when:
- "Sales Reps should only see customers in *their* region."
- "Plant Managers should only see Production Orders for *their* site."

#### XDS Implementation Steps
1.  **Query**: X++ Query defining the *allowed* records (e.g., `Select Region from CustTable where Region == MyRegion`).
2.  **Security Policy**: AOT artifact linking the Query to the Constrained Table (`CustTable`).
3.  **Context**: Constrained Context ("RoleName") or Unconstrained Context.

**Performance Warning**: XDS adds a `WHERE` clause to *every* SQL statement against the table. Ensure indices exist on the constrained fields.

### 3. X++ Security Checks
Stop hardcoding "Admin". Check capabilities.

```xpp
// BAD: Checking specific users
if (curUserId() == "Admin") { ... }

// GOOD: Checking functional access
SecurityRights rights = SecurityRights::construct();
AccessType access = rights.menuItemAccessRight(MenuItemType::Display, menuItemDisplayStr(CustTable));

if (access >= AccessType::Delete)
{
    // Enable sensitive logic
}
```

### 4. Least Privilege & Audit
- **Entry Points First**: Start design by listing Menu Items.
- **Diagnostics**: Use the "Security Diagnostics" button on forms to see which Roles grant access.
- **Reference Duty**: `SysServerXXX` roles are dangerous. Audit them.
