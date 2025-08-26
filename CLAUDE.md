# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python educational project focused on Mars mission simulations, organized in chapters (ch1-ch5). Each chapter contains different exercises and implementations related to space mission scenarios.

## Common Development Commands

### Linting
Based on git history, this project uses flake8 for linting:
```bash
flake8 [filename.py]
```

### Running Python Scripts
Execute individual chapter scripts directly:
```bash
python ch1/main.py
python ch2/1/read_file.py
python ch3/mars_mission_computer.py
python ch4/caesar.py
python ch5/calculator.py
```

## Project Structure and Architecture

### Chapter Organization
- **ch1**: Log analysis system - Reads mission computer logs, filters danger keywords, converts to JSON
- **ch2**: Data processing - Binary/CSV file handling, Mars base inventory management
- **ch3**: Mission computer simulation - Multi-process sensor monitoring with configurable settings via `setting.txt`
- **ch4**: Security/encryption exercises - Caesar cipher implementation, password handling
- **ch5**: PyQt5 Calculator - GUI application with standard calculator operations

### Key Architectural Patterns

1. **Log Processing Pattern (ch1/main.py)**:
   - Read raw logs → Parse into structured data → Filter by criteria → Sort chronologically → Export to JSON
   - Danger keyword filtering for critical events (explosion, leak, high temperature, oxygen issues)

2. **Sensor Simulation Architecture (ch3/mars_mission_computer.py)**:
   - `DummySensor` class generates random environmental data
   - `MissionComputer` orchestrates data collection, 5-minute averaging, and system monitoring
   - Uses multiprocessing for parallel sensor reading and system monitoring
   - Configuration via `setting.txt` controls displayed metrics

3. **GUI Application Structure (ch5/calculator.py)**:
   - Separation of concerns: `Calculator` class handles logic, `App` class manages UI
   - Event-driven architecture with Qt signal/slot connections
   - Dynamic font sizing based on display content

### Dependencies
- **PyQt5**: Required for ch5 calculator GUI
- **Standard library**: json, logging, multiprocessing, subprocess, platform, datetime, random

### Data Flow Patterns
- Files often use CSV/JSON for data interchange
- Logging to dedicated log files in `logs/` directory
- Configuration files (like `setting.txt`) control runtime behavior