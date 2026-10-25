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

__global__ void write_indices(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] = static_cast<int>(i);
}
__global__ void increment(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] += 1;
}

void run_cases() {
  constexpr std::size_t n = 33;
  DeviceBuffer<int> values(n);
  cudaStream_t stream = nullptr;
  cudaGraph_t graph = nullptr;
  cudaGraphExec_t instance = nullptr;
  bool capturing = false;
  try {
    CUDA_CHECK(cudaStreamCreateWithFlags(&stream, cudaStreamNonBlocking));
    CUDA_CHECK(
        cudaStreamBeginCapture(stream, cudaStreamCaptureModeThreadLocal));
    capturing = true;
    write_indices<<<2, 32, 0, stream>>>(values.data, n);
    CUDA_CHECK(cudaGetLastError());
    increment<<<2, 32, 0, stream>>>(values.data, n);
    CUDA_CHECK(cudaGetLastError());
    const auto end_status = cudaStreamEndCapture(stream, &graph);
    capturing = false;
    CUDA_CHECK(end_status);
    CUDA_CHECK(cudaGraphInstantiate(&instance, graph, nullptr, nullptr, 0));
    for (int replay = 0; replay < 3; ++replay) {
      CUDA_CHECK(cudaGraphLaunch(instance, stream));
      CUDA_CHECK(cudaStreamSynchronize(stream));
      std::vector<int> host(n);
      CUDA_CHECK(cudaMemcpy(host.data(), values.data, n * sizeof(int),
                            cudaMemcpyDeviceToHost));
      for (std::size_t i = 0; i < n; ++i)
        require(host[i] == static_cast<int>(i) + 1, "Graph replay mismatch");
    }
    CUDA_CHECK(cudaGraphExecDestroy(instance));
    instance = nullptr;
    CUDA_CHECK(cudaGraphDestroy(graph));
    graph = nullptr;
    CUDA_CHECK(cudaStreamDestroy(stream));
    stream = nullptr;
    values.close();
  } catch (...) {
    if (capturing) {
      cudaGraph_t abandoned = nullptr;
      cudaStreamEndCapture(stream, &abandoned);
      if (abandoned != nullptr)
        cudaGraphDestroy(abandoned);
    }
    if (stream != nullptr)
      cudaStreamSynchronize(stream);
    if (instance != nullptr)
      cudaGraphExecDestroy(instance);
    if (graph != nullptr)
      cudaGraphDestroy(graph);
    if (stream != nullptr)
      cudaStreamDestroy(stream);
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
