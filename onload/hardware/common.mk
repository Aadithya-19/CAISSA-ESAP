# Shared by every lesson. Each lesson's Makefile sets MODULE/TOPLEVEL then
# includes this. You should not need to edit it.
SIM ?= verilator
TOPLEVEL_LANG ?= verilog   # cocotb's VPI switch, not the dialect. RTL stays .sv
SOLUTION ?= 0

ifeq ($(SOLUTION),1)
  VERILOG_SOURCES := $(CURDIR)/solution/$(TOPLEVEL).sv
else
  VERILOG_SOURCES := $(CURDIR)/$(TOPLEVEL).sv
endif

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
