# X++ Batch Processing: SysOperation Framework

The `SysOperation` framework is the standard for batch processing in D365FO, replacing the legacy `RunBaseBatch`. It follows the MVC (Model-View-Controller) pattern.

## Components

1.  **Data Contract (Model)**: Defines parameters. Decorate with `[DataContract]`.
2.  **Service (Controller Logic)**: Contains the business logic.
3.  **Controller**: Orchestrates execution. Extends `SysOperationServiceController`.

## Implementation Example

### Data Contract
```xpp
[DataContract]
class JGPTBatchContract
{
    str paramValue;

    [DataMember]
    public str parmValue(str _value = paramValue)
    {
        paramValue = _value;
        return paramValue;
    }
}
```

### Service
```xpp
class JGPTBatchService
{
    public void process(JGPTBatchContract _contract)
    {
        info(strFmt("Processing: %1", _contract.parmValue()));
        // ... heavy logic ...
    }
}
```

### Controller
The controller links the service method to the execution.

```xpp
class JGPTBatchController extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        JGPTBatchController controller;
        controller = new JGPTBatchController(
            classStr(JGPTBatchService), 
            methodStr(JGPTBatchService, process), 
            SysOperationExecutionMode::Synchronous);
            
        controller.startOperation();
    }
}
```

## Execution Modes
- **Synchronous**: Runs immediately on the client/interactive session. Blocking.
- **Asynchronous**: Runs in the background (CIL) but isn't a reliable batch job. Good for heavy UI tasks.
- **ReliableAsynchronous**: Similar to Asynchronous but persists task state.
- **ScheduledBatch**: Adds the task to the Batch Table to be picked up by the AOS batch server.

## Reliable Async Pattern
For critical background tasks, always prefer `SysOperationExecutionMode::ScheduledBatch` or `ReliableAsynchronous` to ensure retry capabilities if the server restarts.

## Threading (Bundling)
To process millions of records, use the `SysOperationProcess` base class or implement custom bundling logic to split the workload into multiple batch tasks (sub-tasks) that run in parallel.
