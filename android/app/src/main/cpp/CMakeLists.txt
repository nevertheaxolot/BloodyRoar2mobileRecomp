cmake_minimum_required(VERSION 3.22)
project(psx-runtime-android)

# --- SDL2 ---
# Necesitas descargar "SDL2" (versión Android, con su carpeta android-project)
# desde el repo oficial libsdl-org/SDL y colocar su código en
# android/app/src/main/cpp/SDL/ antes de compilar. Esto es aparte del SDL2 de
# escritorio que ya usa el proyecto original en PC.
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/SDL SDL2-build)

# --- psxrecomp (submódulo del proyecto original) ---
# Se asume que ya clonaste el repo con submódulos (checkout recursivo, como
# hace el workflow de Actions). Aquí lo compilamos como librería para Android
# en lugar de ejecutable de escritorio.
set(PSXRECOMP_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../../../../psxrecomp)

add_library(psx-runtime-android SHARED
    android_main_glue.c
    # TODO: aquí hay que listar/enlazar las fuentes reales del runtime de
    # psxrecomp (o añadir su CMakeLists.txt real vía add_subdirectory si
    # expone una librería en vez de solo un ejecutable). Esto depende de
    # cómo está organizado ese submódulo por dentro — es el primer punto
    # que probablemente falle en el primer build y haya que ajustar con el
    # log de error real de Actions en la mano.
)

target_include_directories(psx-runtime-android PRIVATE
    ${PSXRECOMP_DIR}/include
)

find_library(log-lib log)
find_library(android-lib android)
find_library(GLESv3-lib GLESv3)
find_library(vulkan-lib vulkan)

target_link_libraries(psx-runtime-android
    SDL2
    ${log-lib}
    ${android-lib}
    ${GLESv3-lib}
    ${vulkan-lib}
)
