.PHONY: build clean dev lint test install help analyze quick-build production docs setup-python format watch

NPROC ?= $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Default target
.DEFAULT_GOAL := help

# Variables
BUILD_DIR := dist
EXTENSION_DIR := extension_build
EXTENSION_PACKED := $(EXTENSION_DIR)/dannazione-di-providenza.zip
EXTENSION_UNPACKED := $(EXTENSION_DIR)/extension_unpacked
NODE_MODULES := node_modules
STATS_DIR := stats
AGENT_HOST ?= localhost
AGENT_PORT ?= 8765

# CI detection
CI ?= false

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo "$(BLUE)╔════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║   Dannazione di Providenza - Build System     ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  dev                  Start development server with hot reload"
	@echo "  watch                Build in watch mode"
	@echo ""
	@echo "$(YELLOW)Building:$(NC)"
	@echo "  install              Install dependencies (with caching check)"
	@echo "  setup-python         Setup Python virtual environment"
	@echo "  clean                Remove all build artifacts and caches"
	@echo "  quick-build          Fast build without lint and analysis"
	@echo "  build                Standard build with linting (default)"
	@echo "  production           Production build with analysis and optimizations"
	@echo "  analyze              Build with bundle analysis only"
	@echo ""
	@echo "$(YELLOW)Quality:$(NC)"
	@echo "  lint                 Run ESLint with auto-fix"
	@echo "  lint-check           Run ESLint without auto-fix"
	@echo "  format               Format TypeScript/JavaScript files"
	@echo "  test                 Run tests"
	@echo ""
	@echo "$(YELLOW)Extension:$(NC)"
	@echo "  firefox-dev          Run extension in Firefox Developer Edition"
	@echo "  firefox              Run extension in Firefox"
	@echo ""

##@ Development

## dev: Start development server with hot reload
dev: install select-env
	@echo "$(GREEN)Starting development server...$(NC)"
	npm run dev

## watch: Build in watch mode
watch: install select-env
	@echo "$(GREEN)Starting watch mode...$(NC)"
	npm run watch

##@ Building

## install: Install dependencies (with caching check)
install:
	@if [ ! -d "$(NODE_MODULES)" ] || [ "$(CI)" = "true" ] || [ package.json -nt $(NODE_MODULES) ]; then \
		echo "$(GREEN)Installing dependencies...$(NC)"; \
		npm ci --prefer-offline --no-audit 2>/dev/null || npm install; \
	else \
		echo "$(YELLOW)Dependencies up to date$(NC)"; \
	fi

## setup-python: Setup Python virtual environment and install dependencies
setup-python:
	@echo "$(GREEN)Setting up Python environment...$(NC)"
	@if [ ! -d "../.venv" ]; then \
		echo "$(YELLOW)Creating Python virtual environment...$(NC)"; \
		cd .. && (python3 -m venv .venv || python -m venv .venv); \
	fi
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	@cd .. && . .venv/bin/activate && pip install --upgrade pip
	@cd .. && . .venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)✓ Python environment configured successfully!$(NC)"
	@echo "$(YELLOW)To activate manually: source ../.venv/bin/activate$(NC)"

## clean: Remove all build artifacts and caches
clean:
	@echo "$(RED)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR) $(EXTENSION_DIR) node_modules/.cache stats
	@echo "$(GREEN)Clean complete$(NC)"

## quick-build: Fast build without lint and analysis
quick-build: install select-env
	@echo "$(GREEN)Quick build (no lint, no analysis)...$(NC)"
	@npm run build
	@echo "$(GREEN)Quick build complete: $(BUILD_DIR)$(NC)"

## build: Standard build with linting
build: clean install select-env lint
	@echo "$(GREEN)Building extension...$(NC)"
	@npm run build
	@$(MAKE) --no-print-directory package
	@echo "$(GREEN)Build complete: $(EXTENSION_PACKED)$(NC)"

## production: Production build with analysis and optimizations
production: clean install select-env lint
	@echo "$(GREEN)Production build with bundle analysis...$(NC)"
	@ANALYZE=true npm run build
	@$(MAKE) --no-print-directory package
	@echo "$(GREEN)Production build complete!$(NC)"
	@echo "$(YELLOW)Bundle analysis: stats/bundle.html$(NC)"
	@du -sh $(BUILD_DIR) | awk '{print "$(YELLOW)Build size: " $$1 "$(NC)"}'
	@du -sh $(EXTENSION_PACKED) | awk '{print "$(YELLOW)Extension size: " $$1 "$(NC)"}'

