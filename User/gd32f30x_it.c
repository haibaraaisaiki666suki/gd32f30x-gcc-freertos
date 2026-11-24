/*
 * Minimal exception handlers for the GCC baseline.
 *
 * SVC, PendSV and SysTick are provided by the FreeRTOS GCC port through
 * the aliases in FreeRTOSConfig.h, so they must not be defined here.
 */

#include "gd32f30x.h"

void HardFault_Handler(void)
{
    for (;;) {
    }
}
