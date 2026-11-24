[简体中文](README.md) | English

# GD32F30x GCC + FreeRTOS Baseline Project

A minimal buildable project that depends on no IDE: **GD32F30x official standard peripheral library V3.0.3 + FreeRTOS-Kernel V10.5.1**, built with arm-none-eabi-gcc + GNU Make to produce .elf / .hex / .bin.

**Optional enhancements**: VSCode, device pack scripts, flashing and debugging — see [Optional Extensions](#optional-extensions-not-required-to-build) at the end. If you don't need them, you can delete the docs/ tools/ packs/ svd/ .vscode/ folders.

Third-party library files are taken verbatim from the official repositories and left unmodified; for versions, sources and licenses see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## GCC Advantages

**Cost and freedom**
GCC is completely free and open source. It has no 32 KB code-size limit like Keil MDK, and no commercial license fee is required.

**Cross-platform and team collaboration**
Keil MDK only supports Windows. The GCC toolchain, by contrast, runs natively on Windows, Linux and macOS. For developers using a Mac, or for teams that need to build on Linux servers, this is an essential capability.

**Automation and continuous integration (CI/CD)**
This is one of GCC's most striking advantages. Keil's command-line mode is limited and hard to fit into an automated build pipeline. GCC, by contrast, is a natural fit for build systems such as Makefile and CMake, and integrates smoothly with continuous integration environments such as GitHub Actions and GitLab CI, enabling automatic compilation, unit testing and firmware generation after each commit.

**Friendly project management**
With Keil or IAR, project files (such as .uvprojx) are complex formats that are hard to diff and work poorly with version control systems such as Git. The GCC approach manages the build with plain-text Makefile or CMakeLists.txt files, which Git can track and merge as clearly as source code, greatly simplifying version management of the project configuration.

## Directory Structure

```
.
├── GD32F30x/                           GD32F30x firmware library V3.0.3 (vendor files, unmodified)
│   ├── CMSIS/                          CMSIS core, startup files for each device, linker scripts, system clock
│   └── GD32F30x_standard_peripheral/   Standard peripheral library (24 .c files + headers)
├── FREERTOS/                           FreeRTOS-Kernel V10.5.1 (vendor files, unmodified)
│   ├── include/
│   └── portable/
│       ├── GCC/ARM_CM4F/               GCC port for Cortex-M4F
│       └── MemMang/heap_4.c
├── User/                               Project code
│   ├── main.c                          LED blink + task creation
│   ├── gd32f30x_it.c                   Exception handlers (SVC/PendSV/SysTick belong to FreeRTOS)
│   ├── freertos_hooks.c                FreeRTOS application hooks (stack overflow check)
│   ├── gd32f30x_libopt.h               Peripheral library selection header (from the official Template)
│   └── FreeRTOSConfig.h                FreeRTOS configuration
├── Makefile
├── UPSTREAM.md                         Sources, import scope and upgrade procedure for third-party libraries
├── THIRD_PARTY_NOTICES.md
├── LICENSE
│
├── docs/
│   └── vscode.md                       Optional: VSCode editing, flashing, debugging and device scripts
├── tools/                              Optional: pack download and device switching scripts
├── packs/                              Optional: downloaded device packs (not checked in)
├── svd/                                Optional: all SVDs extracted locally (not checked in)
└── .vscode/                            Optional: VSCode tasks and debug configuration
```

## Component Versions

| Component | Version | Upstream | License |
|-----------|---------|----------|---------|
| GD32F30x firmware library | V3.0.3 (tag `3.0.3`) | [GigaDevice-GD32-MCU/GD32F30x_Firmware_Library](https://github.com/GigaDevice-GD32-MCU/GD32F30x_Firmware_Library) | See `GD32F30x/LICENSE` (GigaDevice SLA) |
| FreeRTOS-Kernel | V10.5.1 (tag `V10.5.1`) | [FreeRTOS/FreeRTOS-Kernel](https://github.com/FreeRTOS/FreeRTOS-Kernel) | MIT |
| GCC startup files / linker scripts | Bundled with GD32F30x V3.0.3 | Same as above | Apache-2.0 (noted in file headers) |
| This project's own code | — | — | MIT, see [LICENSE](LICENSE) |

## Environment Setup

1. **ARM GNU Toolchain 13.3.rel1** (arm-none-eabi-gcc 13.3.1, the version tested with this project)

   Installing the official Arm build is recommended. The download page has moved to GitLab, but the binaries can still be downloaded directly:

   - Windows (x86_64) installer:
     <https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi.exe>
   - Windows portable zip:
     <https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi.zip>
   - Linux / macOS and other versions: <https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads>

   During installation, check **Add path to environment variable**.

   If you prefer not to modify PATH, point `GCC_PATH` at the toolchain's bin/:

   ```bash
   make GCC_PATH=/path/to/arm-none-eabi/bin
   ```

   The path given to `GCC_PATH` **must not contain spaces** (the Makefile does not quote compiler paths), so on Windows the default install directory should be used via PATH, not via `GCC_PATH`.

   Newer versions (such as 14.x) usually build too; if installing the Arm build is inconvenient, the portable [xPack ARM Embedded GCC](https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases) can be used instead.

2. **GNU Make** (3.81 or later; tested with 4.2.1 in this project)

    - **Linux**
      - Debian / Ubuntu:
        ```bash
        sudo apt install make # or build-essential
        ```
      - Fedora / RHEL:
        ```bash
        sudo dnf install make
        ```
      - Arch:
        ```bash
        sudo pacman -S make # or build-essential
        ```

    - **macOS**
      - The bundled GNU Make is enough:
        ```bash
        xcode-select --install
        ```
      - To install a newer version with Homebrew:
        ```bash
        brew install make
        ```
        The command is then named `gmake`.

    - **Windows**: pick one, then reopen the terminal
      - **MSYS2**
        Install MSYS2 from <https://www.msys2.org/>, then run in an MSYS2 terminal:
        ```bash
        pacman -S mingw-w64-ucrt-x86_64-make
        ```
        Then add "C:\msys64\ucrt64\bin" to PATH; the command is named `mingw32-make`.
      - **Standalone MinGW-w64 distribution**
        For example the [WinLibs](https://winlibs.com/) zip ships `mingw32-make.exe`; extract it and add its bin directory to PATH.

      Git for Windows only provides a shell and does not include `make`; install it separately using one of the methods above.


3. **Verify the installation**:

  - gcc
    ```bash
    arm-none-eabi-gcc --version    # should print 13.3.1
    ```

  - make
    ```bash
    make --version           # Linux / macOS
    mingw32-make --version   # Windows
    ```

   Usually, on Windows, if the installed executable is named mingw32-make.exe, every `make` command must be replaced with `mingw32-make`. On Windows, if the installed executable is named make.exe, just write `make` directly.

4. **Flashing and debugging tools (optional)**
   - pyocd, openocd and J-Link all work; this project only produces firmware and is not tied to a specific debugger.
   - See [VSCode Programming and Debugging Platform](docs/vscode.en.md) for details.

## Building

From the command line:

```bash
make            # Linux / macOS / MSYS2
mingw32-make    # Windows, when using mingw32-make
```

Outputs go to build/:

```
build/aaa_generic_project_name.elf
build/aaa_generic_project_name.hex
build/aaa_generic_project_name.bin
build/aaa_generic_project_name.map
```

Other targets:

```bash
make clean      # remove build/
make size       # show Flash / RAM usage
```

build/ is listed in .gitignore; build artifacts are not committed.

Verified on arm-none-eabi-gcc 13.3.1 (arm-gnu-toolchain-13.3.rel1) + GNU Make: a from-scratch make produces .elf / .hex / .bin.

Two kinds of messages may appear at link time; neither affects execution:

- `_close/_read/_write ... is not implemented and will always fail`:
  from newlib's libnosys, meaning file IO is not implemented. Unreferenced parts are discarded by --gc-sections; implement _write yourself if you need printf.
- `has a LOAD segment with RWX permissions`:
  the .data section in the official linker script occupies both Flash and RAM, which newer binutils warns about; safe to ignore.

## Runtime Behavior

User/main.c creates one LED task that toggles PB2 every 500 ms. Adjust for your board:

```c
#define LED_RCU   RCU_GPIOB
#define LED_PORT  GPIOB
#define LED_PIN   GPIO_PIN_2
```

With no LED available, use a debugger to inspect SystemCoreClock (120 MHz by default) or single-step directly.

## Switching MCU / Board (Manual)

Switching devices requires no Python, no device pack and no VSCode: the needed startup files and linker scripts already ship with the official library under GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/, so only the `Makefile` needs to change.

### 1. Determine the density class

For GD32F30xxR, the R denotes Flash capacity; for example, `GD32F303VC`'s `C` is 256 KiB:

| Letter | B | C | E | G | I | K |
|--------|---|---|---|---|---|---|
| Flash | 128K | 256K | 512K | 1M | 2M | 3M |

The density macro is chosen by Flash size (refer to the device datasheet):

| Flash size | Density macro | Startup file |
|------------|---------------|--------------|
| ≤ 64 KiB | `GD32F30X_CL` | `startup_gd32f30x_cl.S` |
| ≤ 512 KiB | `GD32F30X_HD` | `startup_gd32f30x_hd.S` |
| > 512 KiB | `GD32F30X_XD` | `startup_gd32f30x_xd.S` |

The official library provides linker scripts under .../Source/GCC/Ld/ in this project:

```
gd32f303x{B,C,E,G,I,K}_flash.ld
gd32f305x{B,C,E,G}_flash.ld
gd32f307x{C,E,G}_flash.ld
```

Devices for which the official PDSC declares no density macro (currently GD32F305/307) are also classified by the table above.

### 2. Change four places in the Makefile

| Variable | Purpose | Project default |
|----------|---------|-----------------|
| `TARGET` | Output file name | aaa_generic_project_name |
| `C_DEFS` | Density macro | -DGD32F30X_HD |
| `ASM_SOURCES` | Startup file | startup_gd32f30x_hd.S |
| `LDSCRIPT` | Linker script | gd32f303xC_flash.ld |

`TARGET` is unrelated to the device model and needs no change when switching MCUs; change it only if you want a different artifact name.

**Example: switching to a `GD32F303VG` MCU**:

**Change the output file name**
```diff
-TARGET    = aaa_generic_project_name
+TARGET    = new_project_name
```

**Adjust the density macro**
```diff
-C_DEFS = -DUSE_STDPERIPH_DRIVER -DGD32F30X_HD
+C_DEFS = -DUSE_STDPERIPH_DRIVER -DGD32F30X_XD
```

**Adjust the linker script**
```diff
-LDSCRIPT = GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/gd32f303xC_flash.ld
+LDSCRIPT = GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/gd32f303xG_flash.ld
```

**Adjust the startup file**
```diff
ASM_SOURCES = \
-  GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/startup_gd32f30x_hd.S
+  GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/startup_gd32f30x_xd.S
```

### 3. Verify Flash / RAM in the linker script

Open the file that `LDSCRIPT` points to and confirm that ORIGIN / LENGTH in MEMORY match the device.
If no matching *.ld script exists, copy a script of the same density class into a project-owned directory (for example User/), then modify
ORIGIN / LENGTH there and point `LDSCRIPT` at the copy; do not modify the official files under GD32F30x/.

### 4. System clock and crystal

The default configuration is in GD32F30x/CMSIS/GD/GD32F30x/Source/system_gd32f30x.c:
__SYSTEM_CLOCK_120M_PLL_HXTAL is currently selected, and the external high-speed crystal is assumed to be 8 MHz.

- To change the clock: switch the `__SYSTEM_CLOCK_*` macro at the top of that file, and update
  `configCPU_CLOCK_HZ` in User/FreeRTOSConfig.h accordingly;
- If the on-board crystal is not 8 MHz: add
  -DHXTAL_VALUE=<frequency> to `C_DEFS` in the Makefile (for example -DHXTAL_VALUE=12000000); do not modify the official headers.

### 5. Rebuild and verify

```bash
make clean && make
make size
```

Confirm the artifact is build/<TARGET>.elf and that Flash / RAM usage does not exceed the device capacity.

**Optional**: if you use VSCode, also sync `targetId`, `svdFile` and the density macro under .vscode/, see [VSCode Programming and Debugging Platform](docs/vscode.en.md).

> To perform the Makefile changes above with a script (and update `.vscode/` and the SVD along the way),
> see [VSCode Programming and Debugging Platform](docs/vscode.en.md). The manual, script-free flow is this section.

## FreeRTOS Configuration Highlights

- Preemptive scheduling, 1 kHz tick, 5 priorities
- heap_4 dynamic allocation, 8 KB heap (configTOTAL_HEAP_SIZE)
- GCC port: portable/GCC/ARM_CM4F
- Exception handling: FreeRTOSConfig.h maps `vPortSVCHandler/xPortPendSVHandler/xPortSysTickHandler` to `SVC_Handler/PendSV_Handler/SysTick_Handler`, so User/gd32f30x_it.c must not define these three functions.
- Hardware floating point: `-mfpu=fpv4-sp-d16 -mfloat-abi=hard`; the FPU is enabled by the FreeRTOS port when the scheduler starts
- Stack overflow check: `configCHECK_FOR_STACK_OVERFLOW 2`; on overflow, vApplicationStackOverflowHook() in User/freertos_hooks.c is entered, which disables interrupts and loops forever, making it easy for a debugger to locate

## Project Conventions

- Files under `GD32F30x/` and `FREERTOS/` stay exactly as shipped by the vendor; no local files are added there. If a patch is needed, first record in [UPSTREAM.md](UPSTREAM.md) what was changed and why.
- New code goes in `User/` and is added to C_SOURCES / C_INCLUDES in the Makefile.
- When upgrading a third-party library, replace the directory as a whole and re-check the version table in this README.
- build/, packs/, svd/ and .vscode/settings.json are not version-controlled.
- packs/ and svd/ are generated by the optional device scripts and must not be redistributed; the SVD is only used for the debugger's peripheral register view and does not participate in compilation.
- Only cross-platform configuration is committed under .vscode/ (tasks.json, c_cpp_properties.json, extensions.json, launch.json).

## Optional Extensions (Not Required to Build)

The following do not affect the `make` build; read as needed:

| Content | Document | Description |
|---------|----------|-------------|
| VSCode programming and debugging platform | [docs/vscode.en.md](docs/vscode.en.md) | Build tasks, IntelliSense, device packs, flashing, F5 debugging, device switching scripts |

## License

- This project's own code (User/, Makefile, documentation) is MIT, see [LICENSE](LICENSE).
- GD32F30x/ is licensed software from GigaDevice (its startup files and linker scripts are Apache-2.0), and FREERTOS/ is MIT. Full details in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); please keep these files when redistributing.
