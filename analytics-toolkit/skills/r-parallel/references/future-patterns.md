# Future Patterns — Code Templates

BEFORE/AFTER code pairs for every supported conversion pattern.

---

## A. Setup Block

Standard preamble for any parallelized script. Place at the top, before any parallel calls.

```r
# --- Parallel setup ---
library(future)
library(future.apply)    # for future_lapply, future_sapply, etc.
# library(furrr)         # uncomment if using purrr conversions
# library(doFuture)      # uncomment if using foreach conversions
# library(progressr)     # uncomment if using progress reporting

plan(multisession)        # cross-platform parallel backend
set.seed(12345)           # one seed for the entire script
```

Notes:
- `plan()` after `library()` — plan depends on loaded packages
- `set.seed()` before any parallel calls — governs all downstream RNG
- Add only the packages you actually use

---

## B. Base R Apply Conversions

### lapply → future_lapply

**BEFORE:**
```r
results <- lapply(data_list, function(d) {
  lm(y ~ x, data = d)
})
```

**AFTER:**
```r
results <- future_lapply(data_list, function(d) {
  lm(y ~ x, data = d)
}, future.seed = TRUE)
```

### sapply → future_sapply

**BEFORE:**
```r
means <- sapply(data_list, function(d) mean(d$x))
```

**AFTER:**
```r
means <- future_sapply(data_list, function(d) mean(d$x), future.seed = TRUE)
```

### vapply → future_vapply

**BEFORE:**
```r
means <- vapply(data_list, function(d) mean(d$x), numeric(1))
```

**AFTER:**
```r
means <- future_vapply(data_list, function(d) mean(d$x), numeric(1), future.seed = TRUE)
```

### mapply / Map → future_mapply

**BEFORE:**
```r
results <- mapply(function(x, y) x + y, vec_a, vec_b)
# or
results <- Map(function(x, y) x + y, vec_a, vec_b)
```

**AFTER:**
```r
results <- future_mapply(function(x, y) x + y, vec_a, vec_b, future.seed = TRUE)
```

### tapply → future_tapply

**BEFORE:**
```r
group_means <- tapply(df$value, df$group, mean)
```

**AFTER:**
```r
group_means <- future_tapply(df$value, df$group, mean, future.seed = TRUE)
```

### by → future_by

**BEFORE:**
```r
models <- by(df, df$group, function(d) lm(y ~ x, data = d))
```

**AFTER:**
```r
models <- future_by(df, df$group, function(d) lm(y ~ x, data = d), future.seed = TRUE)
```

---

## C. For-Loop Conversions

### Accumulating for-loop → future_lapply

**BEFORE:**
```r
results <- list()
for (i in seq_along(params)) {
  results[[i]] <- run_simulation(params[[i]])
}
```

**AFTER:**
```r
results <- future_lapply(params, function(p) {
  run_simulation(p)
}, future.seed = TRUE)
```

### Index-based subsetting → future_lapply with index vector

**BEFORE:**
```r
results <- vector("list", nrow(df))
for (i in 1:nrow(df)) {
  results[[i]] <- process_row(df[i, ])
}
```

**AFTER:**
```r
row_list <- split(df, seq_len(nrow(df)))
results <- future_lapply(row_list, function(row) {
  process_row(row)
}, future.seed = TRUE)
```

### Nested loops → flatten to single future_lapply over expand.grid

**BEFORE:**
```r
results <- list()
k <- 1
for (alpha in alphas) {
  for (beta in betas) {
    results[[k]] <- fit_model(alpha, beta)
    k <- k + 1
  }
}
```

**AFTER:**
```r
grid <- expand.grid(alpha = alphas, beta = betas, stringsAsFactors = FALSE)
results <- future_lapply(seq_len(nrow(grid)), function(i) {
  fit_model(grid$alpha[i], grid$beta[i])
}, future.seed = TRUE)
```

### Pre-allocated matrix rows → future_lapply + do.call(rbind)

**BEFORE:**
```r
mat <- matrix(NA, nrow = B, ncol = p)
for (b in 1:B) {
  mat[b, ] <- compute_row(b)
}
```

