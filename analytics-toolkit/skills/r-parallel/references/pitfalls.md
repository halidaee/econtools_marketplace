# Pitfalls Reference

When NOT to parallelize, and how to handle common problems.

---

## A. What NOT to Parallelize

Check these disqualifiers before converting any pattern.

| Pattern | Why not | Alternative |
|---|---|---|
| Sequential dependencies (iteration i depends on i−1) | Cannot parallelize — results are order-dependent | Keep sequential; vectorize if possible |
| I/O-bound tasks (same disk, DB connection limits) | Disk/network is the bottleneck, not CPU | Keep sequential or use async I/O |
| Very fast operations (< 1ms per iteration) | Worker startup and serialization overhead exceeds computation | Keep sequential; vectorize |
| Shared state modification (global vars, files, environments) | Workers have separate memory; modifications are lost | Return values from workers; merge after |
| Non-exportable objects (DBI connections, external pointers, C++ objects) | Cannot serialize across processes | Create the object inside each worker |
| Side effects (plotting, printing, message()) | Happen in worker process, not the main session | Keep side effects in sequential code |
| Small iteration count (< ~10 iterations) | Overhead of spawning workers likely exceeds benefit | Keep sequential unless each iteration is very slow |
| Code that modifies the input data in place | Workers get copies; in-place modifications are invisible | Restructure to return new data |

**Rule of thumb:** If you're unsure, benchmark. Run the loop body once and time it. If it takes less than ~10ms, parallelization is unlikely to help.

---

## B. Memory Considerations with multisession

`plan(multisession)` spawns separate R processes. Each worker gets its own memory space.

### How memory works

1. **Globals are copied** — every object the worker function references is serialized and sent to each worker process
2. **Each worker has its own copy** — N workers = N copies of globals in memory
3. **Results are serialized back** — worker results are sent back to the main process

### Memory estimation

```r
# Rough estimate: can all workers fit in RAM?
data_size <- as.numeric(object.size(my_large_object))
n_workers <- future::availableCores()
total_needed <- data_size * n_workers
cat(sprintf("Data: %.0f MB × %d workers = %.0f MB needed\n",
            data_size / 1e6, n_workers, total_needed / 1e6))
```

**Rule of thumb:** `object.size(globals) × n_workers < available RAM`

### If memory is tight

- **Reduce workers**: `plan(multisession, workers = 2)` instead of using all cores
- **Read data inside workers**: Instead of passing a large data frame, pass file paths and let each worker read its own subset
- **Increase the globals limit**: `options(future.globals.maxSize = 2 * 1024^3)` (2 GB) — but this doesn't reduce actual memory use, it just allows larger objects to be serialized
- **Chunk the work**: Split into batches, parallelize each batch, combine results

---

## C. Globals and Package Exports

### How auto-detection works

The `future` framework inspects the worker function body to identify:
- **Globals**: objects from the parent environment referenced inside the function
- **Packages**: `library()` and `::` calls inside the function

### When auto-detection fails

| Situation | Problem | Fix |
|---|---|---|
| Dynamic variable names (`get()`, `eval(parse(...))`) | Can't statically analyze | Use `future.globals = list(var = val)` |
| Functions from non-standard environments | Not found in expected scopes | Use `future.packages = c("pkg")` |
| Formulas referencing external data | Formula environments are complex | Pass data explicitly as an argument |
| R6 or reference class objects | May not serialize correctly | Create inside worker or use simpler structures |

### Explicit specification

```r
# Explicit globals
results <- future_lapply(1:10, function(i) {
  my_func(shared_data, i)
}, future.globals = list(my_func = my_func, shared_data = shared_data),
   future.packages = c("dplyr", "fixest"),
   future.seed = TRUE)
```

Only use explicit globals when auto-detection fails. The auto-detection is correct in the vast majority of cases.

---

## D. Debugging Parallel Code

### Strategy: sequential first, parallel second

1. **Always test with `plan(sequential)` first**
   - `plan(sequential)` runs future code in the main process
   - Normal tracebacks, normal debugging, normal error messages
   - If it works sequentially but fails in parallel → the problem is parallelization-specific

2. **Wrap worker body in tryCatch for per-element errors**
   ```r
   results <- future_lapply(seq_along(x), function(i) {
     tryCatch({
       process(x[[i]])
     }, error = function(e) {
       list(index = i, error = conditionMessage(e))
     })
   }, future.seed = TRUE)

   # Find failures
   errors <- Filter(function(r) is.list(r) && !is.null(r$error), results)
   ```

