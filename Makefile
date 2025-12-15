run:
		uvicorn app.main:app --reload

lint:
		ruff check .

format:
		black .

test:
		pytest

install:
		pip3 install -r requirements.txt
