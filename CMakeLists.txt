cmake_minimum_required(VERSION 3.14)
project(springbootplusplus-web VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fetch dependencies FIRST, before pre-build script
# This ensures dependencies are available when the pre-build script runs
include(FetchContent)

# Fetch serializationlib
FetchContent_Declare(
    serializationlib
    GIT_REPOSITORY https://github.com/compilerNayan/arduinolib1.git
    GIT_TAG        dev
)

# Fetch ArduionoLibServer
FetchContent_Declare(
    arduionolibserver
    GIT_REPOSITORY https://github.com/compilerNayan/arduionolibserver.git
    GIT_TAG        dev
)

# Fetch ArduinoDesktopServer
FetchContent_Declare(
    arduinodesktopserver
    GIT_REPOSITORY https://github.com/compilerNayan/arduinodesktopserver.git
    GIT_TAG        dev
)

FetchContent_MakeAvailable(serializationlib arduionolibserver arduinodesktopserver)

# Run pre-build script during configuration (runs even if client creates own library)
# This will run whenever this CMakeLists.txt is processed
# Note: All dependencies are now available since FetchContent_MakeAvailable was called above
find_program(PYTHON_EXECUTABLE python3 python)
if(PYTHON_EXECUTABLE AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/springbootplusplus-web_scripts/springbootplusplus-web_pre_build.py")
    # Get the client project directory (CMAKE_SOURCE_DIR is the top-level project source directory)
    # When this library is included via FetchContent, CMAKE_SOURCE_DIR points to the client project
    set(CLIENT_PROJECT_DIR ${CMAKE_SOURCE_DIR})
    
    # Set environment variable for the script
    set(ENV{CMAKE_PROJECT_DIR} ${CLIENT_PROJECT_DIR})
    
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} 
            "${CMAKE_CURRENT_SOURCE_DIR}/springbootplusplus-web_scripts/springbootplusplus-web_pre_build.py"
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        RESULT_VARIABLE PRE_BUILD_RESULT
        OUTPUT_VARIABLE PRE_BUILD_OUTPUT
        ERROR_VARIABLE PRE_BUILD_ERROR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE
    )
    if(PRE_BUILD_OUTPUT)
        message(STATUS "springbootplusplus-web pre-build output:\n${PRE_BUILD_OUTPUT}")
    endif()
    if(PRE_BUILD_ERROR)
        message(STATUS "springbootplusplus-web pre-build errors (expected in non-PlatformIO environment):\n${PRE_BUILD_ERROR}")
    endif()
    if(PRE_BUILD_RESULT AND NOT PRE_BUILD_RESULT EQUAL "0")
        message(STATUS "springbootplusplus-web pre-build script exited with code ${PRE_BUILD_RESULT} (this is expected in non-PlatformIO CMake builds)")
    endif()
endif()

# Create header-only library (INTERFACE library)
add_library(springbootplusplus-web INTERFACE)

# Set target properties
set_target_properties(springbootplusplus-web PROPERTIES
    VERSION ${PROJECT_VERSION}
)

# Set include directories
target_include_directories(springbootplusplus-web INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:include>
)

# Link serializationlib (header-only library)
# Try the namespaced target first, fallback to non-namespaced
if(TARGET serializationlib::serializationlib)
    target_link_libraries(springbootplusplus-web INTERFACE serializationlib::serializationlib)
elseif(TARGET serializationlib)
    target_link_libraries(springbootplusplus-web INTERFACE serializationlib)
else()
    # Fallback: manually add include directory if target doesn't exist
    FetchContent_GetProperties(serializationlib)
    if(serializationlib_SOURCE_DIR)
        target_include_directories(springbootplusplus-web INTERFACE
            $<BUILD_INTERFACE:${serializationlib_SOURCE_DIR}/src>
            $<INSTALL_INTERFACE:include>
        )
    endif()
endif()

