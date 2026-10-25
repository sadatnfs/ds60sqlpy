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

__global__ void neighbor_sum(const int *input, int *output, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    output[i] =
        (i > 0 ? input[i - 1] : 0) + input[i] + (i + 1 < n ? input[i + 1] : 0);
}

void run_cases() {
  for (std::size_t n : {0U, 1U, 3U, 31U, 32U, 33U, 257U}) {
    if (n == 0)
      continue;
    std::vector<int> original(n), expected(n), actual(n);
    for (std::size_t i = 0; i < n; ++i)
      original[i] = static_cast<int>(i % 7);
    for (std::size_t i = 0; i < n; ++i)
      expected[i] = (i > 0 ? original[i - 1] : 0) + original[i] +
                    (i + 1 < n ? original[i + 1] : 0);
    DeviceBuffer<int> input(n), output(n);
    CUDA_CHECK(cudaMemcpy(input.data, original.data(), n * sizeof(int),
                          cudaMemcpyHostToDevice));
    neighbor_sum<<<static_cast<unsigned>((n + 31) / 32), 32>>>(input.data,
                                                               output.data, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(actual.data(), output.data, n * sizeof(int),
                          cudaMemcpyDeviceToHost));
    require(actual == expected, "Fixed-zero neighbor sum mismatch");
    CUDA_CHECK(cudaMemcpy(actual.data(), input.data, n * sizeof(int),
                          cudaMemcpyDeviceToHost));
    require(actual == original, "Stencil modified its input");
    input.close();
    output.close();
    std::cout << "count " << n
              << " fixed-zero sum validated; divide by 3 for the mean\n";
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
