PULP_APP = lab3_pipe
PULP_APP_FC_SRCS = lab3_pipe.c
PULP_APP_HOST_SRCS = lab3_pipe.c
PULP_CFLAGS = -O2 -g
# PULP GCC 7.1.1 only supports plain RV32IMC (see ../../README.md)
PULP_ARCH_CFLAGS    = -march=rv32imc -DRV_ISA_RV32
PULP_ARCH_LDFLAGS   = -march=rv32imc
PULP_ARCH_OBJDFLAGS = -Mmarch=rv32imc

include $(PULP_SDK_HOME)/install/rules/pulp_rt.mk
