#define BAUD 9600

#include <avr/io.h>
#include <stdint.h>
#include "UART.h"

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