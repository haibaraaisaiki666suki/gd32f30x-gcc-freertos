简体中文 | [English](README.en.md)

# GD32F30x GCC + FreeRTOS 基线工程

[![Build](https://github.com/haibaraaisaiki666suki/gd32f30x-gcc-freertos/actions/workflows/build.yml/badge.svg)](https://github.com/haibaraaisaiki666suki/gd32f30x-gcc-freertos/actions/workflows/build.yml)

一个不依赖任何 IDE 的最小可编译工程：**GD32F30x 官方标准外设库 V3.0.3 + FreeRTOS-Kernel V10.5.1**，用 arm-none-eabi-gcc + GNU Make 构建，生成 .elf / .hex / .bin。

**可选增强**：VSCode、器件包脚本、烧录调试，见文末[可选扩展](#可选扩展非构建必需)。如不需要可删去 docs/ tools/ packs/ svd/ .vscode/ 文件夹。

第三方库文件从官方仓库原样引入，不改动；版本、来源和许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## GCC优势

**成本与自由度**
GCC 是完全免费开源的，没有 Keil MDK 那样的 32KB 代码容量限制，也无需为商用授权付费。

**跨平台与团队协作**
Keil MDK 仅支持 Windows。而 GCC 工具链可以在 Windows、Linux 和 macOS 上原生运行。这对于使用 Mac 的开发者，或需要在 Linux 服务器上进行构建的团队来说，是必需的能力。

**自动化与持续集成 (CI/CD)**
这是 GCC 最突出的优势之一。Keil 的命令行模式功能有限，很难融入自动化的构建流水线。而 GCC 天生适配 Makefile、CMake 等构建系统，可以非常顺畅地接入 GitHub Actions、GitLab CI 等持续集成环境，实现代码提交后的自动编译、单元测试和固件生成。

**工程管理的友好性**
使用 Keil 或 IAR 时，工程文件（如 .uvprojx）是难以进行差异对比的复杂格式，对 Git 等版本控制系统的支持不佳。而 GCC 方案使用纯文本的 Makefile 或 CMakeLists.txt 来管理构建，这些文件可以像源代码一样被 Git 清晰地追踪和合并，极大地简化了工程配置的版本管理。

## 目录结构

```
.
├── GD32F30x/                           GD32F30x 固件库 V3.0.3（原厂文件，不修改）
│   ├── CMSIS/                          CMSIS 内核、各型号启动文件、链接脚本、系统时钟
│   └── GD32F30x_standard_peripheral/   标准外设库（24 个 .c + 头文件）
├── FREERTOS/                           FreeRTOS-Kernel V10.5.1（原厂文件，不修改）
│   ├── include/
│   └── portable/
│       ├── GCC/ARM_CM4F/               Cortex-M4F 的 GCC 移植层
│       └── MemMang/heap_4.c
├── User/                               工程代码
│   ├── main.c                          LED 闪烁 + 建任务
│   ├── gd32f30x_it.c                   异常处理（SVC/PendSV/SysTick 归 FreeRTOS）
│   ├── freertos_hooks.c                FreeRTOS 应用钩子（栈溢出检查）
│   ├── gd32f30x_libopt.h               外设库裁剪头文件（来自官方 Template）
│   └── FreeRTOSConfig.h                FreeRTOS 配置
├── Makefile
├── UPSTREAM.md                         第三方库的来源、引入范围与升级方法
├── THIRD_PARTY_NOTICES.md
├── LICENSE
│
├── docs/
│   └── vscode.md                       可选：VSCode 编程、烧录、调试与型号脚本
├── tools/                              可选：pack 下载与型号切换脚本
├── packs/                              可选：下载的器件包（不入库）
├── svd/                                可选：本地解出的全部 SVD（不入库）
└── .vscode/                            可选：VSCode 任务与调试配置
```

## 组件版本

| 组件 | 版本 | 上游 | 许可 |
|------|------|------|------|
| GD32F30x 固件库 | V3.0.3（tag `3.0.3`） | [GigaDevice-GD32-MCU/GD32F30x_Firmware_Library](https://github.com/GigaDevice-GD32-MCU/GD32F30x_Firmware_Library) | 见 `GD32F30x/LICENSE`（GigaDevice SLA） |
| FreeRTOS-Kernel | V10.5.1（tag `V10.5.1`） | [FreeRTOS/FreeRTOS-Kernel](https://github.com/FreeRTOS/FreeRTOS-Kernel) | MIT |
| GCC 启动文件 / 链接脚本 | 随 GD32F30x V3.0.3 | 同上 | Apache-2.0（文件头注明） |
| 本工程自有代码 | — | — | MIT，见 [LICENSE](LICENSE) |

## 环境准备

1. **ARM GNU Toolchain 13.3.rel1**（arm-none-eabi-gcc 13.3.1，本工程实测版本）

   推荐直接安装 Arm 官方版。下载入口已迁至 GitLab，但二进制文件仍可直接下载：

   - Windows（x86_64）安装包：
     <https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi.exe>
   - Windows 免安装 zip：
     <https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi.zip>
   - Linux / macOS 及其他版本：<https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads>

   安装时勾选 **Add path to environment variable**。

   不想改 PATH 时，可用 `GCC_PATH` 指定工具链的 bin/：

   ```bash
   make GCC_PATH=/path/to/arm-none-eabi/bin
   ```

   `GCC_PATH` 指向的路径中**不能有空格**（Makefile 未给编译器路径加引号），因此 Windows 默认安装目录应通过 PATH 使用，不要用 `GCC_PATH`。

   更新的版本（如 14.x）通常也能编译；安装 Arm 版不方便时，也可使用便携版 [xPack ARM Embedded GCC](https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases)。

2. **GNU Make**（3.81 及以上；本工程实测 4.2.1）

    - **Linux**
      - Debian / Ubuntu：
        ```bash
        sudo apt install make # 或 build-essential 
        ```
      - Fedora / RHEL：
        ```bash
        sudo dnf install make
        ```
      - Arch：
        ```bash
        sudo pacman -S make # 或 build-essential 
        ```

    - **macOS**
      - 自带的 GNU Make 即可：
        ```bash
        xcode-select --install
        ```
      - 用 Homebrew 装新版时执行：
        ```bash
        brew install make
        ```
        命令名为 `gmake`。

    - **Windows**：任选一种，装完重开终端
      - **MSYS2**
        从 <https://www.msys2.org/> 安装 MSYS2，在 MSYS2 终端执行：
        ```bash
        pacman -S mingw-w64-ucrt-x86_64-make
        ```
        再把 "C:\msys64\ucrt64\bin" 加入 PATH；命令名是 `mingw32-make`。
      - **独立 MinGW-w64 发行版**
        如 [WinLibs](https://winlibs.com/) 的 zip，自带 `mingw32-make.exe`，解压后把其中的 bin 目录加入 PATH。

      Git for Windows 只提供 Shell，不带 `make`，需要按上面的方法单独安装。


3. **确认安装**：

  - gcc
    ```bash
    arm-none-eabi-gcc --version    # 应输出 13.3.1
    ```

  - make
    ```bash
    make --version           # Linux / macOS
    mingw32-make --version   # Windows
    ```

   通常，Windows 上如果装到的可执行文件叫 mingw32-make.exe，所有的 `make` 命令需要换成`mingw32-make`。Windows 上如果装到的可执行文件叫 make.exe，命令直接写 `make` 即可。

4. **烧录与调试工具（可选）**
   - pyocd、openocd、J-Link 均可；本工程只产出固件，不绑定具体调试器。
   - 具体步骤见 [VSCode 编程与调试平台](docs/vscode.md)。

## 编译

命令行运行：

```bash
make            # Linux / macOS / MSYS2
mingw32-make    # Windows 下用 mingw32-make 时
```

产物在 build/：

```
build/aaa_generic_project_name.elf
build/aaa_generic_project_name.hex
build/aaa_generic_project_name.bin
build/aaa_generic_project_name.map
```

其他目标：

```bash
make clean      # 删除 build/
make size       # 查看 Flash / RAM 占用
```

build/ 已在 .gitignore 中，不提交编译产物。

已在 arm-none-eabi-gcc 13.3.1（arm-gnu-toolchain-13.3.rel1）+ GNU Make 上验证：从零开始 make 可生成 .elf / .hex / .bin。

链接时可能看到两类提示，都**不影响运行**：

- `_close/_read/_write ... is not implemented and will always fail`：
来自 newlib 的 libnosys，表示没有实现文件 IO。未被引用的部分会被 --gc-sections 丢弃；需要 printf 时自行实现 _write。
- `has a LOAD segment with RWX permissions`：
官方链接脚本的 .data 段同时占 Flash 和 RAM，较新的 binutils 会提示，可忽略。

## 运行现象

User/main.c 创建一个 LED 任务，以 500 ms 周期翻转 PB2。请按自己的板子修改:

```c
#define LED_RCU   RCU_GPIOB
#define LED_PORT  GPIOB
#define LED_PIN   GPIO_PIN_2
```

没有 LED 时，可以用调试器看 SystemCoreClock（默认 120 MHz）或直接单步。

## 换芯片 / 改板（手动）

换型号不需要 Python、器件包或 VSCode：所需的启动文件和链接脚本已经随官方库放在GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/ 下，只需要改 `Makefile`。

### 1. 确认容量等级

GD32F30xxR，R 表示 Flash 容量，例如 `GD32F303VC` 的 `C` 是 256 KiB：

| 字母 | B | C | E | G | I | K |
|------|---|---|---|---|---|---|
| Flash | 128K | 256K | 512K | 1M | 2M | 3M |

容量等级宏按 Flash 大小选择（以芯片手册为准）：

| Flash 大小 | 容量宏 | 启动文件 |
|------------|--------|----------|
| ≤ 64 KiB | `GD32F30X_CL` | `startup_gd32f30x_cl.S` |
| ≤ 512 KiB | `GD32F30X_HD` | `startup_gd32f30x_hd.S` |
| > 512 KiB | `GD32F30X_XD` | `startup_gd32f30x_xd.S` |

官方库在本工程的 .../Source/GCC/Ld/ 下提供链接脚本：

```
gd32f303x{B,C,E,G,I,K}_flash.ld
gd32f305x{B,C,E,G}_flash.ld
gd32f307x{C,E,G}_flash.ld
```

官方 PDSC 未声明容量宏的型号（目前是 GD32F305/307），也按上表判断。

### 2. 修改 Makefile 的四处

| 变量 | 作用 | 本工程默认值 |
|------|------|--------------|
| `TARGET` | 输出文件名 | aaa_generic_project_name |
| `C_DEFS` | 等级宏 | -DGD32F30X_HD |
| `ASM_SOURCES` | 启动文件 | startup_gd32f30x_hd.S |
| `LDSCRIPT` | 链接脚本 | gd32f303xC_flash.ld |

`TARGET` 与芯片型号无关，换芯片时不需要修改；需要改产物名时自行修改即可。

**以`GD32F303VG`单片机为例**: 

**修改输出文件名**
```diff
-TARGET    = aaa_generic_project_name
+TARGET    = new_project_name
```

**调整等级宏**
```diff
-C_DEFS = -DUSE_STDPERIPH_DRIVER -DGD32F30X_HD
+C_DEFS = -DUSE_STDPERIPH_DRIVER -DGD32F30X_XD
```

**调整链接脚本**
```diff
-LDSCRIPT = GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/gd32f303xC_flash.ld
+LDSCRIPT = GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/gd32f303xG_flash.ld
```

**调整启动文件**
```diff
ASM_SOURCES = \
-  GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/startup_gd32f30x_hd.S
+  GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/startup_gd32f30x_xd.S
```

### 3. 核对链接脚本中的 Flash / RAM

打开 `LDSCRIPT` 指向的文件，确认 MEMORY 中的 ORIGIN / LENGTH 与芯片一致。
没有对应的 *.ld 脚本时，复制一份同容量等级的脚本到工程自有目录（例如 User/）再修改
ORIGIN / LENGTH，并把 `LDSCRIPT` 指向副本；不要改动 GD32F30x/ 中的官方文件。

### 4. 系统时钟与晶振

默认配置在 GD32F30x/CMSIS/GD/GD32F30x/Source/system_gd32f30x.c：
当前选中 __SYSTEM_CLOCK_120M_PLL_HXTAL，外部高速晶振按 8 MHz 计算。

- 改主频：切换该文件顶部的 `__SYSTEM_CLOCK_*` 宏，并同步
  User/FreeRTOSConfig.h 的 `configCPU_CLOCK_HZ`；
- 板载晶振不是 8 MHz：在 Makefile 的 `C_DEFS` 中加
  -DHXTAL_VALUE=<频率>（例如 -DHXTAL_VALUE=12000000），不要修改官方头文件。

### 5. 重新编译并验证

```bash
make clean && make
make size
```

确认产物名为 build/<TARGET>.elf，并且 Flash / RAM 占用没有超出芯片容量。

**可选**：如果使用 VSCode，还需同步 .vscode/ 中的 `targetId`、`svdFile` 和容量宏，见 [VSCode 编程与调试平台](docs/vscode.md)。

> 想用脚本自动完成以上 Makefile 修改（并顺带更新 `.vscode/` 与 SVD），
> 见 [VSCode 编程与调试平台](docs/vscode.md)。不依赖脚本的手动流程就是本节。

## FreeRTOS 配置要点

- 抢占式调度，1 kHz 节拍，5 个优先级
- heap_4 动态分配，堆大小 8 KB（configTOTAL_HEAP_SIZE）
- GCC 移植层：portable/GCC/ARM_CM4F
- 异常处理：FreeRTOSConfig.h 把 `vPortSVCHandler/xPortPendSVHandler/xPortSysTickHandler` 映射到 `SVC_Handler/PendSV_Handler/SysTick_Handler`，因此 User/gd32f30x_it.c 不能再定义这三个函数。
- 硬件浮点：`-mfpu=fpv4-sp-d16 -mfloat-abi=hard`；FPU 由 FreeRTOS 移植层在启动调度器时使能
- 栈溢出检查：`configCHECK_FOR_STACK_OVERFLOW 2`，溢出时进入 User/freertos_hooks.c 的 vApplicationStackOverflowHook()，此处关中断并死循环，便于调试器定位

## 工程约定

- `GD32F30x/`、`FREERTOS/` 内文件保持官方原样，不加入任何本地文件。需要打补丁时，先在 [UPSTREAM.md](UPSTREAM.md) 记录改了什么、为什么。
- 新代码放 `User/`，并在 Makefile 的 C_SOURCES / C_INCLUDES 中加入。
- 升级第三方库时整体替换目录，再重新对照本 README 的版本表。
- build/、packs/、svd/ 和 .vscode/settings.json 不纳入版本控制。
- packs/ 与 svd/ 由可选的型号脚本生成，不要再分发；SVD 只用于调试器的外设寄存器视图，不参与编译。
- .vscode/ 只提交跨平台配置 tasks.json、c_cpp_properties.json、extensions.json、launch.json。

## 可选扩展（非构建必需）

以下内容不影响 `make` 构建，按需阅读：

| 内容 | 文档 | 说明 |
|------|------|------|
| VSCode 编程与调试平台 | [docs/vscode.md](docs/vscode.md) | 编译任务、IntelliSense、器件包、烧录、F5 调试、型号切换脚本 |

## 许可

- 本工程自有代码（User/、Makefile、文档）采用 MIT，见 [LICENSE](LICENSE)。
- GD32F30x/ 为兆易创新（GigaDevice）授权软件（其中启动文件与链接脚本为 Apache-2.0），FREERTOS/ 为 MIT。完整说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)，再分发时请一并保留这些文件。
