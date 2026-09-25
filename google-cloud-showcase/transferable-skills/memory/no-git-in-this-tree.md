---
name: no-git-in-this-tree
description: The sibling working tree may stay file-only; git clone/commit home is public-git/agentic-security-test-sdk (2026-09-17)
metadata:
  type: project
---

The folder used to build the app (`.../micro-cosmos/agentic-security-test-sdk`) was started as a working tree without git. The GitHub-capable copy is `.../public-git/agentic-security-test-sdk`. Do not `git init` the working tree unless the owner asks. Port files to public-git and commit there (v0.0.1).
