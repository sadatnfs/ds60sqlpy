PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TEST_WORKERS ?= 4
MODULE_PROFILES ?= python-core,cpp20

.PHONY: help setup generate journey-preview check test test-serial testserial lab mcp app windows-starter docker docker-stop docker-status modules-build modules-start modules-stop modules-check classroom classroom-build classroom-start classroom-stop
help:
	@echo "setup: install learner environment; lab: open coding lab; app: build native executable"
	@echo "generate: refresh catalog/readers/reports; check: validate; docker: build and start lab"
	@echo "windows-starter: package the complete double-click Windows starter ZIP"
	@echo "test: grouped parallel suite (TEST_WORKERS=4); test-serial: serial debugging"
	@echo "journey-preview: validate five planned tracks and rebuild their offline teaching preview"
	@echo "modules-build/start/stop: optional host-folder labs (MODULE_PROFILES=python-core,cpp20)"
	@echo "classroom-build/start/stop: Docker-only labs with persistent local volumes"

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

journey-preview:
	$(PYTHON) scripts/build_journey_preview.py

check:
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

# Empty means all ordinary profiles, as defined once in the shared launcher.
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