# Link arduionolibserver (header-only library)
# Try the namespaced target first, fallback to non-namespaced
if(TARGET arduionolibserver::arduionolibserver)
    target_link_libraries(springbootplusplus-web INTERFACE arduionolibserver::arduionolibserver)
elseif(TARGET arduionolibserver)
    target_link_libraries(springbootplusplus-web INTERFACE arduionolibserver)
else()
    # Fallback: manually add include directory if target doesn't exist
    FetchContent_GetProperties(arduionolibserver)
    if(arduionolibserver_SOURCE_DIR)
        target_include_directories(springbootplusplus-web INTERFACE
            $<BUILD_INTERFACE:${arduionolibserver_SOURCE_DIR}/src>
            $<INSTALL_INTERFACE:include>
        )
    endif()
endif()

# Link arduinodesktopserver (header-only library)
# Try the namespaced target first, fallback to non-namespaced
if(TARGET arduinodesktopserver::arduinodesktopserver)
    target_link_libraries(springbootplusplus-web INTERFACE arduinodesktopserver::arduinodesktopserver)
elseif(TARGET arduinodesktopserver)
    target_link_libraries(springbootplusplus-web INTERFACE arduinodesktopserver)
else()
    # Fallback: manually add include directory if target doesn't exist
    FetchContent_GetProperties(arduinodesktopserver)
    if(arduinodesktopserver_SOURCE_DIR)
        target_include_directories(springbootplusplus-web INTERFACE
            $<BUILD_INTERFACE:${arduinodesktopserver_SOURCE_DIR}/src>
            $<INSTALL_INTERFACE:include>
        )
    endif()
endif()

# Note: For INTERFACE libraries, we don't need to add header files to target_sources
# The include directories are sufficient for consumers to find the headers

# Add pre-build script execution
# Note: This script requires PlatformIO environment to run properly
find_program(PYTHON_EXECUTABLE python3 python REQUIRED)

# Create a custom target that runs the pre-build script
# Set the project directory environment variable for the script
if(CMAKE_SOURCE_DIR)
    set(CLIENT_PROJECT_DIR ${CMAKE_SOURCE_DIR})
else()
    # Fallback if CMAKE_SOURCE_DIR is not available
    get_filename_component(CLIENT_PROJECT_DIR "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
endif()

add_custom_target(springbootplusplus-web_pre_build
    COMMAND ${CMAKE_COMMAND} -E env "CMAKE_PROJECT_DIR=${CLIENT_PROJECT_DIR}"
        ${PYTHON_EXECUTABLE} 
        "${CMAKE_CURRENT_SOURCE_DIR}/springbootplusplus-web_scripts/springbootplusplus-web_pre_build.py"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running springbootplusplus-web pre-build script"
    VERBATIM
)

# Make the library depend on the pre-build step
add_dependencies(springbootplusplus-web springbootplusplus-web_pre_build)

# Optional: Set up installation
include(GNUInstallDirs)

install(TARGETS springbootplusplus-web
    EXPORT springbootplusplus-webTargets
)

install(FILES src/NayanMath2.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT springbootplusplus-webTargets
    FILE springbootplusplus-webTargets.cmake
    NAMESPACE springbootplusplus-web::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/springbootplusplus-web
)

# Optional: Create a config file for find_package support
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arduinolib2Config.cmake.in")
    include(CMakePackageConfigHelpers)

    configure_package_config_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arduinolib2Config.cmake.in"
        "${CMAKE_CURRENT_BINARY_DIR}/springbootplusplus-webConfig.cmake"
        INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/springbootplusplus-web
    )

    write_basic_package_version_file(
        "${CMAKE_CURRENT_BINARY_DIR}/springbootplusplus-webConfigVersion.cmake"
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY AnyNewerVersion
    )

    install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/springbootplusplus-webConfig.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/springbootplusplus-webConfigVersion.cmake"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/springbootplusplus-web
    )
endif()

