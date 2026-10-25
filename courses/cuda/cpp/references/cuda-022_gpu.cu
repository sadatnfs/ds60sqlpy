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

__global__ void count_bins(const int *input, unsigned *bins, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    atomicAdd(&bins[input[i]],
              1U); // Host validates category range before upload.
}

void run_cases() {
  const std::vector<std::vector<int>> cases{
      {}, {0}, {0, 2, 2, 1, 2, 0}, std::vector<int>(257, 2)};
  for (const auto &values : cases) {
    std::array<unsigned, 3> expected{0, 0, 0}, actual{0, 0, 0};
    for (int value : values) {
      require(value >= 0 && value < 3, "Category out of range");
      ++expected[value];
    }
    if (values.empty()) {
      require(expected == actual, "Empty histogram mismatch");
      continue;
    }
    DeviceBuffer<int> data(values.size());
    DeviceBuffer<unsigned> bins(3);
    CUDA_CHECK(cudaMemcpy(data.data, values.data(), values.size() * sizeof(int),
                          cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemset(bins.data, 0, 3 * sizeof(unsigned)));
    count_bins<<<static_cast<unsigned>((values.size() + 31) / 32), 32>>>(
        data.data, bins.data, values.size());
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(actual.data(), bins.data, 3 * sizeof(unsigned),
                          cudaMemcpyDeviceToHost));
    require(actual == expected, "Histogram mismatch");
    data.close();
    bins.close();
    std::cout << "count " << values.size() << " histogram validated\n";
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
