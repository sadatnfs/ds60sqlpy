// SPDX-License-Identifier: MIT
#pragma once
#include "types.hpp"
#include <cerrno>
#include <csignal>
#include <cstddef>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>

namespace ds60_tmbad {
constexpr rlim_t address_space_limit = 1024ULL * 1024 * 1024;
inline void process_guards() {
  const pid_t parent = getppid();
  require(prctl(PR_SET_PDEATHSIG, SIGKILL) == 0,
          "Cannot establish parent-death handling", "PREPARATION_ERROR");
  require(getppid() == parent, "Parent exited during worker startup",
          "PARENT_EXITED");
  rlimit core{0, 0}, address{address_space_limit, address_space_limit},
      cpu{120, 120};
  require(setrlimit(RLIMIT_CORE, &core) == 0 &&
              setrlimit(RLIMIT_AS, &address) == 0 &&
              setrlimit(RLIMIT_CPU, &cpu) == 0,
          "Cannot establish native resource limits", "PREPARATION_ERROR");
  require(prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == 0,
          "Cannot establish no-new-privileges", "PREPARATION_ERROR");
#if defined(__aarch64__)
  constexpr unsigned native_arch = AUDIT_ARCH_AARCH64;
#elif defined(__x86_64__)
  constexpr unsigned native_arch = AUDIT_ARCH_X86_64;
#else
#error This prepared backend supports native Linux AMD64 and ARM64 only.
#endif
  std::vector<sock_filter> filters{
      BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(seccomp_data, arch)),
      BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, native_arch, 1, 0),
      BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
      BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(seccomp_data, nr)),
  };
  std::vector<unsigned> denied{SYS_execve, SYS_execveat, SYS_clone};
#ifdef SYS_fork
  denied.push_back(SYS_fork);
#endif
#ifdef SYS_vfork
  denied.push_back(SYS_vfork);
#endif
#ifdef SYS_clone3
  denied.push_back(SYS_clone3);
#endif
  for (unsigned call : denied) {
    filters.push_back(BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, call, 0, 1));
    filters.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM));
  }
#if defined(__x86_64__)
  // This is a native x86_64 binary; do not permit alternate x32 syscall numbers.
  filters.push_back(BPF_JUMP(BPF_JMP | BPF_JGE | BPF_K, 0x40000000, 0, 1));
  filters.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | EPERM));
#endif
  filters.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW));
  sock_fprog program{static_cast<unsigned short>(filters.size()),
                     filters.data()};
  require(prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &program) == 0,
          "Cannot establish no-child/no-exec policy", "PREPARATION_ERROR");
}
} // namespace ds60_tmbad
