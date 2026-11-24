######################################
# GD32F30x + FreeRTOS GCC baseline
######################################

TARGET    = aaa_generic_project_name
BUILD_DIR = build

######################################
# Toolchain
######################################
PREFIX = arm-none-eabi-
# Used only by debug-setup, not by the firmware build
PYTHON ?= python

ifdef GCC_PATH
CC = $(GCC_PATH)/$(PREFIX)gcc
AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
CP = $(GCC_PATH)/$(PREFIX)objcopy
SZ = $(GCC_PATH)/$(PREFIX)size
else
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
CP = $(PREFIX)objcopy
SZ = $(PREFIX)size
endif

######################################
# MCU and flags
######################################
CPU       = -mcpu=cortex-m4
FPU       = -mfpu=fpv4-sp-d16
FLOAT_ABI = -mfloat-abi=hard
MCU       = $(CPU) -mthumb $(FPU) $(FLOAT_ABI)

C_DEFS = -DUSE_STDPERIPH_DRIVER -DGD32F30X_HD

C_INCLUDES = \
  -IGD32F30x/CMSIS \
  -IGD32F30x/CMSIS/GD/GD32F30x/Include \
  -IGD32F30x/GD32F30x_standard_peripheral/Include \
  -IFREERTOS/include \
  -IFREERTOS/portable/GCC/ARM_CM4F \
  -IUser

OPT = -Os

CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -std=gnu99 -Wall \
         -fdata-sections -ffunction-sections -g -gdwarf-2 \
         -MMD -MP -MF"$(@:%.o=%.d)"

ASFLAGS = $(MCU) $(OPT) -g

LDSCRIPT = GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/Ld/gd32f303xC_flash.ld

LDFLAGS = $(MCU) -T $(LDSCRIPT) -specs=nosys.specs \
          -Wl,--gc-sections -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref \
          -lc -lm

######################################
# Sources
######################################
C_SOURCES = \
  $(wildcard GD32F30x/GD32F30x_standard_peripheral/Source/*.c) \
  GD32F30x/CMSIS/GD/GD32F30x/Source/system_gd32f30x.c \
  FREERTOS/tasks.c \
  FREERTOS/queue.c \
  FREERTOS/list.c \
  FREERTOS/timers.c \
  FREERTOS/event_groups.c \
  FREERTOS/stream_buffer.c \
  FREERTOS/croutine.c \
  FREERTOS/portable/GCC/ARM_CM4F/port.c \
  FREERTOS/portable/MemMang/heap_4.c \
  $(wildcard User/*.c)

ASM_SOURCES = \
  GD32F30x/CMSIS/GD/GD32F30x/Source/GCC/startup_gd32f30x_hd.S

######################################
# Build rules
######################################
OBJECTS  = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.S=.o)))
vpath %.S $(sort $(dir $(ASM_SOURCES)))

all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR)
	$(CC) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/%.o: %.S Makefile | $(BUILD_DIR)
	$(AS) -c $(ASFLAGS) $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile | $(BUILD_DIR)
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf
	$(CP) -O ihex $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf
	$(CP) -O binary -S $< $@

$(BUILD_DIR):
	mkdir -p $@

size: $(BUILD_DIR)/$(TARGET).elf
	$(SZ) $<

clean:
	rm -rf $(BUILD_DIR)

# Optional debug setup: fetch/verify GD32F30x DFP 2.6.0 and extract all SVDs (see docs/vscode.md)
debug-setup:
	$(PYTHON) tools/fetch_pack.py

# Optional device switch: update Makefile/VSCode config and select its SVD (see docs/vscode.md)
# Usage: make select-device DEVICE=GD32F303VE
select-device:
	$(PYTHON) tools/select_device.py $(DEVICE)

-include $(wildcard $(BUILD_DIR)/*.d)

.PHONY: all clean size debug-setup select-device
