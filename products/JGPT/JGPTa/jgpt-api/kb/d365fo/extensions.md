# X++ Extensions & Extensibility Patterns

## 1. Chain of Command (CoC)
CoC is the modern standard for extending logic. It allows you to wrap existing methods (public or protected) to run code before or after the standard logic.

### Syntax
```xpp
[ExtensionOf(tableStr(CustTable))]
final class CustTable_JGPT_Extension
{
    public void insert()
    {
        // 1. Pre-logic
        if (this.AccountNum == '1001')
        {
            warning("Special handling for 1001");
        }

        // 2. Call next (Mandatory)
        next insert();

        // 3. Post-logic
        this.JGPT_CustomField = 'Processed';
    }
}
```

### Critical Rules
- **`next` is Mandatory**: You MUST call `next method()` to ensure the chain continues. Failing to do so breaks other ISV/Microsoft extensions.
- **Wrapper Class**: Must be `final`.
- **Naming**: Suffix your extension class (e.g., `_Extension`) to avoid collisions.

---

## 2. Event Handlers
Used when you need to react to specific standard hooks (like `OnValidated`, `OnInserted`) without wrapping the entire method.

### Best Practice
Prefer CoC over Event Handlers where possible. CoC gives you access to `protected` members and local state more easily. Event handlers are "outsiders" looking in.

```xpp
class CustTableEventHandler
{
    [DataEventHandler(tableStr(CustTable), DataEventType::Inserted)]
    public static void CustTable_onInserted(Common sender, DataEventArgs e)
    {
        CustTable custTable = sender as CustTable;
        // ... logic
    }
}
```

---

## 3. Form Extensions
You cannot modify standard forms directly. You must create an extension.
- **Adding Controls**: Add new fields/buttons.
- **Events**: Use FormDataSource event handlers (`OnActivated`, `OnWriting`) for UX logic.

### FormDataSource CoC
To override a FormDataSource method (e.g., `active`), extend the FormDataSource class, not the Form itself.

```xpp
[ExtensionOf(formDataSourceStr(CustTable, CustTable))]
final class CustTable_Form_DataSource_Extension
{
    public int active()
    {
        int ret = next active();
        // Custom logic here
        return ret;
    }
}
```

---

## 4. Breaking Changes & Upgrade Safety
- **Never Overlayer**: Overlayering is dead. Everything must be an extension.
- **Intrusive Modifications**: If you cannot achieve your goal with CoC/Events, request an **Extensibility Request** from Microsoft via LCS. Do not hack around private methods using reflection.
