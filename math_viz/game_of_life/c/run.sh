#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Print each command before executing it

# Use Ninja if available
if command -v ninja &>/dev/null; then
    GENERATOR="-G Ninja"
else
    GENERATOR="-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
fi

# Enable CCache if available
if command -v ccache &>/dev/null; then
    export CMAKE_CXX_COMPILER_LAUNCHER=ccache
    export CMAKE_C_COMPILER_LAUNCHER=ccache
fi

# Run CMake with optimizations
cmake -S . -B build $GENERATOR -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Ensure compile_commands.json is linked to the project root (for LSP support)
ln -sf build/compile_commands.json .

# Build with all available CPU cores
cmake --build build -- -j$(nproc)

# Move to build directory and execute
cd build/Release
./gol
