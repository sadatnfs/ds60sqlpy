PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
TEST_WORKERS ?= 4
MODULE_PROFILES ?= python-core,cpp20

.PHONY: help setup generate journey-preview check test test-serial testserial lab mcp app windows-starter docker docker-stop docker-status modules-build modules-start modules-stop modules-check
help:
	@echo "setup: install learner environment; lab: open coding lab; app: build native executable"
	@echo "generate: refresh catalog/readers/reports; check: validate; docker: build and start lab"
	@echo "windows-starter: package the complete double-click Windows starter ZIP"
	@echo "test: grouped parallel suite (TEST_WORKERS=4); test-serial: serial debugging"
	@echo "journey-preview: validate five planned tracks and rebuild their offline teaching preview"
	@echo "modules-build/start/stop: optional labs (MODULE_PROFILES=python-core,cpp20)"

setup:
	bash scripts/setup.sh

generate:
	$(PYTHON) scripts/build_catalog.py
	$(PYTHON) scripts/build_journey_preview.py
	$(PYTHON) scripts/audit_practice.py --write-report
	$(PYTHON) scripts/audit_lesson_depth.py --write-report
	$(PYTHON) scripts/build_course_guide.py
	$(PYTHON) scripts/build_lesson_readers.py

journey-preview:
	$(PYTHON) scripts/build_journey_preview.py

check:
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
	bash scripts/docker_lab.sh start --build

docker-stop:
	bash scripts/docker_lab.sh stop

docker-status:
	bash scripts/docker_lab.sh status

modules-build:
	bash scripts/module_lab.sh build --profiles "$(MODULE_PROFILES)"

modules-start:
	bash scripts/module_lab.sh start --profiles "$(MODULE_PROFILES)"

modules-stop:
	bash scripts/module_lab.sh stop --profiles "$(MODULE_PROFILES)"

modules-check:
	$(PYTHON) scripts/check_modules.py
	node scripts/check_module_ui.mjs
