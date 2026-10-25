.PHONY: all help test validate doctor install uninstall update clean

PYTHON ?= python3
BASH   ?= bash

help: ## Show available targets
	@echo "Aetherium OS Developer Commands:"
	@echo "  make test        - Run test suite"
	@echo "  make validate    - Validate configuration tokens and schemas"
	@echo "  make doctor      - Run Aetherium system diagnostic tool"
	@echo "  make install     - Run transactional system installer"
	@echo "  make uninstall   - Safe rollback and uninstallation"
	@echo "  make update      - Non-destructive component update"

test: ## Run test suite
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

validate: ## Validate configuration files
	$(PYTHON) core/bin/aetherium-doctor --validate-configs

doctor: ## Run system diagnostic check
	$(PYTHON) core/bin/aetherium-doctor

install: ## Run installer
	$(BASH) install.sh

uninstall: ## Safe uninstallation
	$(BASH) uninstall.sh

update: ## Update components
	$(BASH) update.sh

clean: ## Clean build and temp files
	rm -rf build/ desktop/build/ *.log .pytest_cache/
