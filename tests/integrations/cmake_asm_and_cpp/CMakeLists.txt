cmake_minimum_required(VERSION 3.12)
project(untitled)

set(CMAKE_CXX_STANDARD 14)
enable_language(ASM_NASM)

add_executable(untitled main.cpp random.asm)
