.PHONY: all help test validate doctor install uninstall update build-shell installer check clean

PYTHON ?= python3
BASH   ?= bash

help: ## Show available targets
	@echo "Aetherium OS Developer Commands:"
	@echo "  make install     - Interactive desktop product installer"
	@echo "  make update      - Authoritative updater preserving user settings"
	@echo "  make uninstall   - Safe rollback and uninstallation"
	@echo "  make build-shell - Build native C++ plugins via CMake"
	@echo "  make installer   - Build interactive C++ TUI installer binary"
	@echo "  make doctor      - Run Aetherium diagnostic health check"
	@echo "  make validate    - Validate configuration tokens and schemas"
	@echo "  make test        - Run automated test suite"
	@echo "  make check       - Syntax check all shell scripts"
	@echo "  make clean       - Remove build and temporary artifacts"

install: ## Run installer
	$(BASH) install.sh

update: ## Update components
	$(BASH) update.sh

uninstall: ## Safe uninstallation
	$(BASH) uninstall.sh

build-shell: ## Build desktop shell C++ plugins
	$(BASH) scripts/08-build-shell.sh

installer: ## Compile interactive C++ TUI binary
	cmake -B installer/build -S installer/tui -DCMAKE_BUILD_TYPE=Release
	cmake --build installer/build

doctor: ## Run system diagnostic check
	$(PYTHON) core/bin/aetherium-doctor

validate: ## Validate configuration files
	$(PYTHON) core/bin/aetherium-doctor --validate-configs

test: ## Run test suite
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

check: ## Syntax check shell scripts
	find scripts installer core -name "*.sh" -exec $(BASH) -n {} +

clean: ## Clean build and temp files
	rm -rf build/ desktop/build/ installer/build/ *.log .pytest_cache/
