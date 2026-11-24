简体中文 | [English](vscode.en.md)

# 可选：VSCode 编程与调试平台

> **可选内容**：本页把 VSCode 工程配置、器件包、烧录调试和型号切换脚本集中在一起。
> 固件构建只依赖 `arm-none-eabi-gcc` + GNU Make；`.vscode/`、`tools/`、`packs/`、`svd/`
> 都不参与 `make`，删除或跳过它们不影响固件产物。
>
> 不依赖 VSCode 和脚本的手动换型号流程，见
> [README 的「换芯片 / 改板（手动）」](../README.md#换芯片--改板手动)。
> `packs/`、`svd/` 都不入库，也不要随工程压缩包转发。

## 环境准备

使用本页的 VSCode 平台完成编译、烧录和调试，需要下列工具：

| 工具 | 用途 | 说明 |
|------|------|------|
| ARM GNU Toolchain | 交叉编译 | 见 [README 的环境准备](../README.md#环境准备) |
| GNU Make | 构建 | 见 [README 的环境准备](../README.md#环境准备) |
| Python 3.8+ | 运行 `tools/` 下的`.py`脚本 | 命令可能是 `python` 或 `python3`，下文统一写 `python` |
| pyOCD | 烧录与调试 | 通过 Python 安装，见下方命令 |
| VSCode | 编辑器 | 主要编程和调试窗口 |
| ms-vscode.cpptools | C/C++ 语法识别 | 是 VSCode 的扩展（插件） |
| marus25.cortex-debug | 调试器识别 | 是 VSCode 的扩展（插件） |
| Git for Windows | 便捷执行make构建任务（仅 Windows） | VSCode for windows 默认终端经常识别不到环境变量，改用 Git 自带的 bash |
| curl | 手动下载器件包（可选） | 不用脚本下载时使用，见「手动下载 pack」 |

硬件：PWLINK2 调试探针（兼容 CMSIS-DAP，pyOCD 可直接识别）。

### 安装方法

**ARM GNU Toolchain**

见 [README 的环境准备](../README.md#环境准备)

**GNU Make**

见 [README 的环境准备](../README.md#环境准备)

**Python 3.8+**

- Windows：从 [python.org](https://www.python.org/downloads/) 下载安装，勾选
  **Add python.exe to PATH**。
- macOS：用 python.org 安装包，或 `brew install python`。
- Linux：`sudo apt install python3 python3-pip`（或发行版等价命令）。

命令名可能是 `python3`：把下文的 `python` 换成 `python3` 即可，用 Make 时写
`make debug-setup PYTHON=python3`。

**pyOCD**

```bash
python -m pip install pyocd
```

Linux 下如果提示找不到探针或没有权限，参考
[pyOCD 文档](https://pyocd.io/docs/installing.html) 配置 udev 规则。

**VSCode**

从 [code.visualstudio.com](https://code.visualstudio.com/) 安装。打开本工程后，
`.vscode/extensions.json` 会提示安装推荐扩展；也可以手动安装
`ms-vscode.cpptools` 和 `marus25.cortex-debug`，装完重新加载窗口。

**Git for Windows**

从 [git-scm.com](https://git-scm.com/download/win) 下载安装，保持默认路径
`C:\Program Files\Git`（构建任务通过其中的 `bin\bash.exe` 执行）；装在别处时
修改 `.vscode/tasks.json` 中的 `shell.executable`。

**curl（可选）**

Windows 10/11、Linux、macOS 通常已自带，只在「手动下载 pack」时用到。

安装后确认：

```bash
arm-none-eabi-gcc --version   # 应输出 13.3.1
make --version                # Windows: mingw32-make --version
python --version              # 需要 3.8 以上
pyocd --version
```

器件包在「完整流程」第 1 步获取。只想用命令行编译和烧录、不装 VSCode 时，可跳过编辑器相关的
工具，改用 OpenOCD / J-Link 的命令（见「其他调试器」）。

## 完整流程

空工程从第 1 步开始，按以下顺序操作。日常只改代码时可直接跳到第 3 步。

### 1. 解出器件包与 SVD

在工程目录，或从目录打开 VSCode 后，调用终端执行：

```bash
make debug-setup        # Windows: mingw32-make debug-setup
```

脚本会下载并校验 `GigaDevice.GD32F30x_DFP 2.6.0`，把包内全部 SVD 解到 `svd/`。
重复执行没有副作用。细节见[器件包与 SVD](#器件包与-svd)。

### 2. 切换型号

先确认好型号，在工程目录，或从目录打开 VSCode 后，调用终端执行：

```bash
make select-device DEVICE=GD32F303VC    # 换成你实际使用的型号
```

脚本会读取器件包，更新 Makefile 的容量宏、启动文件和链接脚本，同时同步
`.vscode/launch.json`、`.vscode/c_cpp_properties.json` 和 `svd/` 中选定的 SVD。
型号不变时也可以运行，用来确认配置一致。细节见[自动切换型号](#自动切换型号)。

### 3. 编译

随附的 `.vscode/tasks.json` 已将默认编译操作绑定到 `Ctrl+Shift+B`；
VSCode 中按 `Ctrl+Shift+B`，或命令行：

```bash
make            # Windows: mingw32-make
```

产物在 `build/<TARGET>.elf`、`.hex`、`.bin`。编译任务的细节见
[VSCode 工程配置](#vscode-工程配置)。

使用清除命令移除产物：

```bash
make clean           # Windows: mingw32-make clean
```

### 4. 烧录与调试

随附的 `.vscode/launch.json` 已将调试操作绑定到 `F5`；连接 PWLINK2 烧录器后，VSCode 中按 `F5` 启动 Cortex-Debug + pyOCD；暂停后可查看内核寄存器和
外设寄存器。也可以先用命令行烧录：

```bash
pyocd flash --pack packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
            -t gd32f303vc build/aaa_generic_project_name.elf
```

细节见[烧录](#烧录)与[调试](#调试)。

## 配置详情

### 器件包与 SVD

pyOCD 需要 GD32F30x 器件包来获得内存布局、Flash 算法和 SVD。本工程使用官方
**GigaDevice.GD32F30x_DFP 2.6.0**（2025-08-20 发布），默认路径为：

```
packs/GigaDevice.GD32F30x_DFP.2.6.0.pack
```

> **许可提示**：该 DFP 由兆易创新以 **SLA-GD0006-version1.1** 授权
> （见 [Addon 仓库的 LICENSE](https://github.com/GigaDevice-GD32-MCU/GD32F30x_Addon/blob/main/LICENSE)），
> 仅允许配合兆易芯片用于开发，并禁止再分发。下载或使用该包即表示接受该协议。
> `packs/` 与 `svd/` 都不要提交到仓库、也不要随工程压缩包转发；本仓库不包含
> 该器件包，也不分发由它解出的 SVD。

#### fetch_pack.py：下载、校验并解出全部 SVD

脚本会：

1. 从 GigaDevice 的 `GD32F30x_Addon` 仓库下载
   `GigaDevice.GD32F30x_DFP.2.6.0.pack`；
2. 校验 SHA-256（同时检查 zip 完整性和 PDSC 的版本声明）；
3. 把包内全部 `SVD/*.svd` 解到 `svd/`；
4. 已存在且校验通过时跳过下载，重复执行没有副作用。

```bash
python tools/fetch_pack.py
# 或
make debug-setup            # Windows: mingw32-make debug-setup
```

只提供 `python3` 的系统把 `python` 换成 `python3`；用 Make 时
`make debug-setup PYTHON=python3`。

| 参数 | 说明 |
|------|------|
| `--force` | 覆盖已存在但校验不通过的文件 |
| `--url URL` | 改用镜像或其他下载源 |
| `--dest PATH` | 指定 pack 保存路径 |
| `--svd-dir DIR` | 指定 SVD 输出目录（默认 `svd/`） |
| `--no-svd` | 只下载并校验 pack，不解 SVD |

#### 手动下载 pack

脚本不是必需的。也可以手动下载后交给脚本校验：

- 仓库目录：
  <https://github.com/GigaDevice-GD32-MCU/GD32F30x_Addon/tree/main/Keil/Keil5>
- 直接链接：
  <https://raw.githubusercontent.com/GigaDevice-GD32-MCU/GD32F30x_Addon/main/Keil/Keil5/GigaDevice.GD32F30x_DFP.2.6.0.pack>
- 保存为：`packs/GigaDevice.GD32F30x_DFP.2.6.0.pack`
- 然后运行一次 `python tools/fetch_pack.py`，校验并解出全部 SVD。

命令行下载：

```bash
mkdir -p packs
curl -L -o packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
  https://raw.githubusercontent.com/GigaDevice-GD32-MCU/GD32F30x_Addon/main/Keil/Keil5/GigaDevice.GD32F30x_DFP.2.6.0.pack
```

SHA-256（可用 `sha256sum` 或 `certutil -hashfile` 核对）：

```
ef90301be96d0607cf3ed46742d9b08a68ad7e4b07b2259b5f9062d45feabe78
```

#### SVD 说明

- `make debug-setup` 会把包内全部 `SVD/*.svd` 解到 `svd/`；
- 当前调试使用哪一个由 `launch.json` 的 `svdFile` 决定；
- `svd/` 不参与编译，也不随仓库分发。

### 自动切换型号

`select_device.py` 从 pack 的 PDSC 器件数据库读取型号属性，自动更新：

| 文件 | 修改内容 |
|------|----------|
| `Makefile` | `C_DEFS` 容量宏、启动文件、`LDSCRIPT`（不改 `TARGET`） |
| `.vscode/launch.json` | `executable`、`targetId`、`svdFile` |
| `.vscode/c_cpp_properties.json` | 配置名、容量等级宏 |
| `svd/` | 选定型号的 SVD；缺失时从 pack 补解 |

Makefile 的修改直接决定固件；`.vscode/` 和 SVD 只影响编辑器与调试体验。
如果不想让脚本改动 `.vscode/`，只手动应用 Makefile 部分即可（见
[README 的手动流程](../README.md#换芯片--改板手动)）。

```bash
python tools/select_device.py --list          # 列出 pack 支持的型号
python tools/select_device.py GD32F303VE      # 切换型号
python tools/select_device.py GD32F307VC --dry-run
python tools/select_device.py GD32F303VE --pack path/to/dfp.pack
# 或
make select-device DEVICE=GD32F303VE
```

- `--list`：列出型号及其 `define`、Flash 大小、SVD；
- `--dry-run`：只打印将要做的修改，不写文件；
- `--pack`：指定 pack 路径（默认用 `packs/` 下的 2.6.0）。

切换后重新编译：

```bash
make clean && make        # Windows: mingw32-make clean && mingw32-make
```

PDSC 中未声明 `compile`/`debug` 的型号（目前是 GD32F305/307）会按 Flash 容量
推断容量等级，输出中会注明 `inferred from flash size`。手动切换的等价步骤见
[README 的「换芯片 / 改板（手动）」](../README.md#换芯片--改板手动)。

### VSCode 工程配置

#### 提交的配置

仓库只提交跨平台的工程级配置：

- `tasks.json`：编译、清理、查看大小；
- `c_cpp_properties.json`：IntelliSense 头文件路径与宏；
- `extensions.json`：推荐扩展 `ms-vscode.cpptools`、`marus25.cortex-debug`；
- `launch.json`：Cortex-Debug + pyOCD 调试配置。

个人设置放在 `.vscode/settings.json`，该文件不纳入版本控制。

#### 编译任务

- `Ctrl+Shift+B`：编译（默认任务）；
- `Ctrl+Shift+P` → `Tasks: Run Task`：`rebuild` / `clean` / `size`；
- 编译错误会进入 Problems 面板（`$gcc` 问题匹配器）。

任务按平台自动切换：Linux/macOS 用 `make`，Windows 用 `mingw32-make` 并通过
Git Bash 执行。Windows 下默认假定 Git 安装在 `C:\Program Files\Git`
（通过 `${env:ProgramFiles}` 获取）；装在别处时修改 `.vscode/tasks.json`
中的 `shell.executable`。

#### IntelliSense

[c_cpp_properties.json](../.vscode/c_cpp_properties.json) 是 C/C++ 扩展的独立配置，
**不参与编译**，但需要和 Makefile 保持一致：

- `name`：当前型号名；
- `defines`：`USE_STDPERIPH_DRIVER` 和容量等级宏，如 `GD32F30X_HD`。

手动换型号时，除了改 Makefile，还要同步这里的容量宏，否则编辑器会按错误型号
解析外设头文件（出现假报错、错误的补全）。运行 `select_device.py` 会自动同步
（见[自动切换型号](#自动切换型号)）。

### 烧录

#### 命令行（pyOCD）

```bash
pyocd flash --pack packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
            -t gd32f303vc build/aaa_generic_project_name.elf
```

`-t` 是 pyOCD 的 targetId，换型号时改成对应的小写型号名。
产物名来自 Makefile 的 `TARGET`，改名后同步修改这里的路径即可。

#### 其他调试器

```bash
# OpenOCD（target 配置随 OpenOCD 版本不同，可能是 gd32f30x.cfg 或 stm32f30x.cfg）
openocd -f interface/cmsis-dap.cfg -f target/stm32f30x.cfg \
        -c "program build/aaa_generic_project_name.hex verify reset exit"

# J-Link
JLinkExe -device GD32F303VC -if SWD -speed 4000
```

### 调试

VSCode 使用 Cortex-Debug + pyOCD 调试（F5）。`extensions.json` 推荐安装
`marus25.cortex-debug`，`launch.json` 已配置：

```json
"cmsisPack": "${workspaceFolder}/packs/GigaDevice.GD32F30x_DFP.2.6.0.pack",
```

Cortex-Debug 会把它转成 `pyocd gdbserver --pack ...`，因此不需要
`pyocd pack install`，也不要求 pyOCD 的 pack 索引里存在 2.6.0。

按 `F5` 启动调试；暂停后可查看：

- CORTEX REGISTERS：内核寄存器；
- CORTEX PERIPHERALS：外设寄存器，读取 `svdFile` 指向的 SVD。

换型号时同步修改 `launch.json` 的 `targetId` 和 `svdFile`，或者运行
`select_device.py` 自动处理（见[自动切换型号](#自动切换型号)）。2.6.0 的 pack
覆盖 GD32F30x 全系列。

## 更换烧录器

默认配置以 PWLINK2（CMSIS-DAP 兼容）配合 pyOCD 为例。更换烧录器只影响烧录和调试
通道；`make` 构建、链接脚本和容量宏都不依赖探针，固件产物不需要重新编译。

### 先确认探针类型

| 新烧录器 | 配置改动 |
|----------|----------|
| 其他 CMSIS-DAP 兼容探针（DAP-Link、GD-Link 等） | pyOCD 一般能直接识别，`launch.json` 只需改 `name` |
| J-Link | 改 `servertype`、`device`，删除 pyOCD 专有字段 |
| ST-Link | 改用 `stutil` 或 OpenOCD |
| 其他 | 走 OpenOCD，配置 `configFiles` |

先用下面的命令确认工具能否识别新探针；识别不到时不要再在 pyOCD 上排查：

```bash
pyocd list
```

### 接线与电气

- 核对新探针的排针定义，重点是 `SWDIO`、`SWCLK`、`GND`、`VTref/3V3`；有条件再接
  `NRST`。
- J-Link 等探针通过 `VTref` 检测目标电平，只接三根信号线可能提示目标未供电。
  目标板需要自行上电。
- 部分探针会从 3.3V 脚输出供电；板子已独立供电时不要同时接入，避免双电源。
- SWD 线尽量短（20 cm 以内），先接 GND 再接信号线。
- 同时只连接一支探针，换探针前拔掉旧的，避免工具选错设备。

### 修改 launch.json

[.vscode/launch.json](../.vscode/launch.json) 中 `targetId`、`cmsisPack`、
`overrideGDBServerStartedRegex` 都是 pyOCD 专有字段，换服务器类型后应删除或忽略。
`svdFile` 与探针无关，始终保留。

**仍是 pyOCD（换另一支 CMSIS-DAP 探针）**

只需修改显示名称：

```jsonc
"name": "Debug (pyOCD / 新探针名)",
```

只有一支探针时无需其它修改。连接多支探针时，用 `pyocd list` 查出 UID 后加：

```jsonc
"serverArgs": ["-u", "<探针 UID>"]
```

**J-Link**

```jsonc
"servertype": "jlink",
"device": "GD32F303VC",
"interface": "swd",
```

`device` 使用 J-Link 器件库中的大写型号名。连接多支 J-Link 时加
`"serialNumber": "<序列号>"`。烧录命令改为：

```bash
JLinkExe -device GD32F303VC -if SWD -speed 4000
```

**ST-Link**

Cortex-Debug 使用 `"servertype": "stutil"`，或改用 OpenOCD。山寨 ST-Link 可能
触发固件版本检查，升级有变砖风险，能用 OpenOCD 就不要升级。

**OpenOCD**

```jsonc
"servertype": "openocd",
"configFiles": ["interface/cmsis-dap.cfg", "target/gd32f30x.cfg"],
"searchDir": ["<OpenOCD scripts 目录>"],
```

target 配置随 OpenOCD 版本不同，可能只有 `target/stm32f30x.cfg`（见
[其他调试器](#其他调试器)）。OpenOCD 的 STM32F30x 驱动对 GD32 的 Flash 容量和
保护位识别可能不准，必要时手动指定。

### GD32 侧注意事项

- **SWD 引脚复用**：固件若把 `PA13`/`PA14` 配置成普通 GPIO，复位后探针可能连不上。
  此时使用 "connect under reset"，并确保 `NRST` 已连接。
- **读保护/选项字节**：芯片被其他工具加过读保护时，新工具会要求解锁或全片擦除，
  全擦会清除现有固件，操作前确认。
- **BOOT0**：从 Flash 启动要求 BOOT0 为低。
- **低功耗**：FreeRTOS 空闲任务会进入 WFI，一般不影响 SWD；连接不稳定时优先尝试
  "connect under reset" 并降低时钟。

### 速率与验证

先用较低速率（1–2 MHz）跑通，再逐步提高。速率参数：pyOCD 用
`serverArgs: ["-f", "1M"]`，J-Link 用 `-speed 1000`，OpenOCD 用 `adapter speed`。

按顺序验证：

```bash
pyocd list                          # 识别探针
pyocd flash --pack packs/GigaDevice.GD32F30x_DFP.2.6.0.pack \
            -t gd32f303vc build/aaa_generic_project_name.elf
pyocd reset                         # 确认程序在运行
```

再按 `F5`，在 `main` 打断点，确认能暂停、单步，并在 CORTEX PERIPHERALS 中读到
外设寄存器。

### 长期更换后要同步的文档

- [.vscode/launch.json](../.vscode/launch.json) 的 `name`、`servertype`、`device`
  等字段；
- 本页[环境准备](#环境准备)的硬件说明，以及[烧录](#烧录)、[调试](#调试)两节的
  命令和描述；
- 命令行烧录示例（`pyocd flash` / `JLinkExe` / `openocd`）。
