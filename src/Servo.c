// This program drives a servo motor from 0 to 180 degrees
// at a constant pace, then back from 180 to 0 degrees.
// Frequency = 61 Hz
// Servo driver signal: Pulse width range: 800 us - 2200 us
// (corresponds to 0 - 180 degrees)
//
// Timer characteristics:
// N = 1024
// feff = 16 MHz/1024 = 15.625 kHz
// Frequency of timer clock: 15.625 kHz
// Tceff of timer clock = 1/feff = 64 us
//
// So, 800 us = 13 Tceff, 1500 us = 23 Tceff, 2200 us = 34 Tceff
// Thus, settings are:
// 800 us: OCR0A = 13
// 1500 us: OCR0A = 23
// 2200 us: OCR0A = 34
#define BAUD 9600

#include <avr/io.h>
#include <stdint.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include "Servo.h"

#define DEGREE0 13
#define DEGREE180 34

void initIO();
void initTimer0();
void initUART();
unsigned char getChar();
void putChar(unsigned char c);

void initServo()
{
    initIO();
    initUART();
    initTimer0();
}

void setServoAngle(uint8_t angle)
{
    OCR0A = DEGREE0 + ((uint16_t)angle * (DEGREE180 - DEGREE0)) / 180;
}

void printServoAngle(uint8_t angle)
{
    printString("Angle: ");
    printNumber(angle);
    printString("\r\n");
}

void initUART() {
    unsigned int baudrate;
    // Set baud rate: UBRR = [F_CPU/(16*BAUD)] - 1
    baudrate = ((F_CPU / 16) / BAUD) - 1;
    UBRR0H = (unsigned char)(baudrate >> 8);
    UBRR0L = (unsigned char)baudrate;

    UCSR0B |= (1 << RXEN0) | (1 << TXEN0);
    UCSR0C |= (1 << UCSZ01) | (1 << UCSZ00);
}

unsigned char getChar() {
    unsigned char c;

    while (!(UCSR0A & (1 << RXC0)));
    c = UDR0;
    UCSR0A |= (1 << RXC0);

    return c;
}

void putChar(unsigned char c) {
    UDR0 = c;
    while (!(UCSR0A & (1 << TXC0)));
    UCSR0A |= (1 << TXC0);
}

void printString(const char *s) {
    unsigned char i = 0;
    while (s[i]) {
        putChar(s[i]);
        i++;
    }
}

void initIO() {
    // Timer 0 - PWM output = OC0A = PD6
    DDRD |= (1 << PIND6);
}

void initTimer0() {
    TCCR0A |= (1 << COM0A1);                    // Non-inverted mode for OC0A
    TCCR0A |= (1 << WGM01) | (1 << WGM00);      // Fast PWM mode
    TCCR0B |= (1 << CS02) | (1 << CS00);        // Prescaler = 1024
    TCNT0 = 0;
}

void printNumber(uint32_t number)
{
    uint32_t divisor = 1000000000;
    uint8_t started = 0;
    while (divisor > 0)
    {
        uint8_t digit = number / divisor;
        if (digit > 0 || started || divisor == 1)
        {
            putChar(digit + '0');
            started = 1;
        }
        number %= divisor;
        divisor /= 10;
    }
}