#!/usr/bin/env bash
# Print a PR description derived from a PR doc: every section from "## Goal" on, except Context.
set -euo pipefail
awk '/^## /{keep = ($0 != "## Context")} /^## Goal/{started = 1} started && keep' "$1"
