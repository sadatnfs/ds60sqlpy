PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: help setup generate check lab mcp app docker docker-stop docker-status
help:
	@echo "setup: install learner environment; lab: open coding lab; app: build native executable"
	@echo "generate: refresh catalog/readers/reports; check: validate; docker: build browser lab"

setup:
	bash scripts/setup.sh

generate:
	$(PYTHON) scripts/build_catalog.py
	$(PYTHON) scripts/audit_practice.py --write-report
	$(PYTHON) scripts/audit_lesson_depth.py --write-report
	$(PYTHON) scripts/build_course_guide.py
	$(PYTHON) scripts/build_lesson_readers.py

check:
	$(PYTHON) scripts/course.py validate
	$(PYTHON) -m pytest

lab:
	$(PYTHON) scripts/learning_lab.py

mcp:
	@$(PYTHON) scripts/mcp_server.py --repo "$(CURDIR)"

app: generate
	$(PYTHON) scripts/build_app.py

docker:
	bash scripts/docker_lab.sh start --build

docker-stop:
	bash scripts/docker_lab.sh stop

docker-status:
	bash scripts/docker_lab.sh status
