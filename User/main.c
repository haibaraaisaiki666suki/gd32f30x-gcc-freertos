/*
 * Minimal GD32F303VC + FreeRTOS + GCC baseline.
 *
 * This is new, generic demonstration code. It does not contain any
 * company-specific logic, pin map, protocol or customer data.
 */

#include "gd32f30x.h"
#include "FreeRTOS.h"
#include "task.h"

/* Change these three macros to match your board's LED. */
#define LED_RCU   RCU_GPIOB
#define LED_PORT  GPIOB
#define LED_PIN   GPIO_PIN_2

static void led_task(void *argument)
{
    (void)argument;

    for (;;) {
        gpio_bit_set(LED_PORT, LED_PIN);
        vTaskDelay(pdMS_TO_TICKS(500));
        gpio_bit_reset(LED_PORT, LED_PIN);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

int main(void)
{
    SystemCoreClockUpdate();

    rcu_periph_clock_enable(LED_RCU);
    gpio_init(LED_PORT, GPIO_MODE_OUT_PP, GPIO_OSPEED_50MHZ, LED_PIN);
    gpio_bit_reset(LED_PORT, LED_PIN);

    xTaskCreate(led_task, "led", configMINIMAL_STACK_SIZE, NULL, 1, NULL);

    vTaskStartScheduler();

    /* vTaskStartScheduler() only returns if there is not enough heap. */
    for (;;) {
    }
}
