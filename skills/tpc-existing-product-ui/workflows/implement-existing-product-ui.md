---
name: implement-existing-product-ui
description: Implement a bounded UI change in an existing TPC product surface.
---

# Implement Existing Product UI

## 1. Establish the exact surface

1. Read the repository's `AGENTS.md` and design guidance before editing.
2. Trace the requested route, its component hierarchy, and one nearby product
   surface that already has the desired pattern.
3. State the requested behavior, the in-scope files, and what remains out of
   scope. If the task is ambiguous, start with the smallest reversible slice.

## 2. Reuse the product system

1. Prefer shared layout, navigation, and UI primitives over page-local copies.
2. Preserve existing tokens, typography, spacing, and interaction conventions
   unless the request explicitly changes them.
3. Keep data, authorization, loading, empty, error, and keyboard behavior
   intact while changing presentation.
4. For responsive or interaction changes, account for narrow and wide layouts
   during implementation rather than treating mobile as a later polish pass.

## 3. Iterate without scope drift

1. Implement one coherent, visible batch.
2. When feedback changes the target, update the scope before continuing; do
   not carry forward unrelated planned changes.
3. Extract a shared component only when at least two in-scope surfaces need
   the same behavior or presentation.

## 4. Verify the actual product surface

1. Load the real route in a browser using the repository's browser-verification
   workflow.
2. Exercise the changed interaction and its affected loading, empty, or error
   state when relevant.
3. For visual changes, inspect mobile, medium, and wide viewports, then report
   the route, rendered evidence, console/network result, and screenshot path.
