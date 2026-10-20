# SPDX-License-Identifier: Apache-2.0 OR MIT
# nodespec task runner

set dotenv-load := false

# Default: show available recipes
default:
    @just --list

# Install dependencies and set up environment
setup:
    uv sync

# Format code (mutates working tree — use locally)
fmt:
    uv run ruff format .

# Verify formatting (non-mutating — use in CI)
fmt-check:
    uv run ruff format --check .

# Run linters
lint:
    uv run ruff check .

# Format + lint (non-mutating — safe for CI)
check: fmt-check lint

# Run everything under tests/: the checker, the case runner, the CLI and the
# reference/ import boundary. `--exact` so the environment is the lockfile's
# and nothing a previous command installed.
test:
    uv run --exact pytest -q

# A conformance case tree against the reference checker. With no tree at
# conformance/cases it says so and exits 0.
conform *ARGS:
    uv run --exact python conformance/run_cases.py {{ARGS}}

# The mutation gate: every mutant of the checker must be killed by a test
mutants:
    uv run --exact python conformance/mutants.py

# Check files against the profile
run *ARGS:
    uv run python -m nodespec check {{ARGS}}

# Remove build artifacts
clean:
    rm -rf .pytest_cache .ruff_cache dist build **/__pycache__
