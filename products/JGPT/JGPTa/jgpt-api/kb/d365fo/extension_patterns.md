# X++ Extension Patterns: Chain of Command (CoC)

Chain of Command (CoC) is the modern mechanism for extending standard D365FO logic. It replaces legacy event handlers for most scenarios, offering better readability and access to protected members.

## Basic Wrapper
To wrap a method, create a class with the `[ExtensionOf]` attribute and end the class name with `_Extension`.

```xpp
[ExtensionOf(tableStr(CustTable))]
final class CustTable_JGPT_Extension
{
    public void insert()
    {
        // Pre-event logic
        this.JGPT_CustomField = 'Default';

        // standard call
        next insert();

        // Post-event logic
        if (this.AccountNum == '1001')
        {
            info("Special customer created!");
        }
    }
}
```

## Wrappers with Return Values
When wrapping a method that returns a value, capture the result of `next`.

```xpp
[ExtensionOf(classStr(SalesFormLetter))]
final class SalesFormLetter_JGPT_Extension
{
    protected boolean validate(Object _contract)
    {
        boolean ret = next validate(_contract);

        if (ret)
        {
             // Add custom validation only if standard validation passed
             if (!this.jgpt_checkCustomRule())
             {
                 ret = checkFailed("Custom rule failed.");
             }
        }
        
        return ret;
    }
}
```

## Disposable Context Pattern
If you need to pass state between a pre-event and a post-event (or between deep method calls) without modifying method signatures, use the **Disposable Context** pattern (usually a singleton or thread-local storage).

1.  **Context Class**: Stores the state.
2.  **Using Clause**: Instantiates the context at the entry point.
3.  **Consumption**: Inner methods check the context instance for state.

## Best Practices
- **Always call `next`**: Unless you intentionally want to break the chain (rare and dangerous), always call `next`.
- **Avoid heavy logic in loops**: If extending a method inside a loop, keep the extension lightweight.
- **Naming**: Suffix extension classes with `_Extension`.
