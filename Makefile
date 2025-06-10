# OpenUI + CrewAI + Gemini Integration Makefile

# Default Python and UV commands
PYTHON := python
UV := uv

# Default values
REQUIREMENTS := Create a beautiful user profile card with avatar, name, title, bio, and action buttons. Include hover animations and professional icons.
ITERATIONS := 2
OUTPUT := component_result.json

.PHONY: help setup test test-apis demo clean install deps

# Default target
help:
	@echo "🎨 OpenUI + CrewAI + Gemini Component Creator"
	@echo "============================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make setup          - Complete setup (install deps + get cookies)"
	@echo "  make simple         - Quick end-to-end test + preview (2 iterations, ~120s)"
	@echo "  make demo           - Full end-to-end demo + preview (2 iterations, ~120sec)"
	@echo "  make pure-demo      - Demo with PURE framework analysis"
	@echo "  make test           - Run all tests"
	@echo "  make test-apis      - Test OpenUI and Gemini API connections"
	@echo "  make preview        - Generate HTML preview from existing results"
	@echo "  make clean          - Clean generated files"
	@echo ""
	@echo "Component creation (with Heroicons + Framer Motion):"
	@echo "  make create         - Create component with default requirements"
	@echo "  make button         - Create animated button component"
	@echo "  make card           - Create animated user profile card"
	@echo "  make toggle         - Create animated toggle switch"
	@echo "  make table          - Create animated data table component"
	@echo ""
	@echo "Custom creation:"
	@echo "  make create REQUIREMENTS='Your requirements here' ITERATIONS=3"
	@echo ""
	@echo "Framework options:"
	@echo "  --framework=pure    - Use PURE framework (Purposeful, Usable, Readable, Extensible)"
	@echo "  --framework=standard - Use standard quality analysis (default)"
	@echo "  make pure-button    - Create button with PURE framework"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - OpenUI running at localhost:7878"
	@echo "  - Valid Gemini API key"
	@echo "  - Python 3.8+ and uv installed"
	@echo "  - Node.js for @heroicons/react and framer-motion"

# Complete setup
setup: install get-cookies
	@echo "✅ Setup complete! Ready to create components."

# Install dependencies
install:
	@echo "📦 Installing Python dependencies with uv..."
	$(UV) sync
	@echo "📦 Installing Node.js dependencies..."
	npm install

# Alternative dependency installation
deps:
	@echo "📦 Installing/updating dependencies..."
	$(UV) add crewai google-generativeai requests selenium sseclient-py
	npm install @heroicons/react framer-motion

# Get authentication cookies from OpenUI
get-cookies:
	@echo "🍪 Getting authentication cookies from OpenUI..."
	$(PYTHON) get_openui_cookie.py

# Test all components
test: test-apis test-gemini test-openui

# Test API connections
test-apis:
	@echo "🔌 Testing API connections..."
	@echo "Testing OpenUI API..."
	$(PYTHON) test_openui_api.py
	@echo "Testing Gemini API..."
	$(PYTHON) gemini_client.py

# Test OpenUI API only
test-openui:
	@echo "🎯 Testing OpenUI API..."
	$(PYTHON) test_openui_api.py

# Test Gemini API only
test-gemini:
	@echo "🧠 Testing Gemini API..."
	$(PYTHON) gemini_client.py

# Test CrewAI agents (short version)
test-crew:
	@echo "🤖 Testing CrewAI agents..."
	timeout 60 $(PYTHON) crew_agents.py || echo "CrewAI test completed (may have timed out)"

# END-TO-END DEMO - Main command for testing
demo:
	@echo "🚀 Running end-to-end demo..."
	@echo "Requirements: $(REQUIREMENTS)"
	@echo "Iterations: $(ITERATIONS)"
	@echo "Output: $(OUTPUT)"
	@echo ""
	$(PYTHON) main.py -r '$(REQUIREMENTS)' -i $(ITERATIONS) -o $(OUTPUT)
	@echo ""
	@echo "📋 Demo completed! Check $(OUTPUT) for full results."
	@if [ -f $(OUTPUT) ]; then \
		echo "📊 Results summary:"; \
		grep -E '"(final_score|iterations)"' $(OUTPUT) || echo "Results file created"; \
		echo ""; \
		echo "🎨 Generating interactive preview..."; \
		$(PYTHON) unified_unified_preview_generator.py $(OUTPUT) preview.html; \
		echo ""; \
		echo "🌐 Open preview.html in your browser to interact with the component!"; \
		which open >/dev/null && open preview.html || echo "   Or run: open preview.html"; \
	fi

