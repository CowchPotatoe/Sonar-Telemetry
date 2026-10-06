#define F_CPU 8000000	// Clock Speed

#include <avr/io.h>
#include <util/delay.h>		// Required for _delay_ms()

int main(void){
	//variable to hold time
	uint16_t time = 0;
	uint32_t distance = 0;

	while (1)
	{
		//Set port for SIG pin as output
		DDRB |= (1 << PB0);      // Use PB0 for SIG, set as output
		//Send 0 to SIG
		PORTB &= ~(1 << PB0);
		//wait for 2 us
		_delay_us(2);
		//Send 1 to SIG
		PORTB |= (1 << PB0);
		//wait for 5 us
		_delay_us(5);
		//Send 0 to SIG
		PORTB &= ~(1 << PB0);
		//Set port to read SIG pin
		DDRB &= ~(1 << PB0);
		PORTB &= ~(1 << PB0);
		//Set TCCR1A for counting time
		TCCR1A = 0x00;           // Normal Mode
		//Set TCCR1B for pre-scaler (8)
		TCCR1B = (1 << CS11);
		//wait here until SIG is high
		//The sensor sets SIG HIGH when the echo is received.
		while (!(PINB & (1 << PB0)));
		//Set TCNT value to 0 to begin counting
		TCNT1 = 0;               // Timer1 = 0
		//Wait here until SIG is low
		//The amount of time SIG stays HIGH represents the echo travel time.
		while (PINB & (1 << PB0));
		//Copy value of TCNT to variable that hold time
		time = TCNT1;
		//reset TCCR1B = 0x00 i.e., disable timer
		TCCR1B = 0x00;
		//use given distance calculation formula
		//with a prescalar of 8, each clock tick is 0.5 us
		distance = (uint32_t)time / 296;
		//distance now contains the measured distance from the sensor.
		//wait for 1 millisecond
		_delay_ms(1);
	}
	return 0;
}
