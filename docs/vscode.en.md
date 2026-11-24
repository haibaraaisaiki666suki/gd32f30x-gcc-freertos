[简体中文](vscode.md) | English

# Optional: VSCode Programming and Debugging Platform

> **Optional content**: this page collects the VSCode project configuration, device packs, flashing/debugging and device switching scripts.
> Firmware building only depends on `arm-none-eabi-gcc` + GNU Make; `.vscode/`, `tools/`, `packs/` and `svd/`
> do not participate in `make`, and deleting or skipping them does not affect the firmware artifacts.
>
> For the manual device-switching flow that needs neither VSCode nor scripts, see
> [the README's "Switching MCU / Board (Manual)"](../README.en.md#switching-mcu--board-manual).
> Neither `packs/` nor `svd/` is checked in, and neither should be forwarded in the project archive.

## Environment Setup

Using the VSCode platform described on this page to build, flash and debug requires the following tools:

| Tool | Purpose | Notes |
|------|---------|-------|
| ARM GNU Toolchain | Cross-compilation | See [README's Environment Setup](../README.en.md#environment-setup) |
| GNU Make | Build | See [README's Environment Setup](../README.en.md#environment-setup) |
| Python 3.8+ | Run the `.py` scripts in `tools/` | The command may be `python` or `python3`; throughout this page we write `python` |
| pyOCD | Flashing and debugging | Installed via Python, see the command below |
| VSCode | Editor | The main editing and debugging window |
| ms-vscode.cpptools | C/C++ language support | A VSCode extension (plugin) |
| marus25.cortex-debug | Debugger support | A VSCode extension (plugin) |
| Git for Windows | Conveniently run make build tasks (Windows only) | VSCode for Windows often fails to detect environment variables in the default terminal; use the bash bundled with Git instead |
| curl | Manually download the device pack (optional) | Used when not downloading via script, see "Manually downloading the pack" |

Hardware: a PWLINK2 debug probe (CMSIS-DAP compatible, recognized directly by pyOCD).

### Installation

**ARM GNU Toolchain**

See [README's Environment Setup](../README.en.md#environment-setup)

**GNU Make**

See [README's Environment Setup](../README.en.md#environment-setup)

**Python 3.8+**

- Windows: download and install from [python.org](https://www.python.org/downloads/), and check
  **Add python.exe to PATH**.
- macOS: use the python.org installer, or `brew install python`.
- Linux: `sudo apt install python3 python3-pip` (or the equivalent for your distribution).

The command name may be `python3`: replace `python` below with `python3`, and when using Make write
`make debug-setup PYTHON=python3`.

**pyOCD**

```bash
python -m pip install pyocd
```

On Linux, if the probe is not found or permission is denied, configure udev rules as described in the
[pyOCD documentation](https://pyocd.io/docs/installing.html).

**VSCode**

Install from [code.visualstudio.com](https://code.visualstudio.com/). After opening this project,
`.vscode/extensions.json` will prompt you to install the recommended extensions; you can also install
`ms-vscode.cpptools` and `marus25.cortex-debug` manually, then reload the window.

**Git for Windows**

Download and install from [git-scm.com](https://git-scm.com/download/win), keeping the default path
`C:\Program Files\Git` (the build tasks run through its `bin\bash.exe`); if installed elsewhere,
change `shell.executable` in `.vscode/tasks.json`.

**curl (optional)**

Windows 10/11, Linux and macOS usually ship with it; only needed for "Manually downloading the pack".

After installation, verify:

```bash
arm-none-eabi-gcc --version   # should print 13.3.1
make --version                # Windows: mingw32-make --version
python --version              # requires 3.8 or newer
pyocd --version
```

The device pack is obtained in step 1 of the "Full Workflow". If you only want to build and flash from the command line without installing
VSCode, you can skip the editor-related tools and use the OpenOCD / J-Link commands instead (see "Other Debuggers").

## Full Workflow

Starting from an empty project, follow the steps below in order. For day-to-day code changes, jump straight to step 3.

### 1. Extract the device pack and SVDs

In the project directory, or after opening VSCode from that directory, run in a terminal:

```bash
make debug-setup        # Windows: mingw32-make debug-setup
```

The script downloads and verifies `GigaDevice.GD32F30x_DFP 2.6.0` and extracts all SVDs from the pack into `svd/`.
Repeated runs have no side effects. Details in [Device Pack and SVD](#device-pack-and-svd).

### 2. Switch device

First decide on the device, then in the project directory, or after opening VSCode from that directory, run in a terminal:

```bash
make select-device DEVICE=GD32F303VC    # replace with the device you actually use
```

The script reads the device pack and updates the Makefile's density macro, startup file and linker script, while syncing
`.vscode/launch.json`, `.vscode/c_cpp_properties.json` and the selected SVD in `svd/`.
You can also run it when the device is unchanged, to confirm the configuration is consistent. Details in [Automatic Device Switching](#automatic-device-switching).

### 3. Build

The bundled `.vscode/tasks.json` binds the default build action to `Ctrl+Shift+B`;
in VSCode press `Ctrl+Shift+B`, or from the command line:

```bash
make            # Windows: mingw32-make
```

Outputs are `build/<TARGET>.elf`, `.hex`, `.bin`. Details of the build task are in
[VSCode Project Configuration](#vscode-project-configuration).

Use the clean command to remove artifacts:

```bash
make clean           # Windows: mingw32-make clean
```

### 4. Flash and debug

The bundled `.vscode/launch.json` binds debugging to `F5`; with a PWLINK2 probe connected, press `F5` in VSCode to start Cortex-Debug + pyOCD; after pausing you can inspect core registers and
peripheral registers. You can also flash from the command line first:

```bash
pyocd flash --pack packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
            -t gd32f303vc build/aaa_generic_project_name.elf
```

Details in [Flashing](#flashing) and [Debugging](#debugging).

## Configuration Details

### Device Pack and SVD

pyOCD needs the GD32F30x device pack for the memory map, Flash algorithms and SVD. This project uses the official
**GigaDevice.GD32F30x_DFP 2.6.0** (released 2025-08-20), with the default path:

```
packs/GigaDevice.GD32F30x_DFP.2.6.0.pack
```

> **License notice**: this DFP is licensed by GigaDevice under **SLA-GD0006-version1.1**
> (see [the Addon repository's LICENSE](https://github.com/GigaDevice-GD32-MCU/GD32F30x_Addon/blob/main/LICENSE));
> it may only be used for development with GigaDevice chips and redistribution is prohibited. Downloading or using the pack means accepting that agreement.
> Do not commit `packs/` or `svd/` to a repository, and do not forward them in the project archive; this repository does not contain
> the device pack and does not distribute the SVDs extracted from it.

#### fetch_pack.py: download, verify and extract all SVDs

The script will:

1. Download `GigaDevice.GD32F30x_DFP.2.6.0.pack` from GigaDevice's `GD32F30x_Addon` repository;
2. Verify the SHA-256 (also checking zip integrity and the version declared in the PDSC);
3. Extract all `SVD/*.svd` from the pack into `svd/`;
4. Skip the download if the file already exists and passes verification; repeated runs have no side effects.

```bash
python tools/fetch_pack.py
# or
make debug-setup            # Windows: mingw32-make debug-setup
```

On systems that only provide `python3`, replace `python` with `python3`; when using Make,
`make debug-setup PYTHON=python3`.

| Option | Description |
|--------|-------------|
| `--force` | Overwrite files that exist but fail verification |
| `--url URL` | Use a mirror or another download source |
| `--dest PATH` | Specify where to save the pack |
| `--svd-dir DIR` | Specify the SVD output directory (default `svd/`) |
| `--no-svd` | Only download and verify the pack, do not extract SVDs |

#### Manually downloading the pack

The script is not required. You can also download manually and let the script verify it:

- Repository directory:
  <https://github.com/GigaDevice-GD32-MCU/GD32F30x_Addon/tree/main/Keil/Keil5>
- Direct link:
  <https://raw.githubusercontent.com/GigaDevice-GD32-MCU/GD32F30x_Addon/main/Keil/Keil5/GigaDevice.GD32F30x_DFP.2.6.0.pack>
- Save as: `packs/GigaDevice.GD32F30x_DFP.2.6.0.pack`
- Then run `python tools/fetch_pack.py` once to verify it and extract all SVDs.

Command-line download:

```bash
mkdir -p packs
curl -L -o packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
  https://raw.githubusercontent.com/GigaDevice-GD32-MCU/GD32F30x_Addon/main/Keil/Keil5/GigaDevice.GD32F30x_DFP.2.6.0.pack
```

SHA-256 (verify with `sha256sum` or `certutil -hashfile`):

```
ef90301be96d0607cf3ed46742d9b08a68ad7e4b07b2259b5f9062d45feabe78
```

#### About SVDs

- `make debug-setup` extracts all `SVD/*.svd` from the pack into `svd/`;
- which one is currently used for debugging is determined by `svdFile` in `launch.json`;
- `svd/` does not participate in compilation and is not distributed with the repository.

### Automatic Device Switching

`select_device.py` reads device attributes from the pack's PDSC device database and automatically updates:

| File | What is changed |
|------|-----------------|
| `Makefile` | `C_DEFS` density macro, startup file, `LDSCRIPT` (`TARGET` is not changed) |
| `.vscode/launch.json` | `executable`, `targetId`, `svdFile` |
| `.vscode/c_cpp_properties.json` | Configuration name, density macro |
| `svd/` | SVD for the selected device; extracted from the pack if missing |

The Makefile changes directly determine the firmware; `.vscode/` and the SVD only affect the editing and debugging experience.
If you don't want the script to modify `.vscode/`, apply only the Makefile part manually (see
[the README's manual flow](../README.en.md#switching-mcu--board-manual)).

```bash
python tools/select_device.py --list          # list devices supported by the pack
python tools/select_device.py GD32F303VE      # switch device
python tools/select_device.py GD32F307VC --dry-run
python tools/select_device.py GD32F303VE --pack path/to/dfp.pack
# or
make select-device DEVICE=GD32F303VE
```

- `--list`: list devices with their `define`, Flash size and SVD;
- `--dry-run`: only print the changes that would be made, write nothing;
- `--pack`: specify the pack path (defaults to 2.6.0 under `packs/`).

Rebuild after switching:

```bash
make clean && make        # Windows: mingw32-make clean && mingw32-make
```

For devices whose PDSC declares no `compile`/`debug` (currently GD32F305/307), the density class is inferred from
Flash size, and the output notes `inferred from flash size`. For the equivalent manual steps see
[the README's "Switching MCU / Board (Manual)"](../README.en.md#switching-mcu--board-manual).

### VSCode Project Configuration

#### Committed configuration

The repository commits only cross-platform project-level configuration:

- `tasks.json`: build, clean, show size;
- `c_cpp_properties.json`: IntelliSense header paths and macros;
- `extensions.json`: recommended extensions `ms-vscode.cpptools`, `marus25.cortex-debug`;
- `launch.json`: Cortex-Debug + pyOCD debug configuration.

Personal settings go in `.vscode/settings.json`, which is not version-controlled.

#### Build tasks

- `Ctrl+Shift+B`: build (default task);
- `Ctrl+Shift+P` → `Tasks: Run Task`: `rebuild` / `clean` / `size`;
- Build errors appear in the Problems panel (`$gcc` problem matcher).

Tasks switch automatically by platform: `make` on Linux/macOS, and `mingw32-make` on Windows executed through
Git Bash. On Windows the default assumes Git is installed at `C:\Program Files\Git`
(via `${env:ProgramFiles}`); if installed elsewhere, change `shell.executable` in `.vscode/tasks.json`.

#### IntelliSense

[c_cpp_properties.json](../.vscode/c_cpp_properties.json) is the separate configuration for the C/C++ extension; it
**does not participate in compilation**, but must stay consistent with the Makefile:

- `name`: the current device name;
- `defines`: `USE_STDPERIPH_DRIVER` and the density macro, e.g. `GD32F30X_HD`.

When switching devices manually, besides the Makefile you must also sync the density macro here; otherwise the editor
will parse peripheral headers as the wrong device (bogus errors, wrong completions). Running `select_device.py` syncs it
automatically (see [Automatic Device Switching](#automatic-device-switching)).

### Flashing

#### Command line (pyOCD)

```bash
pyocd flash --pack packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
            -t gd32f303vc build/aaa_generic_project_name.elf
```

`-t` is pyOCD's targetId; change it to the lowercase device name when switching devices.
The artifact name comes from `TARGET` in the Makefile; update the path here if you rename it.

#### Other debuggers

```bash
# OpenOCD (the target config varies by OpenOCD version; may be gd32f30x.cfg or stm32f30x.cfg)
openocd -f interface/cmsis-dap.cfg -f target/stm32f30x.cfg \
        -c "program build/aaa_generic_project_name.hex verify reset exit"

# J-Link
JLinkExe -device GD32F303VC -if SWD -speed 4000
```

### Debugging

VSCode debugs with Cortex-Debug + pyOCD (`F5`). `extensions.json` recommends installing
`marus25.cortex-debug`, and `launch.json` is already configured with:

```json
"cmsisPack": "${workspaceFolder}/packs/GigaDevice.GD32F30x_DFP.2.6.0.pack",
```

Cortex-Debug turns this into `pyocd gdbserver --pack ...`, so `pyocd pack install` is not needed, nor is
2.6.0 required in pyOCD's pack index.

Press `F5` to start debugging; after pausing you can view:

- CORTEX REGISTERS: core registers;
- CORTEX PERIPHERALS: peripheral registers, read from the SVD referenced by `svdFile`.

When switching devices, update `targetId` and `svdFile` in `launch.json`, or run
`select_device.py` to handle it automatically (see [Automatic Device Switching](#automatic-device-switching)). The 2.6.0 pack
covers the whole GD32F30x series.

## Changing the Probe

The default configuration uses a PWLINK2 (CMSIS-DAP compatible) probe with pyOCD. Changing the probe only affects the
flashing and debugging path; the `make` build, linker script and density macros do not depend on the probe, so the
firmware does not need to be rebuilt.

### Identify the probe type first

| New probe | Configuration changes |
|-----------|-----------------------|
| Another CMSIS-DAP compatible probe (DAP-Link, GD-Link, etc.) | pyOCD usually detects it directly; only change `name` in `launch.json` |
| J-Link | Change `servertype` and `device`, remove pyOCD-specific fields |
| ST-Link | Use `stutil` or switch to OpenOCD |
| Anything else | Use OpenOCD and configure `configFiles` |

Check whether the tools can see the new probe before going further; if not, stop troubleshooting on the pyOCD side:

```bash
pyocd list
```

### Wiring and power

- Check the pinout of the new probe, especially `SWDIO`, `SWCLK`, `GND` and `VTref/3V3`; connect `NRST` as well if
  available.
- Probes such as J-Link use `VTref` to detect the target voltage. With only the three signal wires connected, the tool
  may report that the target is unpowered. The target board must have its own supply.
- Some probes output 3.3 V on the 3.3 V pin. Do not connect it while the board is independently powered, to avoid
  back-feeding.
- Keep SWD wires short (under 20 cm) and connect GND before the signal lines.
- Connect only one probe at a time. Unplug the old probe before connecting the new one so the tool cannot pick the wrong
  device.

### Editing launch.json

In [.vscode/launch.json](../.vscode/launch.json), `targetId`, `cmsisPack` and `overrideGDBServerStartedRegex` are
pyOCD-specific fields; remove or ignore them when switching server types. `svdFile` is independent of the probe and
should always be kept.

**Still pyOCD (a different CMSIS-DAP probe)**

Only the display name needs to change:

```jsonc
"name": "Debug (pyOCD / new probe name)",
```

With a single probe, nothing else is required. When several probes are connected, look up the UID with `pyocd list`
and add:

```jsonc
"serverArgs": ["-u", "<probe UID>"]
```

**J-Link**

```jsonc
"servertype": "jlink",
"device": "GD32F303VC",
"interface": "swd",
```

`device` is the uppercase device name from J-Link's device database. When several J-Link probes are connected, add
`"serialNumber": "<serial>"`. The flashing command becomes:

```bash
JLinkExe -device GD32F303VC -if SWD -speed 4000
```

**ST-Link**

Use `"servertype": "stutil"` in Cortex-Debug, or switch to OpenOCD. Clone ST-Link probes may trigger a firmware
version check; upgrading them risks bricking the probe, so prefer OpenOCD if it works.

**OpenOCD**

```jsonc
"servertype": "openocd",
"configFiles": ["interface/cmsis-dap.cfg", "target/gd32f30x.cfg"],
"searchDir": ["<OpenOCD scripts directory>"],
```

The target config depends on the OpenOCD version; some releases only ship `target/stm32f30x.cfg` (see
[Other debuggers](#other-debuggers)). OpenOCD's STM32F30x driver may not detect GD32 flash size and protection bits
correctly; specify them manually if needed.

### GD32-specific considerations

- **SWD pin reuse**: if the firmware configures `PA13`/`PA14` as plain GPIO, the probe may fail to attach after reset.
  Use "connect under reset" and make sure `NRST` is connected.
- **Readout protection/option bytes**: if the chip was locked by another tool, the new tool will request an unlock or a
  full-chip erase. A full erase wipes the existing firmware, so confirm before proceeding.
- **BOOT0**: booting from flash requires BOOT0 to be low.
- **Low power**: the FreeRTOS idle task enters WFI, which normally does not affect SWD. If attaching is unreliable, try
  "connect under reset" first and lower the clock.

### Speed and verification

Start at a low speed (1–2 MHz) and increase it gradually. Speed settings: `serverArgs: ["-f", "1M"]` for pyOCD,
`-speed 1000` for J-Link, and `adapter speed` for OpenOCD.

Verify in this order:

```bash
pyocd list                          # detect the probe
pyocd flash --pack packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
            -t gd32f303vc build/aaa_generic_project_name.elf
pyocd reset                         # confirm the program is running
```

Then press `F5`, set a breakpoint in `main`, and confirm you can pause, single-step, and read peripheral registers in
CORTEX PERIPHERALS.

### Documentation to update after a permanent change

- The `name`, `servertype`, `device` and related fields in [.vscode/launch.json](../.vscode/launch.json);
- The hardware note in [Environment Setup](#environment-setup), and the commands and descriptions in
  [Flashing](#flashing) and [Debugging](#debugging);
- The command-line flashing examples (`pyocd flash` / `JLinkExe` / `openocd`).
