# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/tcs/Documents/Termination/Repo/Code/term

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/tcs/Documents/Termination/Repo/Code/term/build

# Include any dependencies generated for this target.
include CMakeFiles/instCore.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/instCore.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/instCore.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/instCore.dir/flags.make

CMakeFiles/instCore.dir/main.cpp.o: CMakeFiles/instCore.dir/flags.make
CMakeFiles/instCore.dir/main.cpp.o: ../main.cpp
CMakeFiles/instCore.dir/main.cpp.o: CMakeFiles/instCore.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/tcs/Documents/Termination/Repo/Code/term/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/instCore.dir/main.cpp.o"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/instCore.dir/main.cpp.o -MF CMakeFiles/instCore.dir/main.cpp.o.d -o CMakeFiles/instCore.dir/main.cpp.o -c /home/tcs/Documents/Termination/Repo/Code/term/main.cpp

CMakeFiles/instCore.dir/main.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/instCore.dir/main.cpp.i"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/tcs/Documents/Termination/Repo/Code/term/main.cpp > CMakeFiles/instCore.dir/main.cpp.i

CMakeFiles/instCore.dir/main.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/instCore.dir/main.cpp.s"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/tcs/Documents/Termination/Repo/Code/term/main.cpp -o CMakeFiles/instCore.dir/main.cpp.s

CMakeFiles/instCore.dir/PyASTVisitor.cpp.o: CMakeFiles/instCore.dir/flags.make
CMakeFiles/instCore.dir/PyASTVisitor.cpp.o: ../PyASTVisitor.cpp
CMakeFiles/instCore.dir/PyASTVisitor.cpp.o: CMakeFiles/instCore.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/tcs/Documents/Termination/Repo/Code/term/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/instCore.dir/PyASTVisitor.cpp.o"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/instCore.dir/PyASTVisitor.cpp.o -MF CMakeFiles/instCore.dir/PyASTVisitor.cpp.o.d -o CMakeFiles/instCore.dir/PyASTVisitor.cpp.o -c /home/tcs/Documents/Termination/Repo/Code/term/PyASTVisitor.cpp

CMakeFiles/instCore.dir/PyASTVisitor.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/instCore.dir/PyASTVisitor.cpp.i"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/tcs/Documents/Termination/Repo/Code/term/PyASTVisitor.cpp > CMakeFiles/instCore.dir/PyASTVisitor.cpp.i

CMakeFiles/instCore.dir/PyASTVisitor.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/instCore.dir/PyASTVisitor.cpp.s"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/tcs/Documents/Termination/Repo/Code/term/PyASTVisitor.cpp -o CMakeFiles/instCore.dir/PyASTVisitor.cpp.s

CMakeFiles/instCore.dir/PyASTConsumer.cpp.o: CMakeFiles/instCore.dir/flags.make
CMakeFiles/instCore.dir/PyASTConsumer.cpp.o: ../PyASTConsumer.cpp
CMakeFiles/instCore.dir/PyASTConsumer.cpp.o: CMakeFiles/instCore.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/tcs/Documents/Termination/Repo/Code/term/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object CMakeFiles/instCore.dir/PyASTConsumer.cpp.o"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/instCore.dir/PyASTConsumer.cpp.o -MF CMakeFiles/instCore.dir/PyASTConsumer.cpp.o.d -o CMakeFiles/instCore.dir/PyASTConsumer.cpp.o -c /home/tcs/Documents/Termination/Repo/Code/term/PyASTConsumer.cpp

CMakeFiles/instCore.dir/PyASTConsumer.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/instCore.dir/PyASTConsumer.cpp.i"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/tcs/Documents/Termination/Repo/Code/term/PyASTConsumer.cpp > CMakeFiles/instCore.dir/PyASTConsumer.cpp.i

CMakeFiles/instCore.dir/PyASTConsumer.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/instCore.dir/PyASTConsumer.cpp.s"
	clang++-14 $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/tcs/Documents/Termination/Repo/Code/term/PyASTConsumer.cpp -o CMakeFiles/instCore.dir/PyASTConsumer.cpp.s

# Object files for target instCore
instCore_OBJECTS = \
"CMakeFiles/instCore.dir/main.cpp.o" \
"CMakeFiles/instCore.dir/PyASTVisitor.cpp.o" \
"CMakeFiles/instCore.dir/PyASTConsumer.cpp.o"

# External object files for target instCore
instCore_EXTERNAL_OBJECTS =

../lib/libinstCore.a: CMakeFiles/instCore.dir/main.cpp.o
../lib/libinstCore.a: CMakeFiles/instCore.dir/PyASTVisitor.cpp.o
../lib/libinstCore.a: CMakeFiles/instCore.dir/PyASTConsumer.cpp.o
../lib/libinstCore.a: CMakeFiles/instCore.dir/build.make
../lib/libinstCore.a: CMakeFiles/instCore.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/tcs/Documents/Termination/Repo/Code/term/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Linking CXX static library ../lib/libinstCore.a"
	$(CMAKE_COMMAND) -P CMakeFiles/instCore.dir/cmake_clean_target.cmake
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/instCore.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/instCore.dir/build: ../lib/libinstCore.a
.PHONY : CMakeFiles/instCore.dir/build

CMakeFiles/instCore.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/instCore.dir/cmake_clean.cmake
.PHONY : CMakeFiles/instCore.dir/clean

CMakeFiles/instCore.dir/depend:
	cd /home/tcs/Documents/Termination/Repo/Code/term/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/tcs/Documents/Termination/Repo/Code/term /home/tcs/Documents/Termination/Repo/Code/term /home/tcs/Documents/Termination/Repo/Code/term/build /home/tcs/Documents/Termination/Repo/Code/term/build /home/tcs/Documents/Termination/Repo/Code/term/build/CMakeFiles/instCore.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/instCore.dir/depend
