#include <stdint.h>
#include "UltrasonicSenor.h"
#include "Servo.h"

int main(void)
{
    uint32_t distance;

    // Initialize the servo
    initServo();

    while (1)
    {
        // Get distance from ultrasonic sensor
        distance = getDistance();
    }

    return 0;
}