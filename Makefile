SHELL := pwsh.exe

.PHONY: dev migrate downgrade test

venv := backend/venv/Scripts

dev:
	cd backend; .\venv\Scripts\uvicorn.exe app.main:app --reload

migrate:
	cd backend; .\venv\Scripts\alembic.exe revision --autogenerate -m "auto"
	cd backend; .\venv\Scripts\alembic.exe upgrade head

downgrade:
	cd backend; .\venv\Scripts\alembic.exe downgrade -1

test:
	echo "no tests yet"