## analyze: Build with bundle analysis only
analyze: clean install select-env
	@echo "$(GREEN)Building with bundle analysis...$(NC)"
	@ANALYZE=true npm run build
	@echo "$(GREEN)Analysis complete: stats/bundle.html$(NC)"

##@ Quality

## lint: Run ESLint with auto-fix
lint: install
	@echo "$(GREEN)Running ESLint...$(NC)"
	@npm run lint -- --fix || (echo "$(RED)Lint errors found$(NC)" && exit 1)
	@echo "$(GREEN)Lint passed$(NC)"

## lint-check: Run ESLint without auto-fix
lint-check: install
	@echo "$(GREEN)Checking code with ESLint...$(NC)"
	@npm run lint

## format: Format TypeScript/JavaScript files
format:
	@CORES=$$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4); \
	JOBS=$$((CORES / 2)); \
	if [ $$JOBS -lt 1 ]; then JOBS=1; fi; \
	echo "$(GREEN)Formatting TS/JS files with $$JOBS parallel jobs...$(NC)"; \
	find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" \) \
		-not -path "*/node_modules/*" \
		-not -path "*/dist/*" \
		-not -path "*/build/*" \
		-not -path "*/.git/*" \
	-print0 | \
	xargs -0 -n1 -P $$JOBS -I {} npx js-beautify -r "{}"

## test: Run tests
test: install
	@echo "$(GREEN)Running tests...$(NC)"
	@npm run test || echo "$(YELLOW)No tests configured yet$(NC)"

##@ Extension

## firefox-dev: Run extension in Firefox Developer Edition
firefox-dev: quick-build
	@echo "$(GREEN)Running extension in Firefox Developer Edition...$(NC)"
	@npx web-ext run --source-dir=$(BUILD_DIR) --firefox=firefoxdeveloperedition

## firefox: Run extension in Firefox
firefox: quick-build
	@echo "$(GREEN)Running extension in Firefox...$(NC)"
	@npx web-ext run --source-dir=$(BUILD_DIR)

##@ Internal

## select-env: Select agent environment (internal target)
select-env:
	@echo "$(YELLOW)╔══════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  Select Agent Environment:           ║$(NC)"
	@echo "$(YELLOW)╠══════════════════════════════════════╣$(NC)"
	@echo "$(YELLOW)║  [0] LOCAL  - localhost:8765         ║$(NC)"
	@echo "$(YELLOW)║  [1] DEV    - dev.providenza.ai      ║$(NC)"
	@echo "$(YELLOW)║  [2] PROD   - providenza.ai          ║$(NC)"
	@echo "$(YELLOW)╚══════════════════════════════════════╝$(NC)"
	@echo ""
	@read -p "Enter your choice [0/1/2]: " choice; \
	case $$choice in \
		0) \
			echo "$(GREEN)✓ Selected: LOCAL (localhost:8765)$(NC)"; \
			sed -i "s/^const AGENT_ENV = [0-9];/const AGENT_ENV = 0;/" src/config.ts 2>/dev/null || echo "const AGENT_ENV = 0;" > src/config.ts; \
			;; \
		1) \
			echo "$(GREEN)✓ Selected: DEV (dev.providenza.ai)$(NC)"; \
			sed -i "s/^const AGENT_ENV = [0-9];/const AGENT_ENV = 1;/" src/config.ts 2>/dev/null || echo "const AGENT_ENV = 1;" > src/config.ts; \
			;; \
		2) \
			echo "$(GREEN)✓ Selected: PROD (providenza.ai)$(NC)"; \
			sed -i "s/^const AGENT_ENV = [0-9];/const AGENT_ENV = 2;/" src/config.ts 2>/dev/null || echo "const AGENT_ENV = 2;" > src/config.ts; \
			;; \
		*) \
			echo "$(RED)✗ Invalid choice. Defaulting to LOCAL.$(NC)"; \
			sed -i "s/^const AGENT_ENV = [0-9];/const AGENT_ENV = 0;/" src/config.ts 2>/dev/null || echo "const AGENT_ENV = 0;" > src/config.ts; \
			;; \
	esac
	@echo ""

## package: Package the extension (internal target)
package:
	@echo "$(GREEN)Packaging extension...$(NC)"
	@mkdir -p $(EXTENSION_DIR)
	@cd $(BUILD_DIR) && zip -q -r ../$(EXTENSION_PACKED) .
	@mkdir -p $(EXTENSION_UNPACKED)
	@cp -r $(BUILD_DIR)/* $(EXTENSION_UNPACKED)/
	@echo "$(GREEN)Packaged to: $(EXTENSION_PACKED)$(NC)"
