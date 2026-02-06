# Delegates - Finance & Operations

**Source:** https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/extensible-code-delegates
**Captured:** 2026-02-02
**Domain:** d365fo

Although you can subscribe to existing delegates, don't create new delegates. The Chain of Command (CoC) provides a richer, more robust, and more concise extension mechanism that supersedes delegates.

Instead of creating new delegates, structure your code in small methods that have good names, as described in the [guidelines for writing extensible methods](extensible-methods).

If you decide to use delegates, consider ensuring no more than one response where applicable. For more information, see [EventHandlerResult classes in request or response scenarios](../dev-tools/event-handler-result-class).
