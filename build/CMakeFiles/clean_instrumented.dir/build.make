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
CMAKE_SOURCE_DIR = /home/hrishik/Repos/GitHub/term

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/hrishik/Repos/GitHub/term/build

# Utility rule file for clean_instrumented.

# Include any custom commands dependencies for this target.
include CMakeFiles/clean_instrumented.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/clean_instrumented.dir/progress.make

CMakeFiles/clean_instrumented:
	cd /home/hrishik/Repos/GitHub/term && /usr/bin/cmake -E remove *.c_instrumented.c

clean_instrumented: CMakeFiles/clean_instrumented
clean_instrumented: CMakeFiles/clean_instrumented.dir/build.make
.PHONY : clean_instrumented

# Rule to build all files generated by this target.
CMakeFiles/clean_instrumented.dir/build: clean_instrumented
.PHONY : CMakeFiles/clean_instrumented.dir/build

CMakeFiles/clean_instrumented.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/clean_instrumented.dir/cmake_clean.cmake
.PHONY : CMakeFiles/clean_instrumented.dir/clean

CMakeFiles/clean_instrumented.dir/depend:
	cd /home/hrishik/Repos/GitHub/term/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/hrishik/Repos/GitHub/term /home/hrishik/Repos/GitHub/term /home/hrishik/Repos/GitHub/term/build /home/hrishik/Repos/GitHub/term/build /home/hrishik/Repos/GitHub/term/build/CMakeFiles/clean_instrumented.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/clean_instrumented.dir/depend
