# DRAFT: Async Workload Decision Rule

## Current workload

- Three slow HTTP calls to the same service.
- Each call is independent and mostly spends time waiting on I/O.

## When to use synchronous code

- Keep synchronous (one call after another) when:
  - Requests depend on results from earlier requests.
  - The timing improvement from threads is too small to justify extra complexity.
  - Simpler control flow and easier debugging are more important than latency.

## When to use threads

- Use threads when:
  - Requests are independent and can safely run in parallel.
  - The work is I/O-bound (most of the time is waiting on network or other I/O).
  - Measurements show a clear reduction in total time compared to the sequential baseline.

## Evidence from measurements

- Sequential 3-call HTTP baseline: ~3.05 seconds.
- Threaded 3-call HTTP run: ~1.06 seconds total.
  - Each request still takes ~1 second, but waits overlap.
- CPU-bound counting loop:
  - Sequential average: ~0.2405 seconds.
  - Threaded average: ~0.2403 seconds (no meaningful speedup).

These measurements show:
- Threads **help** for I/O-bound HTTP calls by overlapping waiting time.
- Threads do **not** make pure-Python CPU-bound work faster under CPython.

## Notes and out-of-scope

- For CPU-bound work that really needs to be faster, **processes** are the likely next step, but they are out of scope for this lesson.
- This document is a **DRAFT**. It does not yet include measurements or rules for async/`await` or asynchronous HTTP clients.