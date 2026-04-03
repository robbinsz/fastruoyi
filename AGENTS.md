# Repository Guidelines

## Project Structure & Module Organization
This repository is split by runtime surface. `ruoyi-fastapi-backend` contains the FastAPI service, shared config, Alembic migrations, SQL assets, and business modules such as `module_admin`, `module_ai`, and `module_generator`. `ruoyi-fastapi-frontend/src` holds the Vue 3 admin UI, organized by `api`, `components`, `router`, `store`, and `views`. `ruoyi-fastapi-app/src` contains the uni-app mobile client, with pages under `src/pages`. End-to-end coverage lives in `ruoyi-fastapi-test`, grouped by feature areas like `system/`, `monitor/`, and `tool/`.

## Build, Test, and Development Commands
Run commands from the relevant module directory.

- Admin frontend: `npm install`, `npm run dev`, `npm run build:prod`
- Mobile app: `pnpm install`, `pnpm dev:h5`, `pnpm dev:mp-weixin`
- Backend: `pip install -r requirements.txt`, `python app.py --env=dev`
- E2E tests: in `ruoyi-fastapi-test`, run `pip install -r requirements.txt`, `playwright install`, then `pytest -v`
- Python quality checks: `ruff check ruoyi-fastapi-backend ruoyi-fastapi-test` and `ruff format ruoyi-fastapi-backend ruoyi-fastapi-test --check`

Use the Docker test compose files in `ruoyi-fastapi-test/` when you need a disposable MySQL or PostgreSQL test stack.

## Coding Style & Naming Conventions
Python targets 3.10 and follows Ruff rules with a 120-character line length and single quotes. Keep backend modules aligned with the existing layered pattern: `controller`, `service`, `dao`, `entity`. Test files use `test_*.py`. The uni-app package includes an `.editorconfig` that sets 2-space indentation, UTF-8, and LF endings; match that style in frontend changes as well. Preserve existing directory naming and keep new files feature-oriented rather than generic.

## Testing Guidelines
Prefer Playwright + `pytest` coverage for user-facing behavior, especially for admin flows already mirrored in `ruoyi-fastapi-test`. Add or extend tests near the affected domain, for example `system/test_user_management.py`. For backend-only changes, at minimum run Ruff checks and the relevant E2E path if the API affects UI workflows.

## Commit & Pull Request Guidelines
Recent history uses short, typed commit subjects such as `fix: ...`, `perf: ...`, `docs: ...`, and `chore: ...`. Follow that pattern and keep the subject action-oriented. Pull requests should describe the affected module(s), list the commands used for validation, link the related issue when available, and include screenshots for visible UI changes.