**AFTER:**
```r
row_list <- future_lapply(seq_len(B), function(b) {
  compute_row(b)
}, future.seed = TRUE)
mat <- do.call(rbind, row_list)
```

---

## D. purrr/furrr Conversions

All furrr functions take `.options = furrr_options(seed = TRUE)` for seed handling.

### map → future_map

**BEFORE:**
```r
library(purrr)
results <- map(data_list, ~ lm(y ~ x, data = .x))
```

**AFTER:**
```r
library(furrr)
plan(multisession)
results <- future_map(data_list, ~ lm(y ~ x, data = .x),
                      .options = furrr_options(seed = TRUE))
```

### map_dfr / map_dfc → future_map_dfr / future_map_dfc

**BEFORE:**
```r
all_results <- map_dfr(file_paths, ~ read_and_process(.x))
```

**AFTER:**
```r
all_results <- future_map_dfr(file_paths, ~ read_and_process(.x),
                              .options = furrr_options(seed = TRUE))
```

### map2 → future_map2

**BEFORE:**
```r
results <- map2(formulas, datasets, ~ lm(.x, data = .y))
```

**AFTER:**
```r
results <- future_map2(formulas, datasets, ~ lm(.x, data = .y),
                       .options = furrr_options(seed = TRUE))
```

### pmap → future_pmap

**BEFORE:**
```r
params <- list(alpha = alphas, beta = betas, gamma = gammas)
results <- pmap(params, function(alpha, beta, gamma) {
  fit_model(alpha, beta, gamma)
})
```

**AFTER:**
```r
params <- list(alpha = alphas, beta = betas, gamma = gammas)
results <- future_pmap(params, function(alpha, beta, gamma) {
  fit_model(alpha, beta, gamma)
}, .options = furrr_options(seed = TRUE))
```

### walk → future_walk

**BEFORE:**
```r
walk(plots, ~ ggsave(filename = .x$path, plot = .x$plot))
```

**AFTER:**
```r
future_walk(plots, ~ ggsave(filename = .x$path, plot = .x$plot),
            .options = furrr_options(seed = TRUE))
```

### imap → future_imap

**BEFORE:**
```r
results <- imap(named_list, ~ process(.x, name = .y))
```

**AFTER:**
```r
results <- future_imap(named_list, ~ process(.x, name = .y),
                       .options = furrr_options(seed = TRUE))
```

---

## E. foreach/doFuture Conversions

### foreach %do% → foreach %dofuture%

**BEFORE:**
```r
library(foreach)
results <- foreach(i = 1:100) %do% {
  run_simulation(i)
}
```

**AFTER:**
```r
library(foreach)
library(doFuture)
plan(multisession)
results <- foreach(i = 1:100, .options.future = list(seed = TRUE)) %dofuture% {
  run_simulation(i)
}
```

### foreach %dopar% with old backend → migrate to %dofuture%

**BEFORE:**
```r
library(foreach)
library(doParallel)
cl <- makeCluster(4)
registerDoParallel(cl)
results <- foreach(i = 1:100, .packages = c("dplyr"), .export = c("my_func")) %dopar% {
  my_func(data[i, ])
}
stopCluster(cl)
```

**AFTER:**
```r
library(foreach)
library(doFuture)
plan(multisession, workers = 4)
results <- foreach(i = 1:100, .options.future = list(seed = TRUE)) %dofuture% {
  my_func(data[i, ])
}
plan(sequential)
```

Notes on foreach migration:
- `.packages` is no longer needed — `future` auto-detects required packages
- `.export` is no longer needed — `future` auto-detects globals
- If auto-detection fails, use `future.packages` and `future.globals` options
- `.combine` is preserved as-is — it still works with `%dofuture%`
- No manual cluster creation/teardown — `plan()` handles it

### foreach with .combine

**BEFORE:**
```r
results <- foreach(i = 1:100, .combine = rbind) %dopar% {
  compute_row(i)
}
```

**AFTER:**
```r
results <- foreach(i = 1:100, .combine = rbind,
                   .options.future = list(seed = TRUE)) %dofuture% {
  compute_row(i)
}
```

---

## F. replicate Conversions

