import serial
import time

# Serial port connected to the ATmega32PB
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Give the serial connection time to initialize
time.sleep(2)

# Debugging/connection message
print("Connected to ATmega32PB")

# Close the serial connection
ser.close()