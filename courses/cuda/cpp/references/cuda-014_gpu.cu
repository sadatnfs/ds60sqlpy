// Optional NVIDIA GPU lab. This file does not run on a CPU fallback.
// Compile in a separately prepared CUDA environment:
// nvcc -std=c++17 -O2 -lineinfo main.cu -o main
#include <cuda_runtime.h>
#include <algorithm>
#include <array>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

void checked(cudaError_t status, const char *expression, int line) {
  if (status != cudaSuccess) {
    throw std::runtime_error(std::string(expression) + " at line " +
                             std::to_string(line) + ": " +
                             cudaGetErrorString(status));
  }
}
#define CUDA_CHECK(expression) checked((expression), #expression, __LINE__)

template <class T> class DeviceBuffer {
public:
  T *data = nullptr;
  explicit DeviceBuffer(std::size_t count) {
    if (count != 0)
      CUDA_CHECK(
          cudaMalloc(reinterpret_cast<void **>(&data), count * sizeof(T)));
  }
  DeviceBuffer(const DeviceBuffer &) = delete;
  DeviceBuffer &operator=(const DeviceBuffer &) = delete;
  ~DeviceBuffer() {
    if (data != nullptr)
      cudaFree(data);
  }
  void close() {
    if (data != nullptr) {
      CUDA_CHECK(cudaFree(data));
      data = nullptr;
    }
  }
};

void require_device() {
  int count = 0;
  CUDA_CHECK(cudaGetDeviceCount(&count));
  if (count < 1)
    throw std::runtime_error("No NVIDIA CUDA device; GPU lab unavailable.");
  CUDA_CHECK(cudaSetDevice(0));
  cudaDeviceProp properties{};
  CUDA_CHECK(cudaGetDeviceProperties(&properties, 0));
  std::cout << "Actual CUDA device: " << properties.name << '\n';
}

void require(bool condition, const char *message) {
  if (!condition)
    throw std::runtime_error(message);
}

__global__ void vector_add(const int *a, const int *b, int *out,
                           std::size_t n) {
  const std::size_t start =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  const std::size_t stride = static_cast<std::size_t>(gridDim.x) * blockDim.x;
  for (std::size_t i = start; i < n; i += stride)
    out[i] = a[i] + b[i];
}

void run_cases() {
  for (std::size_t n : {0U, 1U, 31U, 32U, 33U, 257U}) {
    if (n == 0)
      continue;
    std::vector<int> a(n), b(n), host(n);
    for (std::size_t i = 0; i < n; ++i) {
      a[i] = static_cast<int>(i) - 7;
      b[i] = 3 * static_cast<int>(i) + 2;
    }
    DeviceBuffer<int> da(n), db(n), out(n);
    CUDA_CHECK(
        cudaMemcpy(da.data, a.data(), n * sizeof(int), cudaMemcpyHostToDevice));
    CUDA_CHECK(
        cudaMemcpy(db.data, b.data(), n * sizeof(int), cudaMemcpyHostToDevice));
    vector_add<<<2, 32>>>(da.data, db.data, out.data, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(host.data(), out.data, n * sizeof(int),
                          cudaMemcpyDeviceToHost));
    for (std::size_t i = 0; i < n; ++i)
      require(host[i] == a[i] + b[i], "Vector addition mismatch");
    da.close();
    db.close();
    out.close();
    std::cout << "count " << n << " validated\n";
  }
}

int main() {
  try {
    require_device();
    run_cases();
    std::cout << "GPU results validated against the host contract.\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "CUDA lab failed or unavailable: " << error.what() << '\n';
    return 1;
  }
}
