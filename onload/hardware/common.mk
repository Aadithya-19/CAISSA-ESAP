# Shared by every lesson. Each lesson's Makefile sets MODULE/TOPLEVEL then
# includes this. You should not need to edit it.
SIM ?= verilator
TOPLEVEL_LANG ?= verilog   # cocotb's VPI switch, not the dialect. RTL stays .sv
SOLUTION ?= 0

LESSON_KIND ?= rtl

ifeq ($(LESSON_KIND),tb)
  # The RTL is given; the testbench is the exercise. Same .sv either way,
  # `solution` just runs solution/<MODULE>_ref.py instead of yours. The _ref
  # suffix shows up in the results table so you can see which one ran.
  VERILOG_SOURCES := $(CURDIR)/$(TOPLEVEL).sv
  ifeq ($(SOLUTION),1)
    VARIANT := solution
    MODULE  := $(MODULE)_ref
    export PYTHONPATH := $(CURDIR)/solution:$(PYTHONPATH)
  else
    VARIANT := yours
  endif
else
  ifeq ($(SOLUTION),1)
    VARIANT := solution
    VERILOG_SOURCES := $(CURDIR)/solution/$(TOPLEVEL).sv
  else
    VARIANT := yours
    VERILOG_SOURCES := $(CURDIR)/$(TOPLEVEL).sv
  endif
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
  # VCD not FST: verilator's FST writer needs lz4 headers that the
  # conda-forge build does not ship. GTKWave reads both.
  EXTRA_ARGS += --trace --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: solution waves
solution:
	@$(MAKE) SOLUTION=1 sim
waves:
	@$(MAKE) WAVES=1 sim
