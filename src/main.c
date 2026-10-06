#include <stdint.h>
#include <util/delay.h>
#include "UltrasonicSenor.h"
#include "Servo.h"

int main(void)
{
    uint32_t distance;
    // Initialize the servo
    initServo();
    while (1) {
        // Move from 0 degrees to 180 degrees
        for (uint8_t angle = 0; angle <= 180; angle += 5) {
          setServoAngle(angle);
          // Wait for the servo to reach the new position
          _delay_ms(50);
          // Get distance from ultrasonic sensor
          distance = getDistance();
          // Send angle and distance together
          printString("Angle: ");
          printNumber(angle);
          printString(", Distance: ");
          printNumber(distance);
          printString("\r\n");
        }
        // Move from 180 degrees back to 0 degrees
        for (int16_t angle = 180; angle >= 0; angle -= 5) {
          setServoAngle(angle);
          // Wait for the servo to reach the new position
          _delay_ms(50);
          // Get distance from ultrasonic sensor
          distance = getDistance();
          // Send angle and distance together
          printString("Angle: ");
          printNumber(angle);
          printString(", Distance: ");
          printNumber(distance);
          printString("\r\n");
        }
    }

    return 0;
}