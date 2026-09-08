# Shared by every lesson. Each lesson's Makefile sets MODULE/TOPLEVEL then
# includes this. You should not need to edit it.
SIM ?= verilator
TOPLEVEL_LANG ?= verilog   # cocotb's VPI switch, not the dialect. RTL stays .sv
SOLUTION ?= 0

ifeq ($(SOLUTION),1)
  VARIANT := solution
  VERILOG_SOURCES := $(CURDIR)/solution/$(TOPLEVEL).sv
else
  VARIANT := yours
  VERILOG_SOURCES := $(CURDIR)/$(TOPLEVEL).sv
endif

# Build dir is keyed on the variant AND the parameters. Both matter:
# a shared dir meant `make solution` left a binary behind that the next
# plain `make` reused, so an unfilled module passed. The parameter half
# is the same trap - `make N=8` would rerun the N=64 build.
PARAM_TAG := $(shell echo '$(COMPILE_ARGS)' | tr -cd 'A-Za-z0-9=' | tr '=' '-')
SIM_BUILD := sim_build/$(VARIANT)$(if $(PARAM_TAG),_$(PARAM_TAG),)

# unreset registers read 0 in verilator, so a missing reset slips through
EXTRA_ARGS += --x-assign unique --x-initial unique
EXTRA_ARGS += -Wall -Wno-UNUSEDSIGNAL -Wno-UNUSEDPARAM

ifeq ($(WAVES),1)
  EXTRA_ARGS += --trace-fst --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: solution waves
solution:
	@$(MAKE) SOLUTION=1 sim
waves:
	@$(MAKE) WAVES=1 sim
