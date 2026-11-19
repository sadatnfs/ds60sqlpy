#include <stdio.h>

int main(void) {
  /* Exercise 1: Create a trailing payload: change one input
     Copy worked example 1 into a scratch pad and change `unsigned char data[] =
     {1, 2, 3};` to `unsigned char data[] = {2, 2, 3};`. Before running, predict
     which CHECK fails and which value it now sees; then run it and restore the
     original line. Expected: The changed run stops with `Check failed` at the
     CHECK on `p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2] ==
     3`. Restoring the original line brings back the worked observation: length
     and all three bytes are retained. */

  /* Exercise 2: Create an empty packet: debug a regression
     A regression changed one token in worked example 2, so one line now reads
     `struct Packet *p = packet_create(NULL, 1);`. Run worked example 2 with
     that line, use the failing CHECK to locate the defect and repair it without
     changing the CHECK. Expected: Before the repair the run stops with `Check
     failed` at the CHECK on `p != NULL && p->length == 0`; after it the line
     reads `struct Packet *p = packet_create(NULL, 0);` again and the header
     exists and records zero length. */

  /* Exercise 3: Reject total-size overflow
     Request SIZE_MAX payload bytes.
     Expected: The operation returns NULL before allocation. */

  /* Exercise 4: Clone the complete record
     Create two packets from the same source and mutate one.
     Expected: The other payload remains unchanged. */

  /* Exercise 5: Preserve binary zero
     Store a payload containing a zero byte.
     Expected: Length remains three and the zero is retained. */

  /* Exercise 6: Transfer source independence
     Change the original source after packet construction.
     Expected: The owned packet retains its copied value. */

  puts("Implement the six investigations in your saved pad.");
  return 0;
}
