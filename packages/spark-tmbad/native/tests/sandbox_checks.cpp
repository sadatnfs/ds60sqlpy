// SPDX-License-Identifier: MIT
#include "ds60_tmbad/sandbox.hpp"
#include <sys/mman.h>
#include <sys/wait.h>
#include <iostream>
using namespace ds60_tmbad;
void check(bool okay) {
  if (!okay)
    throw std::runtime_error("Native process guard check failed");
}
int main() {
  try {
    // Fork before confinement to independently observe parent-death handling.
    check(prctl(PR_SET_CHILD_SUBREAPER, 1) == 0);
    int ready[2];
    check(pipe(ready) == 0);
    const pid_t parent = fork();
    check(parent >= 0);
    if (parent == 0) {
      close(ready[0]);
      const pid_t child = fork();
      if (child < 0)
        _exit(20);
      if (child == 0) {
        process_guards();
        const char okay = '1';
        if (write(ready[1], &okay, 1) != 1)
          _exit(21);
        for (;;)
          pause();
      }
      // Wait for explicit coordinator acknowledgement, ensuring guards are set.
      close(ready[1]);
      for (;;)
        pause();
    }
    close(ready[1]);
    char marker = 0;
    check(read(ready[0], &marker, 1) == 1 && marker == '1');
    close(ready[0]);
    check(kill(parent, SIGTERM) == 0);
    int status = 0;
    check(waitpid(parent, &status, 0) == parent && WIFSIGNALED(status));
    const pid_t orphan = waitpid(-1, &status, 0);
    check(orphan > 0 && WIFSIGNALED(status) && WTERMSIG(status) == SIGKILL);
    process_guards();
    rlimit limit{};
    check(getrlimit(RLIMIT_AS, &limit) == 0 &&
          limit.rlim_cur == address_space_limit);
    check(getrlimit(RLIMIT_CPU, &limit) == 0 && limit.rlim_cur == 120);
    check(getrlimit(RLIMIT_CORE, &limit) == 0 && limit.rlim_cur == 0);
    check(prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0) == 1);
    errno = 0;
    check(fork() == -1 && errno == EPERM);
    char path[] = "/bin/true";
    char *args[]{path, nullptr};
    char *env[]{nullptr};
    errno = 0;
    check(execve(path, args, env) == -1 && errno == EPERM);
    errno = 0;
    void *large =
        mmap(nullptr, 2ULL * address_space_limit, PROT_READ | PROT_WRITE,
             MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    check(large == MAP_FAILED && errno == ENOMEM);
    std::cout << "PASS parent-death SIGKILL, no-child/no-exec policy, "
                 "no-new-privileges, address-space/CPU/core limits\n";
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