3. **Check specific futures (low-level)**
   ```r
   f <- future({ expensive_computation() }, seed = TRUE)
   resolved(f)   # TRUE/FALSE — has it finished?
   value(f)      # block and get result (or re-throw error)
   ```

### Common debugging scenarios

**"It works sequentially but not in parallel"**
- Missing package in worker → add `library()` call or `future.packages`
- Missing global variable → add to `future.globals`
- Non-exportable object → create inside worker
- Side effect dependency → restructure to return values

**"Results differ between sequential and parallel"**
- Missing `future.seed = TRUE` → add it
- `set.seed()` inside worker → remove it
- Order-dependent computation → cannot parallelize
- Floating-point accumulation order → use `all.equal()` with tolerance

---

## E. Common Error Messages

| Error | Cause | Fix |
|---|---|---|
| `"The total size of globals exported is ... exceeding the maximum"` | Large objects being copied to workers | Increase limit: `options(future.globals.maxSize = 2 * 1024^3)` or restructure to avoid copying |
| `"A non-exportable object of class '...' detected"` | DB connection, external pointer, C++ object | Create the object inside each worker function |
| `"unused argument (future.seed = TRUE)"` | Using base `lapply()` instead of `future_lapply()` | Change to `future_lapply()` |
| `"could not find function 'my_func'"` | Worker doesn't have access to function | Define in global environment, use `pkg::func()`, or pass via `future.globals` |
| `"object 'x' not found"` | Global auto-detection missed a variable | Pass explicitly via `future.globals = list(x = x)` |
| `"Error in unserialize(node$con) : error reading from connection"` | Worker process crashed (usually out of memory) | Reduce workers or data size |
| `"Cannot set a Column Spec ... future.seed must be FALSE"` | Package conflict with seed handling | Check for conflicting packages; ensure correct seed argument syntax |
| `"UNRELIABLE VALUE: ... of 'MultisessionFuture' ..."` | Worker returned unexpected type or encountered a warning treated as error | Check worker function return type; test with `plan(sequential)` |

---

## F. Performance Tuning

### Number of workers

```r
# See available cores
future::availableCores()

# Use all but one (leave one for the OS / main R session)
plan(multisession, workers = availableCores() - 1)

# Or set explicitly
plan(multisession, workers = 4)
```

### Chunk size

Controls how tasks are batched and sent to workers.

```r
# One task per chunk — best for uneven task durations
future_lapply(x, fun, future.seed = TRUE, future.chunk.size = 1)

# Auto chunking (default) — best for many small, uniform tasks
future_lapply(x, fun, future.seed = TRUE, future.chunk.size = NULL)

# Large chunks — reduces overhead for very many tiny tasks
future_lapply(x, fun, future.seed = TRUE, future.chunk.size = 100)
```

**Guidance:**
- Uneven tasks (some take seconds, some take minutes) → `future.chunk.size = 1`
- Many uniform tasks (10,000+ iterations, ~same duration) → let auto-chunking handle it
- Very many tiny tasks (100,000+ fast iterations) → increase chunk size

### Multi-machine parallelism via SSH

```r
# Connect to remote machines (requires passwordless SSH)
plan(cluster, workers = c("localhost", "server1.example.com", "server2.example.com"))
```

Requirements:
- Same R version on all machines
- Same packages installed
- Shared filesystem or data accessible from each machine
- Passwordless SSH configured

---

## G. Cleanup and Resource Management

### Always reset the plan

```r
# At the end of every script
plan(sequential)
```

This shuts down worker processes and frees memory. Without it, workers persist in the background.

### In Quarto / R Markdown

```r
# In setup chunk:
library(future)
library(future.apply)
plan(multisession)

# ... parallel code in middle chunks ...

# In final chunk:
plan(sequential)
```

### Connection and resource limits

If workers open database connections, API connections, or file handles:
- Respect pool sizes (e.g., max DB connections)
- Open connections inside workers, not in the parent
- Close connections at the end of each worker's task

```r
results <- future_lapply(queries, function(q) {
  con <- DBI::dbConnect(...)    # open inside worker
  on.exit(DBI::dbDisconnect(con))  # ensure cleanup
  DBI::dbGetQuery(con, q)
}, future.seed = TRUE)
```

### Temporary files in workers

Workers have their own `tempdir()`. Temp files created in workers are cleaned up when the worker process exits (when `plan(sequential)` is called).
