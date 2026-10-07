#ifndef SERVO_H
#define SERVO_H

#include <stdint.h>

void initServo(void);
void setServoAngle(uint8_t angle);
void printServoAngle(uint8_t angle);

#endif