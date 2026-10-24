PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TEST_WORKERS ?= 4
MODULE_PROFILES ?= python-core,cpp20

.PHONY: help setup generate format format-check lint journey-preview check test test-serial testserial lab mcp app windows-starter docker docker-stop docker-status modules-build modules-start modules-stop modules-check classroom classroom-build classroom-start classroom-stop
help:
	@echo "classroom: resume saved containers; build only missing images (or run ./classroom)"
	@echo "Windows: run in the WSL 2 Ubuntu shell with Docker integration enabled"
	@echo "classroom-build: build selected updates; classroom-start: strict no-build resume; classroom-stop: pause"
	@echo "./classroom --rebuild: install source updates; --all: select all ordinary workers"
	@echo "windows-starter: package the portable Docker source ZIP (legacy target name)"
	@echo "setup: install the Linux contributor environment; learners only need Docker"
	@echo "generate: refresh catalog/readers/reports; check: validate source and tests"
	@echo "format: style maintained sources with Docker; format-check: check without changing sources"
	@echo "lint: read-only static source checks using the same Docker toolchain"
	@echo "test: grouped parallel suite (TEST_WORKERS=4); test-serial: serial debugging"
	@echo "journey-preview: rebuild the historical design preview"
	@echo "modules-build/start/stop: contributor host-folder labs (MODULE_PROFILES=python-core,cpp20)"
	@echo "Historical targets outside Docker release support: lab (native server), app (native executable)"

setup:
	bash scripts/setup.sh

generate:
	$(PYTHON) scripts/normalize_lesson_prose.py --write
	$(PYTHON) scripts/build_catalog.py
	$(PYTHON) scripts/build_journey_preview.py
	$(PYTHON) scripts/audit_practice.py --write-report
	$(PYTHON) scripts/audit_lesson_depth.py --write-report
	$(PYTHON) scripts/build_course_guide.py
	$(PYTHON) scripts/build_lesson_readers.py

format:
	./scripts/format-repo

format-check:
	./scripts/format-repo --check

lint:
	./scripts/lint-repo

journey-preview:
	$(PYTHON) scripts/build_journey_preview.py

check: format-check lint
	$(PYTHON) scripts/check_public_release.py
	$(PYTHON) scripts/normalize_lesson_prose.py
	$(PYTHON) scripts/check_content_rendering.py
	$(PYTHON) scripts/check_published_links.py
	$(PYTHON) scripts/course.py validate
	$(MAKE) test

test:
	$(PYTHON) -m pytest -n $(TEST_WORKERS) --dist loadgroup

test-serial:
	$(PYTHON) -m pytest -n 0

testserial: test-serial

lab:
	$(PYTHON) scripts/learning_lab.py

mcp:
	@$(PYTHON) scripts/mcp_server.py --repo "$(CURDIR)"

app: generate
	$(PYTHON) scripts/build_app.py

windows-starter: generate
	$(PYTHON) scripts/build_windows_starter.py

docker:
	bash classroom

docker-stop:
	bash classroom stop

docker-status:
	bash classroom status

modules-build:
	bash scripts/module_lab.sh build --profiles "$(MODULE_PROFILES)"

modules-start:
	bash scripts/module_lab.sh start --profiles "$(MODULE_PROFILES)"

modules-stop:
	bash scripts/module_lab.sh stop --profiles "$(MODULE_PROFILES)"

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
