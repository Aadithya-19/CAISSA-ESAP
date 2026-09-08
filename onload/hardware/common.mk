# Shared by every lesson. Each lesson's Makefile sets MODULE/TOPLEVEL then
# includes this. You should not need to edit it.
SIM ?= verilator
TOPLEVEL_LANG ?= verilog   # cocotb's VPI switch, not the dialect. RTL stays .sv
SOLUTION ?= 0

ifeq ($(SOLUTION),1)
  VERILOG_SOURCES := $(CURDIR)/solution/$(TOPLEVEL).sv
  SIM_BUILD := sim_build/solution
else
  VERILOG_SOURCES := $(CURDIR)/$(TOPLEVEL).sv
  SIM_BUILD := sim_build/yours
endif

# separate build dirs on purpose. sharing one meant `make solution` left a
# compiled binary behind and the next plain `make` reused it - your unfilled
# module would pass because you were running the answer.

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
