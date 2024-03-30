#include <stdio.h>

#include "imrat.h"

struct test {
  char* input;
  int radix;
  mp_result want;
};

int main(int arch, char* argv[]) {
  struct test tests[] = {
    {"123", 10, 0},
    {"  1ca", 16, 0},
    {"1010", 2, 0},
    {"123 ", 10, -5}, /* MP_TRUNC */
    {"123/456", 8, 0},
    {"123 / 456", 8, 0},
    {"123 /", 8, -4}, /* MP_UNDEF */
    {" -5/-3", 10, 0},
    {NULL, 10, 0},
  };

  int errs = 0;
  for (int i = 0; tests[i].input != NULL; i++) {
    mpq_t value;
    mp_rat_init(&value);

    mp_result got = mp_rat_read_cstring(&value, tests[i].radix, tests[i].input, NULL);
    if (got != tests[i].want) {
      printf("ERROR: test %d: input \"%s\": got \"%s\", want \"%s\"\n",
             i+1, tests[i].input, mp_error_string(got), mp_error_string(tests[i].want));
    }
  }
  printf("REGRESSION: mp_rat_read_cstring inconsistent space handling: %s\n",
         errs ? "FAILED" : "OK");
  return !errs;
}
