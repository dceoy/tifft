# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`tifft` is a Python package for calculating technical indicators for financial trading. It provides:
- Python calculator classes for MACD, Bollinger Bands, and RSI
- Command-line interface for fetching historical data and calculating indicators
- Integration with pandas-datareader for remote data sources (FRED, etc.)

## Commands

### Development
```bash
# Install the package in development mode
pip install -e .

# Run linting (as per test workflow)
flake8 .

# Test command-line interface
tifft --version
tifft --help
```

### Testing
```bash
# Run basic commands to test functionality
tifft history DJIA SP500 NASDAQ100
tifft macd SP500
tifft bb SP500
tifft rsi SP500
```

### Building and Publishing
```bash
# Build package (standard Python packaging)
python setup.py sdist bdist_wheel

# Docker build
docker build -t tifft .
```

## Architecture

### Core Structure
- `tifft/cli.py`: Command-line interface using docopt, entry point for the package
- `tifft/datareader.py`: Data fetching and indicator calculation orchestration
- `tifft/macd.py`, `tifft/bollingerbands.py`, `tifft/rsi.py`: Calculator classes for each indicator

### Key Design Patterns
- Each indicator is implemented as a Calculator class with a `calculate()` method
- CLI commands map to functions in `datareader.py` that handle data fetching and processing
- Uses pandas DataFrames for all data manipulation
- Remote data fetching via `pandas_datareader.data.DataReader`

### Dependencies
- `docopt`: CLI argument parsing
- `pandas`: Data manipulation
- `pandas-datareader`: Financial data fetching

### Entry Points
- Console script: `tifft` (defined in setup.py)
- Python imports: `from tifft.{indicator} import {Indicator}Calculator`

## Web Search Instructions

For tasks requiring web search, always use Gemini CLI (`gemini` command) instead of the built-in web search tools (WebFetch and WebSearch).
Gemini CLI is an AI workflow tool that provides reliable web search capabilities.

### Usage

```sh
# Basic search query
gemini --sandbox --prompt "WebSearch: <query>"

# Example: Search for latest news
gemini --sandbox --prompt "WebSearch: What are the latest developments in AI?"
```

### Policy

When users request information that requires web search:

1. Use `gemini --sandbox --prompt` command via terminal
2. Parse and present the Gemini response appropriately

This ensures consistent and reliable web search results through the Gemini API.

## Code Design Principles

Follow Robert C. Martin's SOLID and Clean Code principles:

### SOLID Principles

1. **SRP (Single Responsibility)**: One reason to change per class; separate concerns (e.g., storage vs formatting vs calculation)
2. **OCP (Open/Closed)**: Open for extension, closed for modification; use polymorphism over if/else chains
3. **LSP (Liskov Substitution)**: Subtypes must be substitutable for base types without breaking expectations
4. **ISP (Interface Segregation)**: Many specific interfaces over one general; no forced unused dependencies
5. **DIP (Dependency Inversion)**: Depend on abstractions, not concretions; inject dependencies

### Clean Code Practices

- **Naming**: Intention-revealing, pronounceable, searchable names (`daysSinceLastUpdate` not `d`)
- **Functions**: Small, single-task, verb names, 0-3 args, extract complex logic
- **Classes**: Follow SRP, high cohesion, descriptive names
- **Error Handling**: Exceptions over error codes, no null returns, provide context, try-catch-finally first
- **Testing**: TDD, one assertion/test, FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely), Arrange-Act-Assert pattern
- **Code Organization**: Variables near usage, instance vars at top, public then private functions, conceptual affinity
- **Comments**: Self-documenting code preferred, explain "why" not "what", delete commented code
- **Formatting**: Consistent, vertical separation, 88-char limit, team rules override preferences
- **General**: DRY, KISS, YAGNI, Boy Scout Rule, fail fast

## Development Methodology

Follow Martin Fowler's Refactoring, Kent Beck's Tidy Code, and t_wada's TDD principles:

### Core Philosophy

- **Small, safe changes**: Tiny, reversible, testable modifications
- **Separate concerns**: Never mix features with refactoring
- **Test-driven**: Tests provide safety and drive design
- **Economic**: Only refactor when it aids immediate work

### TDD Cycle

1. **Red** → Write failing test
2. **Green** → Minimum code to pass
3. **Refactor** → Clean without changing behavior
4. **Commit** → Separate commits for features vs refactoring

### Practices

- **Before**: Create TODOs, ensure coverage, identify code smells
- **During**: Test-first, small steps, frequent tests, two hats rule
- **Refactoring**: Extract function/variable, rename, guard clauses, remove dead code, normalize symmetries
- **TDD Strategies**: Fake it, obvious implementation, triangulation

### When to Apply

- Rule of Three (3rd duplication)
- Preparatory (before features)
- Comprehension (as understanding grows)
- Opportunistic (daily improvements)

### Key Rules

- One assertion per test
- Separate refactoring commits
- Delete redundant tests
- Human-readable code first

> "Make the change easy, then make the easy change." - Kent Beck
