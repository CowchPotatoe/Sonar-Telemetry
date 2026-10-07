#ifndef UART_H
#define UART_H

#include <stdint.h>

void initUART(void);
unsigned char getChar(void);
void putChar(unsigned char c);
void printString(const char *s);
void printNumber(uint32_t number);

#endif