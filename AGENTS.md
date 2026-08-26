# AGENTS.md - Agent Instructions and Rules

## Project Overview
- **Name**: MeitavAlternateView
- **Purpose**: Web application providing an alternative view for Meitav Dash financial portfolios.
- **Tech Stack**: Python 3.12+, FastAPI, Uvicorn, Pandas, Requests / curl-cffi, Pydantic, Bootstrap 5 UI.

## Local Overrides Priority (CRITICAL)
If `AGENTS.local.md` exists in the workspace root, its rules and instructions MUST take precedence and override any conflicting directives in this file (`AGENTS.md`). The agent must always check for and respect `AGENTS.local.md`.

## Code Quality & Standards
- **Typing**: Use strict typing with mypy (configured to use strict settings).
- **Linting & Formatting**: Use Ruff for both linting and formatting.
- **Concurrency**: Be aware of async/thread-safety considerations when working with FastAPI and Pandas.

## Development Workflow
1. **Install dependencies**:
   ```bash
   uv sync
   ```
2. **Run the application**:
   ```bash
   uv run meitav_view
   ```
3. **Linting**:
   ```bash
   uv run ruff check src --fix
   ```
4. **Formatting**:
   ```bash
   uv run ruff format src
   ```
5. **Type Checking**:
   ```bash
   uv run mypy src
   ```
6. **Running Tests**:
   ```bash
   uv run pytest
   ```

**Note**: Always run tests and linters before completing tasks.

## UI
The frontend codebase is located in `ui/` using Vanilla JS, Bootstrap 5, Bootstrap Table, Chart.js, and FontAwesome.

### UI Build Workflow
To install dependencies and build UI assets:
```bash
cd ui && npm install && npm run build
```
Or run the build script directly:
```bash
./ui/build.sh
```
This builds and copies compiled static assets into `src/meitav_view/static/`.

## Style, Docstrings & Comments
- **High-Level Docstrings**: Write clear, high-level only docstrings for all public modules, classes, and functions.
- **No Implementation/Task Details in Comments**: Do NOT add task-specific notes, issue tracker references, or redundant step-by-step implementation details in comments or docstrings.
- **Type Signatures**: Use explicit type annotations everywhere.
- **Error Handling & Modularity**: Implement proper error handling and maintain modular, testable code.

## Project Structure
```
src/meitav_view/
  - app.py
  - viewer.py
  - healthcheck.py
  - model/
  - static/
  - utils/

ui/
  - src/
  - build.sh
  - package.json

tests/
```
