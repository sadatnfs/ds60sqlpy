PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TEST_WORKERS ?= 4

.PHONY: help setup generate format format-check lint check test test-serial testserial serve mcp starter docker docker-stop docker-status modules-check classroom classroom-build classroom-start classroom-stop
help:
	@echo "classroom: resume saved containers; build only missing images (or run ./classroom)"
	@echo "Windows: run in the WSL 2 Ubuntu shell with Docker integration enabled"
	@echo "classroom-build: build selected updates; classroom-start: strict no-build resume; classroom-stop: pause"
	@echo "./classroom --rebuild: install source updates; --all: select all ordinary workers"
	@echo "starter: package the complete Docker source ZIP for every supported host"
	@echo "setup: install the Linux contributor environment; learners only need Docker"
	@echo "serve: run the contributor classroom on loopback; mcp: start the optional tutor adapter"
	@echo "generate: refresh catalog/readers/reports; check: validate source and tests"
	@echo "format: style maintained sources with Docker; format-check: check without changing sources"
	@echo "lint: read-only static source checks using the same Docker toolchain"
	@echo "test: grouped parallel suite (TEST_WORKERS=4); test-serial: serial debugging"

setup:
	bash scripts/setup.sh

generate:
	$(PYTHON) scripts/normalize_lesson_prose.py --write
	$(PYTHON) scripts/build_catalog.py
	$(PYTHON) scripts/audit_practice.py --write-report
	$(PYTHON) scripts/audit_lesson_depth.py --write-report
	$(PYTHON) accomplishments/index.py build --repo .
	$(PYTHON) scripts/build_course_guide.py
	$(PYTHON) scripts/compile_lesson_tex.py
	$(PYTHON) scripts/build_lesson_readers.py

format:
	./scripts/format-repo

format-check:
	./scripts/format-repo --check

lint:
	./scripts/lint-repo

check: format-check lint
	$(PYTHON) scripts/check_public_release.py
	$(PYTHON) scripts/check_repository_guidance.py
	$(PYTHON) scripts/normalize_lesson_prose.py
	$(PYTHON) scripts/compile_lesson_tex.py --check
	$(PYTHON) scripts/check_content_rendering.py
	$(PYTHON) scripts/check_published_links.py
	$(PYTHON) accomplishments/index.py check --repo .
	DS60_INDEX_REPO="$(CURDIR)" $(PYTHON) -m unittest -v accomplishments/test_index.py
	$(PYTHON) scripts/course.py validate
	$(MAKE) test

test:
	$(PYTHON) -m pytest -n $(TEST_WORKERS) --dist loadgroup

test-serial:
	$(PYTHON) -m pytest -n 0

testserial: test-serial

serve:
	$(PYTHON) scripts/course.py serve

starter: generate
	$(PYTHON) scripts/build_starter.py

mcp:
	@$(PYTHON) scripts/mcp_server.py --repo "$(CURDIR)"

docker:
	bash classroom

docker-stop:
	bash classroom stop

docker-status:
	bash classroom status

modules-check:
	$(PYTHON) scripts/check_modules.py
	node scripts/check_classroom_ui.mjs

# Empty reuses the saved selection; a new project defaults to all ordinary profiles.
CLASSROOM_PROFILES ?=
CLASSROOM_FLAGS = $(foreach profile,$(CLASSROOM_PROFILES),--profile $(profile))

classroom-build:
	bash classroom build $(CLASSROOM_FLAGS)

classroom-start:
	bash classroom --no-build $(CLASSROOM_FLAGS)

classroom-stop:
	bash classroom stop

classroom:
	bash classroom $(CLASSROOM_FLAGS)
