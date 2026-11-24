/*
 * Application hooks required by FreeRTOSConfig.h.
 *
 * vApplicationStackOverflowHook() is called by the kernel when
 * configCHECK_FOR_STACK_OVERFLOW detects a task stack overflow. It runs in
 * the context of the offending task, so the stack may already be corrupt;
 * stop in the debugger here instead of returning.
 */

#include "FreeRTOS.h"
#include "task.h"

void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    (void)xTask;
    (void)pcTaskName;

    taskDISABLE_INTERRUPTS();

    for (;;) {
    }
}
