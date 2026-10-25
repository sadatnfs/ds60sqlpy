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

__global__ void block_sums(const int *input, int *output, std::size_t n) {
  __shared__ int tile[64];
  const unsigned lane = threadIdx.x;
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + lane;
  tile[lane] = i < n ? input[i] : 0;
  __syncthreads();
  for (unsigned width = 32; width > 0; width /= 2) {
    if (lane < width)
      tile[lane] += tile[lane + width];
    __syncthreads();
  }
  if (lane == 0)
    output[blockIdx.x] = tile[0];
}

void run_cases() {
  for (std::size_t n : {0U, 1U, 31U, 32U, 33U, 65U, 257U}) {
    if (n == 0) {
      require(0 == 0, "Empty sum identity");
      continue;
    }
    std::vector<int> input(n);
    for (std::size_t i = 0; i < n; ++i)
      input[i] = static_cast<int>(i % 11) - 5;
    const unsigned blocks = static_cast<unsigned>((n + 63) / 64);
    require(blocks <= 64,
            "This bounded two-stage lab supports at most 64 partials");
    DeviceBuffer<int> data(n), partials(blocks), result(1);
    CUDA_CHECK(cudaMemcpy(data.data, input.data(), n * sizeof(int),
                          cudaMemcpyHostToDevice));
    block_sums<<<blocks, 64>>>(data.data, partials.data, n);
    CUDA_CHECK(cudaGetLastError());
    block_sums<<<1, 64>>>(partials.data, result.data, blocks);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    int actual = 0;
    CUDA_CHECK(
        cudaMemcpy(&actual, result.data, sizeof(int), cudaMemcpyDeviceToHost));
    require(actual == std::accumulate(input.begin(), input.end(), 0),
            "Two-stage sum mismatch");
    data.close();
    partials.close();
    result.close();
    std::cout << "count " << n << " sum " << actual << " validated\n";
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
