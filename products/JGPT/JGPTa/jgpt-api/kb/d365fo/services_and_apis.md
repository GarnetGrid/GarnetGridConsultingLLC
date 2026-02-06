# Services + APIs (Integrations)

## Custom service pattern (SysOperation)
- Contract class (DataContractAttribute)
- Service class (business logic)
- Controller class (entrypoint)

## REST / OData notes
- Standard entities expose OData endpoints
- Use batch when possible
- Handle throttling and retries

## Power Automate integration tips
- Prefer calling a stable API endpoint
- Use idempotency keys if you can
- Log correlation IDs in D365 and your middleware