**BEFORE:**
```r
set.seed(42)
boot_stats <- replicate(10000, {
  idx <- sample(nrow(df), replace = TRUE)
  mean(df$x[idx])
})
```

**AFTER:**
```r
set.seed(42)
boot_list <- future_lapply(seq_len(10000), function(b) {
  idx <- sample(nrow(df), replace = TRUE)
  mean(df$x[idx])
}, future.seed = TRUE)
boot_stats <- simplify2array(boot_list)
```

Note: `replicate()` has no direct `future_replicate()`. Convert to `future_lapply()` over an integer sequence and use `simplify2array()` if you need a vector/matrix output.

---

## G. Econometrics-Specific Patterns

### 1. Bootstrap Inference

**BEFORE:**
```r
set.seed(42)
B <- 5000
boot_coefs <- matrix(NA, nrow = B, ncol = 2)
for (b in 1:B) {
  idx <- sample(nrow(df), replace = TRUE)
  boot_df <- df[idx, ]
  fit <- lm(y ~ x, data = boot_df)
  boot_coefs[b, ] <- coef(fit)
}
ci <- apply(boot_coefs, 2, quantile, probs = c(0.025, 0.975))
```

**AFTER:**
```r
set.seed(42)
B <- 5000
boot_list <- future_lapply(seq_len(B), function(b) {
  idx <- sample(nrow(df), replace = TRUE)
  boot_df <- df[idx, ]
  fit <- lm(y ~ x, data = boot_df)
  coef(fit)
}, future.seed = TRUE)
boot_coefs <- do.call(rbind, boot_list)
ci <- apply(boot_coefs, 2, quantile, probs = c(0.025, 0.975))
```

### 2. Monte Carlo Simulation

**BEFORE:**
```r
set.seed(123)
n_sims <- 10000
n_obs <- 100
results <- data.frame(bias = numeric(n_sims), rmse = numeric(n_sims))
for (s in 1:n_sims) {
  x <- rnorm(n_obs)
  eps <- rnorm(n_obs)
  y <- 2 + 3 * x + eps
  fit <- lm(y ~ x)
  results$bias[s] <- coef(fit)[2] - 3
  results$rmse[s] <- sqrt(mean(residuals(fit)^2))
}
```

**AFTER:**
```r
set.seed(123)
n_sims <- 10000
n_obs <- 100
sim_list <- future_lapply(seq_len(n_sims), function(s) {
  x <- rnorm(n_obs)
  eps <- rnorm(n_obs)
  y <- 2 + 3 * x + eps
  fit <- lm(y ~ x)
  data.frame(bias = coef(fit)[2] - 3, rmse = sqrt(mean(residuals(fit)^2)))
}, future.seed = TRUE)
results <- do.call(rbind, sim_list)
```

### 3. Cross-Validation Folds

**BEFORE:**
```r
set.seed(42)
K <- 10
folds <- sample(rep(1:K, length.out = nrow(df)))
cv_errors <- numeric(K)
for (k in 1:K) {
  train <- df[folds != k, ]
  test  <- df[folds == k, ]
  fit <- lm(y ~ ., data = train)
  preds <- predict(fit, newdata = test)
  cv_errors[k] <- mean((test$y - preds)^2)
}
cv_mse <- mean(cv_errors)
```

**AFTER:**
```r
set.seed(42)
K <- 10
folds <- sample(rep(1:K, length.out = nrow(df)))
cv_list <- future_lapply(1:K, function(k) {
  train <- df[folds != k, ]
  test  <- df[folds == k, ]
  fit <- lm(y ~ ., data = train)
  preds <- predict(fit, newdata = test)
  mean((test$y - preds)^2)
}, future.seed = TRUE)
cv_errors <- unlist(cv_list)
cv_mse <- mean(cv_errors)
```

Note: `folds` is computed sequentially before the parallel call — the fold assignment itself must be reproducible and is controlled by the upstream `set.seed(42)`.

### 4. Multiple Model Specifications

**BEFORE:**
```r
library(fixest)
formulas <- list(
  y ~ x1 | fe1,
  y ~ x1 + x2 | fe1,
  y ~ x1 + x2 | fe1 + fe2,
  y ~ x1 + x2 + x3 | fe1 + fe2
)
models <- lapply(formulas, function(f) feols(f, data = df))
```

