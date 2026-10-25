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

__global__ void produce(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] = 2 * static_cast<int>(i);
}
__global__ void consume(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] += 1;
}

void run_cases() {
  constexpr std::size_t n = 33;
  DeviceBuffer<int> values(n);
  cudaStream_t producer = nullptr, consumer = nullptr;
  cudaEvent_t ready = nullptr;
  try {
    CUDA_CHECK(cudaStreamCreateWithFlags(&producer, cudaStreamNonBlocking));
    CUDA_CHECK(cudaStreamCreateWithFlags(&consumer, cudaStreamNonBlocking));
    CUDA_CHECK(cudaEventCreateWithFlags(&ready, cudaEventDisableTiming));
    produce<<<2, 32, 0, producer>>>(values.data, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaEventRecord(ready, producer));
    CUDA_CHECK(cudaStreamWaitEvent(consumer, ready, 0));
    consume<<<2, 32, 0, consumer>>>(values.data, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaStreamSynchronize(consumer));
    std::vector<int> host(n);
    CUDA_CHECK(cudaMemcpy(host.data(), values.data, n * sizeof(int),
                          cudaMemcpyDeviceToHost));
    for (std::size_t i = 0; i < n; ++i)
      require(host[i] == 2 * static_cast<int>(i) + 1,
              "Cross-stream result mismatch");
    CUDA_CHECK(cudaEventDestroy(ready));
    ready = nullptr;
    CUDA_CHECK(cudaStreamDestroy(consumer));
    consumer = nullptr;
    CUDA_CHECK(cudaStreamDestroy(producer));
    producer = nullptr;
    values.close();
  } catch (...) {
    if (consumer != nullptr)
      cudaStreamSynchronize(consumer);
    if (producer != nullptr)
      cudaStreamSynchronize(producer);
    if (ready != nullptr)
      cudaEventDestroy(ready);
    if (consumer != nullptr)
      cudaStreamDestroy(consumer);
    if (producer != nullptr)
      cudaStreamDestroy(producer);
    throw;
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
