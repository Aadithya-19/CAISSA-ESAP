SIM ?= verilator
TOPLEVEL_LANG ?= verilog   # cocotb's VPI switch, not the dialect. RTL stays .sv
WIDTH ?= 8
SOLUTION ?= 0

MODULE   := test_stp_sr
TOPLEVEL := stp_sr

# a variable, not a goal - cocotb re-invokes make and MAKECMDGOALS doesn't survive
ifeq ($(SOLUTION),1)
  VERILOG_SOURCES := $(CURDIR)/solution/stp_sr.sv
else
  VERILOG_SOURCES := $(CURDIR)/stp_sr.sv
endif

COMPILE_ARGS += -GWIDTH=$(WIDTH)

# unreset registers read 0 in verilator, so a missing reset slips through
EXTRA_ARGS += --x-assign unique --x-initial unique
EXTRA_ARGS += -Wall

ifeq ($(WAVES),1)
  EXTRA_ARGS += --trace-fst --trace-structs
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: lint waves solution

lint:
	verilator --lint-only -Wall -GWIDTH=$(WIDTH) $(CURDIR)/stp_sr.sv

waves:
	$(MAKE) WAVES=1 sim
	@echo "wrote dump.fst - copy it to your own machine to view"

solution:
	$(MAKE) SOLUTION=1 sim
