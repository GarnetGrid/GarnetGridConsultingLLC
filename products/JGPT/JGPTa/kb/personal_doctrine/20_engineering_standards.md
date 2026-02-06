## DOC-ENG-001: Durability beats cleverness
- **Domain:** engineering
- **Priority:** P1
- **Rule:** Prefer boring, observable, failure-tolerant solutions.
- **Do:** retries, idempotency, metrics, limits
- **Avoid:** hidden state, magic defaults
- **Tags:** #durability #production

## DOC-ENG-002: Async must be bounded
- **Domain:** engineering
- **Priority:** P1
- **Rule:** All async pipelines must have limits or backpressure.
- **Do:** chunking, queues, batching
- **Avoid:** unbounded async fan-out
- **Tags:** #async #pipelines

## DOC-ENG-003: Defaults should be safe
- **Domain:** engineering
- **Priority:** P1
- **Rule:** Default behavior should fail safely and visibly.
- **Tags:** #safety #defaults
