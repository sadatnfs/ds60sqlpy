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

__global__ void brighten(int *image, std::size_t width, std::size_t height,
                         std::size_t stride) {
  const std::size_t col =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  const std::size_t row =
      static_cast<std::size_t>(blockIdx.y) * blockDim.y + threadIdx.y;
  if (row < height && col < width)
    image[row * stride + col] += 10;
}

void run_cases() {
  const std::array<std::array<std::size_t, 2>, 4> shapes{
      {{3, 2}, {2, 3}, {17, 9}, {1, 1}}};
  for (const auto &shape : shapes) {
    const auto width = shape[0], height = shape[1], stride = width + 2;
    std::vector<int> expected(height * stride, -99);
    for (std::size_t r = 0; r < height; ++r)
      for (std::size_t c = 0; c < width; ++c)
        expected[r * stride + c] = static_cast<int>(r * width + c);
    DeviceBuffer<int> image(expected.size());
    CUDA_CHECK(cudaMemcpy(image.data, expected.data(),
                          expected.size() * sizeof(int),
                          cudaMemcpyHostToDevice));
    const dim3 block(8, 4);
    const dim3 grid(static_cast<unsigned>((width + 7) / 8),
                    static_cast<unsigned>((height + 3) / 4));
    brighten<<<grid, block>>>(image.data, width, height, stride);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    std::vector<int> actual(expected.size());
    CUDA_CHECK(cudaMemcpy(actual.data(), image.data,
                          actual.size() * sizeof(int), cudaMemcpyDeviceToHost));
    for (std::size_t r = 0; r < height; ++r)
      for (std::size_t c = 0; c < width; ++c)
        expected[r * stride + c] += 10;
    require(actual == expected, "2D result or padding changed incorrectly");
    image.close();
    std::cout << width << " by " << height << " and padding validated\n";
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
