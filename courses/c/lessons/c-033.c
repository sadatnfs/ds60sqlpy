#include <stdio.h>

int main(void) {
  /* Exercise 1: Create a trailing payload: change one input
     Copy worked example 1, the "create a trailing payload" case, into a scratch
     pad and change `unsigned char data[] = {1, 2, 3};` to `unsigned char data[]
     = {2, 2, 3};`. Before running, predict which CHECK fails and which value it
     sees in place of the worked result (length and all three bytes are
     retained); then run it and restore the original line. Expected: With
     `unsigned char data[] = {2, 2, 3};` the run stops with `Check failed` at
     the CHECK on `p != NULL && p->length == 3 && p->data[0] == 1 && p->data[2]
     == 3`, because the "create a trailing payload" case no longer shows that
     length and all three bytes are retained. Restoring `unsigned char data[] =
     {1, 2, 3};` brings that observation back. */

  /* Exercise 2: Create an empty packet: debug a regression
     A regression changed one token in worked example 2, the "create an empty
     packet" case, so one line now reads `struct Packet *p = packet_create(NULL,
     1);`. Run the example with that line, use the failing CHECK to find why the
     header exists and records zero length no longer holds and repair the line
     without changing the CHECK. Expected: Before the repair the run stops with
     `Check failed` at the CHECK on `p != NULL && p->length == 0`. Once the line
     reads `struct Packet *p = packet_create(NULL, 0);` again, the "create an
     empty packet" case again shows that the header exists and records zero
     length. */

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
