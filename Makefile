# Front door. The real work happens in pytest - see tb/_harness.py.
#
#   make test      every module
#   make lint      verilator lint over rtl/
#   make waves     same as test, but dumps an FST per run
#   make lesson    the onboarding lesson still passes

RTL_DIRS := $(shell find rtl -type d 2>/dev/null)
LINT_INC := $(addprefix -y ,$(RTL_DIRS))

.PHONY: test lint waves lesson clean

test:
	pytest tb/

lint:
	@for f in $$(find rtl -name '*.sv'); do \
	  echo "lint $$f"; \
	  verilator --lint-only -Wall $(LINT_INC) "$$f" || exit 1; \
	done

waves:
	pytest tb/ --waves

lesson:
	$(MAKE) -C onload/hardware solution

clean:
	rm -rf sim_build .pytest_cache
