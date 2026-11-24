# Upstream Record

This file records the origin, scope, and upgrade procedure for the `GD32F30x/` and `FREERTOS/` directories, to make later verification and upgrades easier.

The `GD32F30x/` and `FREERTOS/` directories contain **only upstream files**, with no files added by this project. This lets you compare them directly against upstream source packages with `diff -r` to confirm there are no local changes.

```bash
diff -r --strip-trailing-cr <upstream extract dir>/Firmware/CMSIS GD32F30x/CMSIS
diff -r --strip-trailing-cr <upstream extract dir>/Firmware/GD32F30x_standard_peripheral GD32F30x/GD32F30x_standard_peripheral
diff -r --strip-trailing-cr <FreeRTOS upstream extract dir>/include FREERTOS/include
```

---

## 1. GD32F30x Firmware Library

### Origin

| Item | Details |
|------|---------|
| Repository | https://github.com/GigaDevice-GD32-MCU/GD32F30x_Firmware_Library |
| Version | V3.0.3 |
| Git tag | `3.0.3` |
| Date obtained | 2026-11-23 |
| How obtained | Downloaded the source archive for the tag (tar.gz packaged by `codeload.github.com`), extracted it, and copied the files |

### Scope included

The extracted upstream source archive has the root directory `GD32F30x_Firmware_Library-3.0.3/`.

| Upstream path | Path in this repository | Description |
|---------------|-------------------------|-------------|
| `Firmware/CMSIS/` | `GD32F30x/CMSIS/` | CMSIS core files, GD32F30x system clock, ARM/IAR/GCC startup files, GCC linker scripts for each device |
| `Firmware/GD32F30x_standard_peripheral/` | `GD32F30x/GD32F30x_standard_peripheral/` | Standard peripheral library, 24 `.c` files and their corresponding headers |
| `LICENSE` (taken from the `main` branch) | `GD32F30x/LICENSE` | See the note below |
| `Template/gd32f30x_libopt.h` | `User/gd32f30x_libopt.h` | Aggregate header for peripheral headers; it is project configuration, so it is not inside `GD32F30x/` |

### Not included

`Doc/`, `Examples/`, `Utilities/`, `Firmware/GD32F30x_usbd_library/`, `Firmware/GD32F30x_usbfs_library/`, and the remaining files in `Template/` (`.uvprojx`, Keil/IAR projects, etc.).

If you need the USB libraries or examples, copy them from the official package in the same way as shown in the table above.

### About the LICENSE

The root of the `3.0.3` tag source archive has **no** `LICENSE` file (only `Doc/`, `Examples/`, `Firmware/`, `Template/`, `Utilities/`). The `GD32F30x/LICENSE` in this repository was taken from the release archive of the upstream `main` branch from the same period; its content is the GigaDevice Software License Agreement (SLA-GD0001-version1.1).

After an upstream upgrade, if the tag archive includes its own `LICENSE`, the one inside the tag archive takes precedence.

### About `gd32f30x_it.c` from Template

The official `Template/gd32f30x_it.c` defines empty implementations of `SVC_Handler`, `PendSV_Handler`, and `SysTick_Handler`, whereas in this project these three exceptions are provided by the FreeRTOS GCC port; defining both would cause a link conflict. Therefore that file was **not** included; the project's `User/gd32f30x_it.c` keeps only the necessary interrupt handlers.

### Modification record

There are currently **no** modifications to upstream files, confirmed with `diff -r` against the tag source archive.

If a patch is genuinely needed, record it here item by item: the file, the reason, the patch content, and the corresponding upstream issue/PR (if any). These patches must be re-evaluated when upgrading upstream.

### Upgrade procedure