# PURE Framework demo
pure-demo:
	@echo "🎯 Running PURE framework demo..."
	@echo "Framework: PURE (Purposeful, Usable, Readable, Extensible)"
	@echo "Requirements: $(REQUIREMENTS)"
	@echo "Iterations: $(ITERATIONS)"
	@echo ""
	$(PYTHON) main.py -r '$(REQUIREMENTS)' -i $(ITERATIONS) --pure -o pure_result.json
	@echo ""
	@echo "📋 PURE demo completed! Check pure_result.json for results."
	@if [ -f pure_result.json ]; then \
		echo "🎨 Generating interactive preview..."; \
		$(PYTHON) unified_preview_generator.py pure_result.json pure_preview.html; \
		echo "🌐 Opening PURE framework preview..."; \
		which open >/dev/null && open pure_preview.html || echo "   Run: open pure_preview.html"; \
	fi

# Quick component creation with default settings
create:
	@echo "🎨 Creating component..."
	$(PYTHON) main.py -r '$(REQUIREMENTS)' -i $(ITERATIONS) -o $(OUTPUT)
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py $(OUTPUT) create_preview.html
	@echo "🌐 Opening component preview in browser..."
	@which open >/dev/null && open create_preview.html || echo "   Run: open create_preview.html"

# Predefined component types with animations and professional icons
button:
	@echo "🔘 Creating animated button component..."
	$(PYTHON) main.py -r 'Create a stunning button component with multiple variants (primary, secondary, danger), loading states, Heroicons, and smooth Framer Motion animations. Include scale and color transitions on hover/tap.' -i 2 -o button_result.json
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py button_result.json button_preview.html
	@echo "🌐 Opening button preview in browser..."
	@which open >/dev/null && open button_preview.html || echo "   Run: open button_preview.html"

card:
	@echo "🃏 Creating animated user profile card..."
	$(PYTHON) main.py -r 'Create a beautiful user profile card with avatar, name, title, bio, Heroicons for social links, follow button with Framer Motion hover effects. Include lift animations and smooth transitions.' -i 2 -o card_result.json
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py card_result.json card_preview.html
	@echo "🌐 Opening card preview in browser..."
	@which open >/dev/null && open card_preview.html || echo "   Run: open card_preview.html"

toggle:
	@echo "🔀 Creating animated toggle switch..."
	$(PYTHON) main.py -r 'Create a sleek toggle switch with Framer Motion spring animations, Heroicons for states, smooth color transitions, keyboard support, and proper accessibility. Include satisfying haptic-like motion.' -i 2 -o toggle_result.json
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py toggle_result.json toggle_preview.html
	@echo "🌐 Opening toggle preview in browser..."
	@which open >/dev/null && open toggle_preview.html || echo "   Run: open toggle_preview.html"

table:
	@echo "📊 Creating animated data table..."
	$(PYTHON) main.py -r 'Create a data table with sortable columns, pagination, Heroicons for sorting/actions, and Framer Motion animations. Include row hover effects, smooth sorting transitions, and loading states.' -i 2 -o table_result.json
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py table_result.json table_preview.html
	@echo "🌐 Opening table preview in browser..."
	@which open >/dev/null && open table_preview.html || echo "   Run: open table_preview.html"

# PURE Framework examples
pure-button:
	@echo "🎯 Creating animated button with PURE framework..."
	@echo "Note: Make sure GEMINI_API_KEY is set in your environment"
	$(PYTHON) main.py -r 'Create a modern button component with Heroicons, Framer Motion animations, multiple variants, loading states, and accessibility features' --pure -i 2 -o pure_button_result.json
	$(PYTHON) unified_preview_generator.py pure_button_result.json pure_button_preview.html
	@which open >/dev/null && open pure_button_preview.html || echo "   Run: open pure_button_preview.html"

pure-card:
	@echo "🎯 Creating animated card with PURE framework..."
	$(PYTHON) main.py -r 'Create a user profile card component with Heroicons, Framer Motion hover effects, avatar, content, and interactive actions' --pure -i 2 -o pure_card_result.json
	$(PYTHON) unified_preview_generator.py pure_card_result.json pure_card_preview.html
	@which open >/dev/null && open pure_card_preview.html || echo "   Run: open pure_card_preview.html"

# Advanced animated examples
modal:
	@echo "🪟 Creating animated modal component..."
	$(PYTHON) main.py -r "Create a flexible modal with Framer Motion entrance/exit animations, Heroicons for close button, backdrop blur, keyboard escape, focus management, and portal rendering. Include slide-in and fade effects." -i 2 -o modal_result.json
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py modal_result.json modal_preview.html
	@echo "🌐 Opening modal preview in browser..."
	@which open >/dev/null && open modal_preview.html || echo "   Run: open modal_preview.html"

