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

#define DEGREE0 13
#define DEGREE180 34

void initIO();
void initTimer0();
void initUART();
unsigned char getChar();
void putChar(unsigned char c);
void printString(char *s);
void printNumber(uint8_t number);

int main(void)
{
    initIO();
    initUART();
    initTimer0();
    uint8_t angle;

    while (1) {
        // Move from 0 degrees to 180 degrees
        for (uint8_t position = DEGREE0; position <= DEGREE180; position++) {
            OCR0A = position;
			// Convert OCR0A position to actual servo angle
            angle = ((position - DEGREE0) * 180) / (DEGREE180 - DEGREE0);

            printString("Angle: ");
            printNumber(angle);
            printString("\r\n");

            _delay_ms(100);
        }
        // Move from 180 degrees back to 0 degrees
        for (uint8_t position = DEGREE180; position >= DEGREE0; position--) {
            OCR0A = position;
			// Convert OCR0A position to actual servo angle
            angle = ((position - DEGREE0) * 180) / (DEGREE180 - DEGREE0);

            printString("Angle: ");
            printNumber(angle);
            printString("\r\n");
            _delay_ms(100);
        }
    }
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

void printString(char *s) {
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

void printNumber(uint8_t number) {
    if (number >= 100) {
        putChar((number / 100) + '0');
        putChar(((number / 10) % 10) + '0');
        putChar((number % 10) + '0');
    }
    else if (number >= 10) {
        putChar((number / 10) + '0');
        putChar((number % 10) + '0');
    }
    else {
        putChar(number + '0');
    }
}