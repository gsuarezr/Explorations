cmake_minimum_required(VERSION 3.16)
project(gol)

# set the output directory for built objects.
# This makes sure that the dynamic library goes into the build directory automatically.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIGURATION>")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIGURATION>")

# This assumes the SDL source is available in vendored/SDL
add_subdirectory(/home/mcditoos/SDL ${CMAKE_BINARY_DIR}/SDL EXCLUDE_FROM_ALL)

# Create your game executable target as usual
add_executable(gol WIN32 gol.c)

# Link to the actual SDL3 library.
target_link_libraries(gol PRIVATE SDL3::SDL3)

#for intellisense
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