form:
	@echo "📝 Creating animated form component..."
	$(PYTHON) main.py -r "Create a comprehensive form with Framer Motion field animations, Heroicons for validation states, smooth error transitions, different input types, submit states, and accessibility. Include focus animations and loading states." -i 2 -o form_result.json
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py form_result.json form_preview.html
	@echo "🌐 Opening form preview in browser..."
	@which open >/dev/null && open form_preview.html || echo "   Run: open form_preview.html"

# Development helpers
quick-test:
	@echo "⚡ Quick test with animated component..."
	$(PYTHON) main.py -r 'Create a simple button with Heroicons and Framer Motion hover animation' -i 1 -o quick_test.json

# Simple test that should work immediately
simple:
	@echo "🔥 Running simple animated end-to-end test..."
	$(PYTHON) main.py -r 'Create a beautiful button with Heroicons and smooth Framer Motion animations' -i 2 -o simple_result.json
	@echo ""
	@echo "🎨 Generating interactive preview..."
	$(PYTHON) unified_preview_generator.py simple_result.json simple_preview.html
	@echo ""
	@echo "🌐 Opening preview in browser..."
	@which open >/dev/null && open simple_preview.html || echo "   Run: open simple_preview.html"

# Generate preview from existing results
preview:
	@if [ -f $(OUTPUT) ]; then \
		echo "🎨 Generating interactive preview from $(OUTPUT)..."; \
		$(PYTHON) unified_unified_preview_generator.py $(OUTPUT) preview.html; \
		echo "🌐 Opening preview..."; \
		which open >/dev/null && open preview.html || echo "   Run: open preview.html"; \
	else \
		echo "❌ No results file found at $(OUTPUT)"; \
		echo "   Run 'make demo' or 'make simple' first"; \
	fi

# View results
show-results:
	@if [ -f $(OUTPUT) ]; then \
		echo "📋 Component Results:"; \
		echo "=================="; \
		cat $(OUTPUT) | jq -r '.component_code' 2>/dev/null || cat $(OUTPUT); \
	else \
		echo "❌ No results file found at $(OUTPUT)"; \
	fi

# View latest component code only
show-component:
	@if [ -f $(OUTPUT) ]; then \
		echo "📋 Generated Component Code:"; \
		echo "============================"; \
		cat $(OUTPUT) | jq -r '.component_code' 2>/dev/null | head -50; \
	else \
		echo "❌ No results file found at $(OUTPUT)"; \
	fi

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -f *.json
	rm -f *.log
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	@echo "✅ Cleanup complete"

# Health check - verify everything is working
health-check:
	@echo "🏥 Running health check..."
	@echo "Checking OpenUI connection..."
	@curl -s http://localhost:7878 > /dev/null && echo "✅ OpenUI is running" || echo "❌ OpenUI not accessible"
	@echo "Checking Python dependencies..."
	@$(PYTHON) -c "import crewai, google.generativeai, requests, selenium; print('✅ All Python dependencies installed')" 2>/dev/null || echo "❌ Missing Python dependencies"
	@echo "Checking Node.js dependencies..."
	@[ -d node_modules ] && echo "✅ Node.js dependencies installed" || echo "❌ Missing Node.js dependencies (run npm install)"
	@echo "Checking cookie file..."
	@[ -f openui_cookies.json ] && echo "✅ Cookies file exists" || echo "❌ No cookies file (run make get-cookies)"

# Development mode - watch for changes (requires entr)
dev:
	@echo "👀 Development mode - watching for changes..."
	@which entr > /dev/null && find . -name "*.py" | entr -r make quick-test || echo "Install 'entr' for file watching: brew install entr"

# Benchmark performance
benchmark:
	@echo "📈 Running performance benchmark..."
	@time $(PYTHON) main.py -r "Create a simple span element" -i 1 -o benchmark.json
	@echo "Benchmark complete"

# Show project structure
tree:
	@echo "📁 Project structure:"
	@tree -I '__pycache__|.venv|*.json|uv.lock' . || ls -la

# Export results as markdown
export-md:
	@if [ -f $(OUTPUT) ]; then \
		echo "# Generated Component Result" > result.md; \
		echo "" >> result.md; \
		echo "\`\`\`jsx" >> result.md; \
		cat $(OUTPUT) | jq -r '.component_code' >> result.md 2>/dev/null; \
		echo "\`\`\`" >> result.md; \
		echo "📄 Results exported to result.md"; \
	else \
		echo "❌ No results file found"; \
	fi