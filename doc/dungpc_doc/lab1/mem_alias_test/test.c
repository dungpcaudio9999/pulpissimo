/* Lab 1 step 5: check memory-map aliasing seen in the RTL.
 * - L2 interleaved: decoded 0x1C010000-0x1C090000 (512 KiB),
 *   but only 4 banks x 64 KiB = 256 KiB exist.
 * - Boot ROM: decoded 0x1A000000-0x1A040000 (256 KiB), only 8 KiB exist.
 */
#include <stdio.h>
#include <stdint.h>

#define RD(a)    (*(volatile uint32_t *)(a))
#define WR(a, v) (*(volatile uint32_t *)(a) = (v))

int main()
{
  int errors = 0;

  /* 1. L2 interleaved region: write below 256 KiB, read 256 KiB higher. */
  uint32_t base  = 0x1C030000;
  uint32_t alias = base + 0x40000;
  WR(base, 0xCAFE0001);
  printf("L2  [%08x]=%08x  alias [%08x]=%08x\n", base, RD(base), alias, RD(alias));
  WR(alias, 0x12345678);
  printf("after write to alias: [%08x]=%08x\n", base, RD(base));
  if (RD(base) != 0x12345678) errors++;

  /* 2. Boot ROM: read first word and the same offset 8 KiB higher. */
  printf("ROM [1a000000]=%08x  [1a002000]=%08x  [1a03e000]=%08x\n",
         RD(0x1A000000), RD(0x1A002000), RD(0x1A03E000));
  if (RD(0x1A000000) != RD(0x1A002000)) errors++;

  printf("aliasing %s\n", errors ? "NOT observed" : "observed");
  return errors;
}
