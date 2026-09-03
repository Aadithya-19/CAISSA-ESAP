SIM ?= verilator
TOPLEVEL_LANG ?= verilog   # cocotb's VPI switch, not the dialect. RTL stays .sv
WIDTH ?= 8

MODULE   := test_stp_sr
TOPLEVEL := stp_sr

ifeq ($(MAKECMDGOALS),solution)
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
	$(MAKE) WAVES=1
	@echo "wrote dump.fst - copy it to your own machine to view"

solution: sim
