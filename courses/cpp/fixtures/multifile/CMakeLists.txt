cmake_minimum_required(VERSION 3.28)
project(ds60_multifile LANGUAGES CXX)
include(CTest)
add_library(ds60_math STATIC math.cpp)
target_include_directories(ds60_math PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>"
                                            "$<INSTALL_INTERFACE:include>")
target_compile_features(ds60_math PUBLIC cxx_std_20)
set_target_properties(ds60_math PROPERTIES CXX_EXTENSIONS OFF)
add_executable(math_check main.cpp)
target_link_libraries(math_check PRIVATE ds60_math)
add_test(NAME arithmetic_contract COMMAND math_check)
set_tests_properties(arithmetic_contract PROPERTIES TIMEOUT 5 PASS_REGULAR_EXPRESSION
                                                    "add=5 subtract=2")
install(
  TARGETS ds60_math math_check
  EXPORT ds60MathTargets
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin)
install(FILES math.hpp DESTINATION include)
install(
  EXPORT ds60MathTargets
  NAMESPACE ds60::
  DESTINATION lib/cmake/ds60Math)
