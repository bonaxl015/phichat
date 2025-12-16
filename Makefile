run:
	uvicorn app.main:app --reload

lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	black .

test:
	pytest

install:
	pip3 install -r requirements.txt
