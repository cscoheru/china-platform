# CEGR — Makefile
# Per reviews/86 §NOW (Stage 1 / S1.11).
# Provides discoverable entry points for Great Expectations data-contract work.

.PHONY: help ge-check ge-docs ge-suite-% ge-test ge-list

GE_DIR := ge
GE_RUN := $(GE_DIR)/scripts/ge_run.sh

help: ## Show this help message
	@echo "CEGR — make targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

ge-check: ## Run all 5 GE suites via CI checkpoint (docs/25 §8)
	$(GE_RUN) check

ge-docs: ## Build GE Data Docs HTML
	$(GE_RUN) --docs

ge-suite-%: ## Run a single suite (dev loop) — e.g. make ge-suite-d4
	$(GE_RUN) --suite d$*

ge-test: ## Run pytest suite for ge/ (≥19 tests per reviews/86)
	$(VENV_PY) -m pytest $(GE_DIR)/tests/ -v

ge-list: ## List available GE suites and checkpoints
	$(VENV_PY) -m great_expectations --v3-api suite list --dir $(GE_DIR)
	@echo "---"
	$(VENV_PY) -m great_expectations --v3-api checkpoint list --dir $(GE_DIR)