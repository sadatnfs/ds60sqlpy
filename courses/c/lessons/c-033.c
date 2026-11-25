#include <stdio.h>

int main(void) {
  /* Exercise 1: Create a trailing payload: change one input
     In worked example 1, change `unsigned char data[] = {1, 2, 3};` to
     `unsigned char data[] = {2, 2, 3};`. Predict which value the CHECK on `p !=
     NULL && p->length == 3 && p->data[0] == 1 && p->data[2] == 3` sees, then
     run and restore. Expected: `Check failed` at `p != NULL && p->length == 3
     && p->data[0] == 1 && p->data[2] == 3`; restoring `unsigned char data[] =
     {1, 2, 3};` passes again. */

  /* Exercise 2: Create an empty packet: debug a regression
     Worked example 2 now has a line reading `struct Packet *p =
     packet_create(NULL, 1);`. Repair it so that the header exists and records
     zero length again. Expected: `Check failed` at `p != NULL && p->length ==
     0` until the line reads `struct Packet *p = packet_create(NULL, 0);` again.
   */

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
