/*
 * HC-SR04 Ultrasonic Distance Sensor
 *
 * Connections:
 * VCC  -> 5V
 * GND  -> GND
 * TRIG -> PB0
 * ECHO -> PB2
 *
 * PB0 sends a short trigger pulse to start a measurement.
 * PB2 receives the echo pulse from the sensor.
 *
 * Timer1 is used to measure how long the ECHO pin stays HIGH.
 * With a prescaler of 8 and a 16 MHz clock, each Timer1 tick
 * is 0.5 us.
 */

#include <avr/io.h>
#include <util/delay.h>     // Required for _delay_ms()
#include "UltrasonicSenor.h"

uint32_t getDistance(void)
{
    uint16_t time = 0;
    uint32_t distance = 0;

    // Set TRIG (PB0) as output
    DDRB |= (1 << PB0);

    // Set ECHO (PB2) as input
    DDRB &= ~(1 << PB2);

    // Send 0 to TRIG
    PORTB &= ~(1 << PB0);

    // Wait for 2 us
    _delay_us(2);

    // Send 1 to TRIG
    PORTB |= (1 << PB0);

    // Wait for 10 us
    _delay_us(10);

    // Send 0 to TRIG
    PORTB &= ~(1 << PB0);

    // Set Timer1 to Normal Mode
    TCCR1A = 0x00;

    // Set Timer1 prescaler to 8
    TCCR1B = (1 << CS11);

    // Wait until ECHO goes HIGH
    while (!(PINB & (1 << PB2)));

    // Set Timer1 to 0 to begin counting
    TCNT1 = 0;

    // Wait until ECHO goes LOW
    while (PINB & (1 << PB2));

    // Copy Timer1 value
    time = TCNT1;

    // Disable Timer1
    TCCR1B = 0x00;

    // With a prescaler of 8, each clock tick is 0.5 us.
    // Convert echo time to distance in centimeters.
    distance = (uint32_t)time / 296;

    // Wait 1 ms before the next measurement
    _delay_ms(1);

    return distance;
}
