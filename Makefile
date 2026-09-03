# Shortcuts. Everything works the same typing the commands by hand.
VENV := .venv/bin

.PHONY: install lint types test build serve run json csv clean browser

install:            ## create the environment and install everything
	uv venv --python 3.12 .venv
	uv pip install --python $(VENV)/python -e ".[dev]"
	$(VENV)/python -m playwright install chromium
	npm install

lint:               ## unused imports, undefined names, import order
	$(VENV)/ruff check .

types:              ## the payload contract, compiled
	npm run typecheck

test: lint types    ## lint, typecheck, then the whole suite
	$(VENV)/python -m pytest

build:              ## run the pipeline and write docs/
	$(VENV)/python build.py

serve: build        ## build, then serve the page
	$(VENV)/python -m http.server -d docs 8000

run:                ## console analysis of both profiles
	$(VENV)/python -m analysis.run

json:               ## the same analysis as JSON
	$(VENV)/python -m analysis.run --format json

csv:                ## dump the daily and weekly frames into out/
	$(VENV)/python -m analysis.run --csv out

clean:
	rm -rf .pytest_cache out **/__pycache__

browser:            ## drive the built page in Chromium and report
	@for f in tests/browser/check_*.py; do echo "--- $$f"; $(VENV)/python $$f; done
