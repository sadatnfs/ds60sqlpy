#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void lesson_check(bool condition, const char *file, int line) {
  if (!condition) {
    fprintf(stderr, "Check failed at %s:%d\n", file, line);
    abort();
  }
}
#define CHECK(condition) lesson_check((condition), __FILE__, __LINE__)

int main(void) {
  /* Round-trip an owned stream */
  {
    FILE *f = tmpfile();
    CHECK(f != NULL);
    CHECK(fwrite("abc", 1, 3, f) == 3);
    rewind(f);
    char data[4] = {0};
    CHECK(fread(data, 1, 3, f) == 3 && strcmp(data, "abc") == 0);
    CHECK(fclose(f) == 0);
  }

  /* Observe a short read */
  {
    FILE *f = tmpfile();
    CHECK(f != NULL);
    CHECK(fwrite("ab", 1, 2, f) == 2);
    rewind(f);
    char data[4];
    size_t n = fread(data, 1, 4, f);
    CHECK(n == 2 && feof(f) && !ferror(f));
    CHECK(fclose(f) == 0);
  }

  /* Avoid prechecking EOF */
  {
    FILE *f = tmpfile();
    CHECK(f != NULL);
    CHECK(!feof(f));
    CHECK(fgetc(f) == EOF && feof(f));
    CHECK(fclose(f) == 0);
  }

  /* Read a bounded line */
  {
    FILE *f = tmpfile();
    CHECK(f != NULL);
    CHECK(fputs("red\n", f) >= 0);
    rewind(f);
    char line[8];
    CHECK(fgets(line, sizeof line, f) != NULL && strcmp(line, "red\n") == 0);
    CHECK(fclose(f) == 0);
  }

  /* Clear EOF by rewinding */
  {
    FILE *f = tmpfile();
    CHECK(f != NULL);
    CHECK(fputc('x', f) != EOF);
    rewind(f);
    CHECK(fgetc(f) == 'x' && fgetc(f) == EOF);
    rewind(f);
    CHECK(!feof(f) && fgetc(f) == 'x');
    CHECK(fclose(f) == 0);
  }

  /* Transfer binary zero bytes */
  {
    unsigned char source[] = {1, 0, 2}, out[3] = {0};
    FILE *f = tmpfile();
    CHECK(f != NULL);
    CHECK(fwrite(source, 1, 3, f) == 3);
    rewind(f);
    CHECK(fread(out, 1, 3, f) == 3 && memcmp(source, out, 3) == 0);
    CHECK(fclose(f) == 0);
  }
  puts("All lesson checks passed.");
  return 0;
}
