# CAISSA
#
#   make new NAME=mac_array        scaffold a module + its testbench
#   make new NAME=foo DIR=nnue     same, under rtl/nnue/
#   make test                      run everything
#   make test NAME=mac_array       run one module
#   make waves NAME=mac_array      same, dump an FST
#   make lint                      verilator lint over rtl/
#   make lesson                    check the onboarding lesson still passes

NAME ?=
DIR  ?=

RTL_DIRS := $(shell find rtl -type d 2>/dev/null)
LINT_INC := $(addprefix -y ,$(RTL_DIRS))
SELECT   := $(if $(NAME),-k $(NAME),)

.PHONY: new test waves lint lesson clean

new:
	@scripts/new.sh "$(NAME)" "$(DIR)"

test:
	pytest tb/ $(SELECT)

waves:
	pytest tb/ $(SELECT) --waves

lint:
	@for f in $$(find rtl -name '*.sv'); do \
	  echo "lint $$f"; \
	  verilator --lint-only -Wall $(LINT_INC) "$$f" || exit 1; \
	done

lesson:
	$(MAKE) -C onload/hardware solution

clean:
	rm -rf sim_build .pytest_cache
