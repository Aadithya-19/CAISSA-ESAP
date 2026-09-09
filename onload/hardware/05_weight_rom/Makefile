MODULE   := test_weight_rom
TOPLEVEL := weight_rom
DEPTH    ?= 256
WIDTH    ?= 8
COMPILE_ARGS += -GDEPTH=$(DEPTH) -GWIDTH=$(WIDTH)
export DEPTH WIDTH        # the testbench reads them too
include ../common.mk

# weights.hex has to match the parameters or $readmemh either overruns the
# array or truncates every value. Regenerate it before each run.
sim solution: weights
.PHONY: weights
weights:
	@python3 gen_weights.py $(DEPTH) $(WIDTH) > weights.hex
