# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **intelligent React component creation system** that integrates OpenUI, CrewAI, and Google Gemini to automatically generate, analyze, and refine React components through iterative improvement workflows.

## Core Architecture

### Multi-Service Integration
- **OpenUI** (localhost:7878): Component generation via `/v1/chat/completions` with SSE streaming
- **CrewAI**: Multi-agent orchestration system with 4 specialized agents
- **Google Gemini**: Deep component analysis using either Standard or PURE framework

### Agent System Design
The system uses CrewAI to orchestrate specialized agents in `crew_agents.py`:
- **Component Designer**: Interfaces with OpenUI for initial component generation
- **Quality Analyst**: Performs quality assessment (configurable framework)
- **Test Engineer**: Generates comprehensive Jest/RTL test suites  
- **Refiner**: Iteratively improves components based on analysis feedback

### Analysis Frameworks
Two analysis approaches are available:
- **Standard Framework** (default): 6-dimension evaluation (functionality, code quality, accessibility, performance, UX, missing features)
- **PURE Framework** (optional): Structured evaluation of Purposeful, Usable, Readable, Extensible dimensions

## Essential Commands

### Setup and Prerequisites
```bash
# Complete setup (install deps + get OpenUI cookies)
make setup

# Get authentication cookies from OpenUI frontend
make get-cookies

# Verify system health (OpenUI connection, dependencies, cookies)
make health-check
```

### Component Creation
```bash
# Quick test (1 iteration, ~90 seconds)
make simple

# Full demo (2 iterations, ~3 minutes)  
make demo

# PURE framework analysis
make pure-demo

# Custom component creation
make create REQUIREMENTS='Your custom requirements' ITERATIONS=3

# Predefined components with optimized prompts
make button    # Modern button with variants, loading states, accessibility
make card      # User profile card with hover effects
make toggle    # Toggle switch with animations and keyboard support
make table     # Data table with sorting, filtering, pagination
```

### Testing and Development
```bash
# Test API connectivity
make test-apis        # Both OpenUI and Gemini
make test-openui      # OpenUI connection only
make test-gemini      # Gemini API only

# Generate interactive HTML preview from existing results
make preview

# Performance benchmarking
make benchmark
```

## Authentication and Environment

### Required Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key (never commit to repo)
- `USE_PURE_FRAMEWORK`: Optional framework selection (true/false)

### Authentication Flow
1. **OpenUI Cookies**: `get_openui_cookie.py` uses Selenium to extract session cookies from localhost:7878
2. **Cookie Storage**: Saved to `openui_cookies.json` (gitignored)
3. **API Key Loading**: Environment-based loading with fallbacks in clients

## Key Implementation Details

### SSE Streaming Handling (`openui_client.py`)
OpenUI returns streaming responses that must be parsed line-by-line:
```python
for line in response.iter_lines(decode_unicode=True):
    if line.startswith("data: "):
        data = line[6:]  # Remove "data: " prefix
```

### Framework Selection (`main.py`, `crew_agents.py`)
The system supports switching between analysis frameworks:
- CLI flags: `--pure`, `--framework=pure/standard`
- Environment variable: `USE_PURE_FRAMEWORK`
- Constructor parameter in `ComponentCreationCrew(use_pure_framework=True)`

### Score Extraction (`pure_analyst.py`)
PURE framework uses simple regex extraction for robust parsing:
```python
match = re.search(r'PURE_SCORE:\s*([0-9.]+)', analysis)
```

### Preview Generation (`preview_generator.py`)
Components are converted to vanilla JavaScript for browser demonstration with interactive HTML previews.

## Output Structure

Generated files follow consistent patterns:
- `component_result.json`: Complete analysis with code, scores, tests
- `preview.html`: Interactive component demonstration
- Framework-specific outputs: `pure_*.json`, `pure_*.html`

## Testing Strategy

The system generates and executes multiple test types:
- **Unit Tests**: Jest/React Testing Library for component behavior
- **Accessibility Tests**: ARIA compliance, keyboard navigation, screen reader support
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Timing benchmarks and resource usage

## Development Notes

### Framework Switching
When modifying framework behavior, ensure changes are made in:
1. `main.py`: CLI argument parsing
2. `crew_agents.py`: Agent initialization and analysis routing  
3. Respective analyst files: `gemini_client.py` or `pure_analyst.py`

### Adding New Component Templates
New predefined components should be added to `Makefile` with:
- Descriptive target name
- Optimized requirements prompt
- Appropriate iteration count
- Output file naming convention

### Error Handling
The system handles common failures gracefully:
- OpenUI connection issues
- Gemini API rate limits  
- SSE stream interruptions
- Score extraction failures (falls back to neutral scores)

## Security Considerations

- API keys are loaded from environment variables only
- `.env` and API key files are gitignored
- Cookie files contain session data and should not be committed
- Test functions may contain hardcoded API keys for development - these should be removed before production use