**AFTER:**
```r
library(fixest)
formulas <- list(
  y ~ x1 | fe1,
  y ~ x1 + x2 | fe1,
  y ~ x1 + x2 | fe1 + fe2,
  y ~ x1 + x2 + x3 | fe1 + fe2
)
models <- future_lapply(formulas, function(f) {
  fixest::feols(f, data = df)
}, future.seed = TRUE)
```

Note: Prefix with `fixest::` inside the worker to ensure the function is found. For deterministic model fits (no bootstrapped SEs), `future.seed = NULL` is also fine.

### 5. Permutation Tests

**BEFORE:**
```r
set.seed(42)
n_perm <- 10000
obs_stat <- mean(df$y[df$treat == 1]) - mean(df$y[df$treat == 0])
perm_stats <- numeric(n_perm)
for (p in 1:n_perm) {
  perm_treat <- sample(df$treat)
  perm_stats[p] <- mean(df$y[perm_treat == 1]) - mean(df$y[perm_treat == 0])
}
p_value <- mean(abs(perm_stats) >= abs(obs_stat))
```

**AFTER:**
```r
set.seed(42)
n_perm <- 10000
obs_stat <- mean(df$y[df$treat == 1]) - mean(df$y[df$treat == 0])
perm_list <- future_lapply(seq_len(n_perm), function(p) {
  perm_treat <- sample(df$treat)
  mean(df$y[perm_treat == 1]) - mean(df$y[perm_treat == 0])
}, future.seed = TRUE)
perm_stats <- unlist(perm_list)
p_value <- mean(abs(perm_stats) >= abs(obs_stat))
```

### 6. Processing Multiple Datasets/Files

**BEFORE:**
```r
files <- list.files("data/", pattern = "\\.csv$", full.names = TRUE)
all_results <- list()
for (f in files) {
  df <- read.csv(f)
  df <- clean_data(df)
  fit <- lm(y ~ x, data = df)
  all_results[[f]] <- tidy(fit)
}
combined <- do.call(rbind, all_results)
```

**AFTER:**
```r
files <- list.files("data/", pattern = "\\.csv$", full.names = TRUE)
all_results <- future_lapply(files, function(f) {
  df <- read.csv(f)
  df <- clean_data(df)
  fit <- lm(y ~ x, data = df)
  broom::tidy(fit)
}, future.seed = TRUE)
combined <- do.call(rbind, all_results)
```

Note: Each worker reads its own file — no shared file handles. Prefix package functions (`broom::tidy`) to ensure availability in workers.

---

## H. Progress Reporting with progressr

For long-running parallel tasks, add progress reporting:

```r
library(progressr)
handlers(global = TRUE)

with_progress({
  p <- progressor(steps = length(x))
  results <- future_lapply(x, function(xi) {
    p()                          # signal one step completed
    expensive_function(xi)
  }, future.seed = TRUE)
})
```

With furrr:

```r
library(progressr)
handlers(global = TRUE)

with_progress({
  p <- progressor(steps = length(x))
  results <- future_map(x, function(xi) {
    p()
    expensive_function(xi)
  }, .options = furrr_options(seed = TRUE))
})
```

With foreach:

```r
library(progressr)
handlers(global = TRUE)

with_progress({
  p <- progressor(steps = n)
  results <- foreach(i = 1:n, .options.future = list(seed = TRUE)) %dofuture% {
    p()
    run_simulation(i)
  }
})
```

Notes:
- `handlers(global = TRUE)` enables progress output in non-interactive contexts
- `p()` must be called inside the worker body
- Progress works with all future backends
- Default handler shows a text progress bar; customize with `handlers("txtprogressbar")`, `handlers("cli")`, etc.

---

## I. Cleanup

Always reset to sequential at the end of a script:

```r
# --- Cleanup ---
plan(sequential)
```

This closes worker processes and frees memory. Especially important in:
- Interactive sessions (workers persist until reset)
- Quarto/R Markdown documents (set plan in setup chunk, reset in final chunk)
- Scripts that run multiple analyses with different plans
