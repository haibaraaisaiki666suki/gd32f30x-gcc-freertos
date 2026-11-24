# Third-Party Notices

This repository contains third-party software. This file lists the origin, version, license, and repository path of each component.

This file is not legal advice. Before commercial use or redistribution, read the full license text of each component.

---

## 1. GD32F30x Firmware Library V3.0.3

| Item | Details |
|------|---------|
| Upstream repository | https://github.com/GigaDevice-GD32-MCU/GD32F30x_Firmware_Library |
| Version | V3.0.3, Git tag `3.0.3` |
| How obtained | Copied as-is after extracting the release archive for the upstream tag (2026-11-23) |
| Path in this repository | `GD32F30x/` |
| Modified? | No. File contents match upstream; files were only relocated into the directory structure |
| License | See `GD32F30x/LICENSE` |

### License notes

- The root `LICENSE` of the upstream release archive is the **GigaDevice Software License Agreement (SLA-GD0001-version1.1)**. This repository preserves it as-is at `GD32F30x/LICENSE`.
- Source files, header files, and startup files in the library additionally carry a **BSD-3-Clause** copyright notice (Copyright (c) GigaDevice Semiconductor Inc.). Both licenses are present and apply as stated in each individual file.
- The linker script and startup file are derived from Arm's CMSIS templates, and their file headers state **Apache-2.0**.

### Redistribution notes

Section 2 of the SLA permits redistribution in source form, but requires that any redistribution reproduce the copyright notice, restrictions, disclaimer, export control and compliance statements in documentation or accompanying materials, and that the licensed software may only run on chips manufactured by GigaDevice (or its contract manufacturers).

This repository satisfies the reproduction requirement by retaining the full text of `GD32F30x/LICENSE`. **If you redistribute this repository or publish a derivative project, please keep this file as well.**

For the complete terms, read `GD32F30x/LICENSE` directly.

---

## 2. FreeRTOS-Kernel V10.5.1

| Item | Details |
|------|---------|
| Upstream repository | https://github.com/FreeRTOS/FreeRTOS-Kernel |
| Version | V10.5.1, Git tag `V10.5.1` |
| How obtained | Copied as-is after extracting the release archive for the upstream tag (2026-11-23) |
| Path in this repository | `FREERTOS/` |
| Modified? | No |
| License | MIT, see `FREERTOS/LICENSE.md` |

### Files included

```
FREERTOS/tasks.c
FREERTOS/queue.c
FREERTOS/list.c
FREERTOS/timers.c
FREERTOS/event_groups.c
FREERTOS/stream_buffer.c
FREERTOS/croutine.c
FREERTOS/include/*.h
FREERTOS/portable/GCC/ARM_CM4F/port.c
FREERTOS/portable/GCC/ARM_CM4F/portmacro.h
FREERTOS/portable/MemMang/heap_4.c
FREERTOS/LICENSE.md
```

Parts of the upstream repository that are irrelevant to this project (ports for other architectures, other memory management schemes, tests, and documentation) were not included.

`User/FreeRTOSConfig.h` is **this project's configuration file** and is not FreeRTOS upstream code.

---

## 3. GCC startup file and linker script

| Item | Details |
|------|---------|
| Origin | GD32F30x Firmware Library V3.0.3 (same as above) |
| Paths in this repository | `GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/startup_gd32f30x_hd.S` (startup file); `GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/gd32f303xC_flash.ld` (linker script) |
| Modified? | No |
| License | Apache-2.0 (stated in the file headers) |

These two files were brought in as part of the entire `GD32F30x/` directory, with no renaming or modification.

---

## 4. GD32F30x SVDs (generated locally, not distributed with the repository)

| Item | Details |
|------|---------|
| Origin | GigaDevice.GD32F30x_DFP 2.6.0 (released 2025-08-20), `SVD/*.svd` inside the pack |
| How obtained | `tools/fetch_pack.py` extracts all SVDs from a pack that the user downloads from the official source (`make debug-setup`), then `tools/select_device.py` selects one for the current device |
| Path in this repository | None. Generated into `svd/`, which is listed in `.gitignore` |
| Modified? | No |
| Purpose | Only for displaying peripheral registers in Cortex-Debug; not involved in firmware compilation |
| License | GigaDevice **SLA-GD0006-version1.1** (`LICENSE` at the root of the `GigaDevice-GD32-MCU/GD32F30x_Addon` repository) |

Section 2 of that SLA grants only the right to use and copy the software for designing and developing products, and Section 4(1) prohibits redistribution of the Licensed Software in any form (in whole or in part). Therefore this repository **does not include** these SVDs, nor does it include the DFP device pack; both are downloaded, extracted, and used locally by the user only, and only in conjunction with chips manufactured by GigaDevice (or its contract manufacturers).

The PDSC inside the device pack has no `<license>` element; the license terms are governed by the `LICENSE` at the root of the Addon repository, and the PDSC cannot be cited as the basis of authorization.

---

## 5. Code original to this project

The project code under `User/`, the `Makefile`, and the documentation were written by the authors of this repository and are licensed under MIT; see [LICENSE](LICENSE).

The MIT license covers only the original code described above. It **does not cover** the third-party files in `GD32F30x/` and `FREERTOS/`, nor does it apply to the `packs/` and `svd/` content that the user generates locally.
