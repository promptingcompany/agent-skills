---
name: real-jobs-not-setup
applies: Apply when writing task prompts.
---

# Tasks are real jobs; the product is the means

Each task is a job a developer would hand an agent, where using the product is the natural route. Name the product, never the tool or endpoint. Pre-wire credentials and never mention them. Test setup separately from use.

**Why:** A task about configuring the product measures its setup docs. A task about doing a job measures whether agents reach for the product's own features, which is what the client needs to know.

**Pattern:**
- Write the prompt as the developer would type it: product named, outcome stated, no route.
- Put connection details in a workspace file the prompt points to, without the word key or token.
- If setup friction matters, give it its own experiment.

**Example:** 'Our accounts-payable email runs on X. Find the Acme invoice for September and save the PDF' measured search behaviour; no prompt mentioned an endpoint.
