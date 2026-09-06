SHELL = /bin/bash

# Run these inside the pixi env:  pixi shell -e rtl
#
#   make module_foo    new module + testbench (add SUB_DIR=nnue to nest it)
#   make test          run every testbench
#   make test_foo      run one
#   make waves_foo     run one, dump an FST
#   make lint          verilator over rtl/
#   make lesson        check the onboarding lesson still passes
#   make clean

SUB_DIR ?=
LINT_INC := $(addprefix -y ,$(shell find rtl -type d 2>/dev/null))

.DEFAULT_GOAL := help
.PHONY: help test waves lint lesson clean

help:
	@sed -n 's/^#   //p' Makefile

module_%:
	@bash scripts/new.sh "$*" "$(SUB_DIR)"

test:
	@pytest tb/; s=$$?; if [ $$s -eq 5 ]; then echo "no testbenches yet"; else exit $$s; fi

test_%:
	pytest tb/ -k "$*"

waves:
	pytest tb/ --waves

waves_%:
	pytest tb/ -k "$*" --waves

lint:
	@for f in $$(find rtl -name '*.sv'); do \
	  echo "lint $$f"; \
	  verilator --lint-only -Wall $(LINT_INC) "$$f" || exit 1; \
	done

lesson:
	@$(MAKE) --no-print-directory -C onload/hardware solution

clean:
	rm -rf sim_build .pytest_cache onload/hardware/sim_build
