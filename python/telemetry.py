import serial
import time

# For Plotting
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Serial port connected to the ATmega32PB
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# Number of complete sweeps to receive
MAX_SWEEPS = 3

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Give the serial connection time to initialize
time.sleep(2)

# Clear old data from the serial buffer
ser.reset_input_buffer()

print("Connected to ATmega32PB")
print("Waiting for telemetry...\n")

# Send start command to ATmega
ser.write(b"S\n")

# Count complete sweeps
sweeps = 0

# Keep track of the previous angle
previous_angle = None

# Wait for the first angle of the sweep
started = False

angles = []
distances = []

plt.ion() # Interactive mode so we can see plotting in real-time

# Create a single polar plot for the sonar sweep
ax = plt.subplot(111, projection ="polar")
ax.set_title(f"180 Degree Sonar Sweep - {datetime.now().strftime('%H:%M:%S')}")

while sweeps < MAX_SWEEPS:

    # Read one line from the ATmega
    line = ser.readline().decode("utf-8").strip()

    if line:
        # Get the angle
        angle = int(line.split(",")[0].split(":")[1])

        # Wait until the servo is at 0 degrees before recording data
        if not started:
            if angle != 0:
                continue
            started = True

        print(line)

        distance = int(line.split(",")[1].split(":")[1])

        # Do not append invalid distance measurements
        if distance != 999:
            angles.append(np.radians(angle))  # Convert angle to radians for polar plot
            distances.append(distance)        # Append the distance into the array

        # A sweep is complete when the servo returns to 0 degrees.
        if previous_angle == 5 and angle == 0:
            sweeps += 1
            print("Completed sweep:", sweeps)

            # Stop after the requested number of sweeps
            if sweeps == MAX_SWEEPS:
                ser.write(b"X\n")
                break

        previous_angle = angle

# Close the serial connection
ser.close()
plt.ioff()

# Plot the data on the polar plot
ax.scatter(angles, distances)

# Set the limits for the polar plot
ax.set_thetamin(0)
ax.set_thetamax(180)

plt.show() # Keep the graph on the screen
print("\nTelemetry stopped.")