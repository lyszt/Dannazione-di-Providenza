.PHONY: build clean dev lint install help quick-build production chrome

# Default target
.DEFAULT_GOAL := help

# Variables
BUILD_DIR := dist
EXTENSION_DIR := extension_build
EXTENSION_PACKED := $(EXTENSION_DIR)/dannazione.zip
EXTENSION_UNPACKED := $(EXTENSION_DIR)/extension_unpacked
NODE_MODULES := node_modules

# CI detection
CI ?= false

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m

## help: Show this help message
help:
	@echo "$(BLUE)╔════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║          Dannazione - Build System            ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  dev                  Start development server"
	@echo ""
	@echo "$(YELLOW)Building:$(NC)"
	@echo "  install              Install dependencies"
	@echo "  clean                Remove build artifacts"
	@echo "  quick-build          Fast build"
	@echo "  build                Standard build with packaging"
	@echo "  production           Production build with optimizations"
	@echo ""
	@echo "$(YELLOW)Extension:$(NC)"
	@echo "  chrome               Run extension in Chrome/Chromium"
	@echo ""

## dev: Start development server
dev: install
	@echo "$(GREEN)Starting development server...$(NC)"
	npm run dev

## install: Install dependencies
install:
	@if [ ! -d "$(NODE_MODULES)" ] || [ "$(CI)" = "true" ] || [ package.json -nt $(NODE_MODULES) ]; then \
		echo "$(GREEN)Installing dependencies...$(NC)"; \
		npm install; \
	else \
		echo "$(YELLOW)Dependencies up to date$(NC)"; \
	fi

## clean: Remove build artifacts
clean:
	@echo "$(RED)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR) $(EXTENSION_DIR) node_modules/.cache
	@echo "$(GREEN)Clean complete$(NC)"

## quick-build: Fast build
quick-build: install
	@echo "$(GREEN)Quick build...$(NC)"
	@npm run build
	@echo "$(GREEN)Quick build complete: $(BUILD_DIR)$(NC)"

## build: Standard build with packaging
build: clean install
	@echo "$(GREEN)Building extension...$(NC)"
	@npm run build
	@$(MAKE) --no-print-directory package
	@echo "$(GREEN)Build complete: $(EXTENSION_PACKED)$(NC)"

## production: Production build
production: clean install
	@echo "$(GREEN)Production build...$(NC)"
	@NODE_ENV=production npm run build
	@$(MAKE) --no-print-directory package
	@echo "$(GREEN)Production build complete!$(NC)"
	@du -sh $(BUILD_DIR) | awk '{print "$(YELLOW)Build size: " $$1 "$(NC)"}'
	@du -sh $(EXTENSION_PACKED) | awk '{print "$(YELLOW)Extension size: " $$1 "$(NC)"}'

## chrome: Run extension in Chrome/Chromium
chrome: quick-build
	@echo "$(GREEN)Running extension in Chrome/Chromium...$(NC)"
	@npx web-ext run --source-dir=$(BUILD_DIR) --target=chromium

## package: Package the extension
package:
	@echo "$(GREEN)Packaging extension...$(NC)"
	@mkdir -p $(EXTENSION_DIR)
	@cd $(BUILD_DIR) && zip -q -r ../$(EXTENSION_PACKED) .
	@mkdir -p $(EXTENSION_UNPACKED)
	@cp -r $(BUILD_DIR)/* $(EXTENSION_UNPACKED)/
	@echo "$(GREEN)Packaged to: $(EXTENSION_PACKED)$(NC)"
