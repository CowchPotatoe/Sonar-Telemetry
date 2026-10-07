import serial
import time

# Serial port connected to the ATmega32PB
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# Number of complete sweeps to receive
MAX_SWEEPS = 2

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Give the serial connection time to initialize
time.sleep(2)

# Clear old data from the serial buffer
ser.reset_input_buffer()

print("Connected to ATmega32PB")
print("Waiting for telemetry...\n")

# Count complete sweeps
sweeps = 0

# Keep track of the previous angle
previous_angle = None

while sweeps < MAX_SWEEPS:

    # Read one line from the ATmega
    line = ser.readline().decode("utf-8").strip()

    if line:
        print(line)
        # Get the angle
        angle = int(line.split(",")[0].split(":")[1])
        # A sweep is complete when the servo returns to 0 degrees.
        if previous_angle == 5 and angle == 0:
            sweeps += 1
            print("Completed sweep:", sweeps)
        previous_angle = angle

# Close the serial connection
ser.close()

print("\nTelemetry stopped.")
