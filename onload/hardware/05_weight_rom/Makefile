MODULE   := test_weight_rom
TOPLEVEL := weight_rom
DEPTH    ?= 256
WIDTH    ?= 8
COMPILE_ARGS += -GDEPTH=$(DEPTH) -GWIDTH=$(WIDTH)
export DEPTH WIDTH        # the testbench reads them too
include ../common.mk
