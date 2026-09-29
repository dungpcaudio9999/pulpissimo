#!/usr/bin/env bash
# Print the version of every Lab 1 tool. Run it in a terminal and take a
# screenshot of the output, or redirect it to a file:
#   ./collect_versions.sh | tee 01_tool_versions.txt

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TOOLCHAIN="${PULP_RISCV_GCC_TOOLCHAIN:-/opt/pulp-toolchain}"
OSEDA_IMAGE="${OSEDA_IMAGE:-hpretl/iic-osic-tools:2025.12}"

section() { printf '\n===== %s =====\n' "$1"; }
run() {
  if command -v "$1" > /dev/null 2>&1; then
    "$@" 2>&1 | head -n "${LINES_MAX:-2}"
  else
    echo "NOT FOUND: $1"
  fi
}

echo "Host: $(uname -srm) | $(date -u '+%Y-%m-%d %H:%M UTC')"

section "Vivado"
run vivado -version

section "RISC-V LLVM (clang / lld)"
run clang --version
clang -print-targets 2>/dev/null | grep -E 'riscv(32|64)'
LINES_MAX=1 run ld.lld --version

section "RISC-V GCC (PULP)"
LINES_MAX=1 run "$TOOLCHAIN/bin/riscv32-unknown-elf-gcc" --version

section "OpenOCD"
LINES_MAX=1 run openocd --version

section "Bender"
run "$ROOT/utils/bin/bender" --version

section "QuestaSim"
LINES_MAX=1 run vsim -version

section "Container oseda ($OSEDA_IMAGE)"
if command -v docker > /dev/null 2>&1; then
  docker --version
  docker image inspect "$OSEDA_IMAGE" \
    --format 'image: {{index .RepoTags 0}}  id: {{.Id}}  created: {{.Created}}' 2>&1 | cut -c1-120
  docker run --rm --entrypoint bash "$OSEDA_IMAGE" -lc '
    for c in "yosys -V" "openroad -version" "verilator --version" "bender --version" \
             "klayout -v" "riscv64-unknown-elf-gcc --version"; do
      printf "  %-36s %s\n" "$c" "$($c 2>&1 | head -1)"
    done
    echo "  PDKs in /foss/pdks: $(ls /foss/pdks | tr "\n" " ")"' 2>/dev/null | grep -v '^\[INFO\]'
else
  echo "NOT FOUND: docker"
fi
