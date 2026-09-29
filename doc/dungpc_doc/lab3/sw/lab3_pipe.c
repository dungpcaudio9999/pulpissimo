/*
 * Lab 3 – pipeline, bus and memory-latency test for CV32E40P on PULPissimo.
 *
 * Part 1 (tasks 1-3): a short, fixed instruction sequence framed by two
 *   marker stores to MARKER_ADDR, easy to find on the data bus in the waves.
 * Part 2 (task 4): cycle counts (mcycle) of four unrolled kernels:
 *   alu  – 32 x addi               (reference, no memory access)
 *   ldi  – 32 x lw, independent    (4 destination registers, never used)
 *   ldd  – 32 x (lw + dependent add)
 *   st   – 32 x sw
 * Part 3 (task 5): one div. With the divider disabled it must trap.
 *
 * Build: -march=rv32imc (PULP GCC 7.1.1), see ../README.md.
 */
#include <stdio.h>
#include <stdint.h>

#define MARKER_ADDR 0x1C007F00u   /* unused word in L2 private bank 0 */
#define DATA_ADDR   0x1C007E00u   /* 64-byte scratch buffer for the kernels */

#define MARKER(v) (*(volatile uint32_t *)MARKER_ADDR = (v))

static inline uint32_t rdcycle(void)
{
  uint32_t c;
  __asm__ volatile("csrr %0, 0xB00" : "=r"(c));   /* mcycle */
  return c;
}

#define R4(x)  x x x x
#define R8(x)  R4(x) R4(x)
#define R32(x) R8(x) R8(x) R8(x) R8(x)

static uint32_t k_empty(void)
{
  uint32_t t0 = rdcycle();
  uint32_t t1 = rdcycle();
  return t1 - t0;
}

static uint32_t k_alu(void)
{
  uint32_t t0 = rdcycle();
  __asm__ volatile(R32("addi t0, t0, 1\n") ::: "t0");
  uint32_t t1 = rdcycle();
  return t1 - t0;
}

static uint32_t k_ld_indep(uint32_t base)
{
  uint32_t t0 = rdcycle();
  __asm__ volatile(R8("lw t0, 0(%0)\n lw t1, 4(%0)\n lw t2, 8(%0)\n lw t3, 12(%0)\n")
                   :: "r"(base) : "t0", "t1", "t2", "t3");
  uint32_t t1 = rdcycle();
  return t1 - t0;
}

static uint32_t k_ld_dep(uint32_t base)
{
  uint32_t t0 = rdcycle();
  __asm__ volatile(R32("lw t0, 0(%0)\n add t1, t1, t0\n")
                   :: "r"(base) : "t0", "t1");
  uint32_t t1 = rdcycle();
  return t1 - t0;
}

static uint32_t k_st(uint32_t base)
{
  uint32_t t0 = rdcycle();
  __asm__ volatile(R32("sw zero, 0(%0)\n") :: "r"(base) : "memory");
  uint32_t t1 = rdcycle();
  return t1 - t0;
}

int main()
{
  /* Enable mcycle/minstret (mcountinhibit = 0x320). */
  __asm__ volatile("csrw 0x320, zero");

  volatile uint32_t *buf = (volatile uint32_t *)DATA_ADDR;
  for (int i = 0; i < 16; i++) buf[i] = 0x100 + i;

  /* ---------------- Part 1: sequence to observe in the waves ---------- */
  MARKER(0xA5A50001);
  __asm__ volatile(
      "addi  t0, zero, 7      \n"   /* I1  ALU                          */
      "lw    t1, 0(%0)        \n"   /* I2  load  (followed in task 2)   */
      "add   t2, t1, t0       \n"   /* I3  uses t1 -> load-use stall    */
      "sw    t2, 4(%0)        \n"   /* I4  store (task 3)               */
      "addi  t3, zero, 3      \n"   /* I5                               */
      "div   t4, t2, t3       \n"   /* I6  divide (task 5)              */
      "addi  t5, t4, 1        \n"   /* I7  uses div result              */
      :: "r"(DATA_ADDR) : "t0", "t1", "t2", "t3", "t4", "t5", "memory");
  MARKER(0xA5A50002);

  /* ---------------- Part 2: cycle counts ------------------------------ */
  uint32_t e   = k_empty();
  uint32_t alu = k_alu()             - e;
  uint32_t ldi = k_ld_indep(DATA_ADDR) - e;
  uint32_t ldd = k_ld_dep(DATA_ADDR)   - e;
  uint32_t st  = k_st(DATA_ADDR + 32)  - e;
  printf("LAB3 empty=%d alu32=%d ldi32=%d ldd32=%d st32=%d\n",
         (int)e, (int)alu, (int)ldi, (int)ldd, (int)st);

  /* ---------------- Part 3: divider ----------------------------------- */
  volatile int a = 1000, b = 7;
  int q;
  __asm__ volatile("div %0, %1, %2" : "=r"(q) : "r"(a), "r"(b));
  printf("LAB3 div 1000/7=%d\n", q);

  return (q == 142) ? 0 : 1;
}
