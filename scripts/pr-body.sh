#!/usr/bin/env bash
# Print a PR description derived from a PR doc: "Left off" first, then every section from "## Goal" on, except Context.
set -euo pipefail
awk '/^## /{keep = ($0 == "## Left off")} keep' "$1"
awk '/^## /{keep = ($0 != "## Context" && $0 != "## Left off")} /^## Goal/{started = 1} started && keep' "$1"