```bash
VERSION=3.0.4        # change to the target tag
curl -L -o gd32.tar.gz \
  "https://codeload.github.com/GigaDevice-GD32-MCU/GD32F30x_Firmware_Library/tar.gz/refs/tags/${VERSION}"
mkdir -p /tmp/gd32_upgrade
tar -xzf gd32.tar.gz -C /tmp/gd32_upgrade

rm -rf GD32F30x/CMSIS GD32F30x/GD32F30x_standard_peripheral
cp -a /tmp/gd32_upgrade/GD32F30x_Firmware_Library-${VERSION}/Firmware/CMSIS GD32F30x/
cp -a /tmp/gd32_upgrade/GD32F30x_Firmware_Library-${VERSION}/Firmware/GD32F30x_standard_peripheral GD32F30x/
```

After upgrading, check:

1. Whether the `LDSCRIPT` path in the `Makefile` is still under `CMSIS/GD/GD32F30x/Source/GCC/Ld/`.
2. Whether the startup file is still named `startup_gd32f30x_hd.S`.
3. Whether any peripheral API used by this project has been renamed (historically ADC/DAC/CAN/ENET were renamed between V2 and V3).
4. Rebuild and flash to verify.
5. Update the version table in [README.md](README.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

## 2. FreeRTOS-Kernel

### Origin

| Item | Details |
|------|---------|
| Repository | https://github.com/FreeRTOS/FreeRTOS-Kernel |
| Version | V10.5.1 |
| Git tag | `V10.5.1` |
| Date obtained | 2026-11-23 |
| How obtained | Downloaded the source archive for the tag, extracted it, and copied the files |

### Scope included

The extracted upstream source archive has the root directory `FreeRTOS-Kernel-10.5.1/`.

| Upstream path | Path in this repository |
|---------------|-------------------------|
| `tasks.c` `queue.c` `list.c` `timers.c` `event_groups.c` `stream_buffer.c` `croutine.c` | `FREERTOS/` |
| `include/` | `FREERTOS/include/` |
| `portable/GCC/ARM_CM4F/port.c` `portmacro.h` | `FREERTOS/portable/GCC/ARM_CM4F/` |
| `portable/MemMang/heap_4.c` | `FREERTOS/portable/MemMang/` |
| `LICENSE.md` | `FREERTOS/LICENSE.md` |

### Not included

Ports for other architectures (ARM_CM0, ARM_CM3, ARM_CM7, IAR, RVDS, etc. under `portable/`), other memory management schemes (`heap_1/2/3/5.c`), `CMakeLists.txt`, `manifest.yml`, `sbom.spdx`, tests, and documentation.

If you need to switch ports or memory schemes, copy the additional files from the official package of the same version and update `C_SOURCES` in the `Makefile` accordingly.

### Modification record

There are currently **no** modifications to upstream files.

`User/FreeRTOSConfig.h` is this project's configuration file, supplied by the application as FreeRTOS convention requires; it is not upstream code, and for that reason it lives in `User/`.

### Upgrade procedure

```bash
VERSION=10.6.0
curl -L -o freertos.tar.gz \
  "https://codeload.github.com/FreeRTOS/FreeRTOS-Kernel/tar.gz/refs/tags/V${VERSION}"
mkdir -p /tmp/freertos_upgrade
tar -xzf freertos.tar.gz -C /tmp/freertos_upgrade

rm -rf FREERTOS
mkdir -p FREERTOS/portable/GCC FREERTOS/portable/MemMang
SRC=/tmp/freertos_upgrade/FreeRTOS-Kernel-${VERSION}
cp -a "$SRC"/tasks.c "$SRC"/queue.c "$SRC"/list.c "$SRC"/timers.c \
      "$SRC"/event_groups.c "$SRC"/stream_buffer.c "$SRC"/croutine.c FREERTOS/
cp -a "$SRC"/include FREERTOS/
cp -a "$SRC"/portable/GCC/ARM_CM4F FREERTOS/portable/GCC/
cp -a "$SRC"/portable/MemMang/heap_4.c FREERTOS/portable/MemMang/
cp -a "$SRC"/LICENSE.md FREERTOS/
```

After upgrading, check:

1. Whether `FreeRTOSConfig.h` has new mandatory configuration items (the compiler will flag these with `#error`).
2. Whether the function names and exception aliases in the GCC/ARM_CM4F port have changed.
3. Rebuild and run to verify.
4. Update the version table in [README.md](README.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
