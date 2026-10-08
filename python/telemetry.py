import serial
import time

# For Plotting
import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import datetime

# Serial port connected to the ATmega32PB
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# Number of complete sweeps to receive
MAX_SWEEPS = 3

# Colors for the plot
GREEN = "#00ff41"       # bright radar green
DIM_GREEN = "#0a5c1f"   # darker green for the grid

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Give the serial connection time to initialize
time.sleep(2)

# Clear old data from the serial buffer
ser.reset_input_buffer()

print("Connected to ATmega32PB")
print("Waiting for telemetry...\n")

# Stop first in case it was running
ser.write(b"X\n")

# Send start command to ATmega
ser.write(b"S\n")

# Count complete sweeps
sweeps = 0

# Keep track of the previous angle
previous_angle = None

# Wait for the first angle of the sweep
started = False

# Arrays to hold angles and distances for plotting and saving to CSV
angles = []
distances = []
rows = []

# Telemetry statistics
measurements = 0
invalid_measurements = 0
last_angle = 0
last_distance = 0

plt.ion() # Interactive mode so we can see plotting in real-time

# Create a single polar plot for the sonar sweep
fig = plt.figure(facecolor="black")
ax = fig.add_subplot(111, projection="polar", facecolor="black")

ax.set_title(f"180 Degree Sonar Sweep - {datetime.now().strftime('%H_%M_%S')}", color=GREEN)
ax.grid(True, color=DIM_GREEN)
ax.tick_params(colors=GREEN)                 # angle and distance labels
for spine in ax.spines.values():
    spine.set_color(GREEN)                   # outline of the half circle

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

        # Keep track of the latest measurement
        last_angle = angle
        last_distance = distance
        measurements += 1
        
        # Do not append invalid distance measurements
        if distance != 999:
            angles.append(np.radians(angle))  # Convert angle to radians for polar plot
            distances.append(distance)        # Append the distance into the array
            rows.append([sweeps + 1, angle, distance])
        else:
            invalid_measurements += 1

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

# Set the limits for the polar plot
ax.set_thetamin(0)
ax.set_thetamax(180)

# Changes color of the points to green
ax.scatter(angles, distances, s=90, color=GREEN, alpha=0.15)
ax.scatter(angles, distances, s=15, color=GREEN)

# Display the number of completed sweeps at the bottom
ax.text(
    0.5, -0.15,
    f"Sweeps: {sweeps}",
    transform=ax.transAxes,
    ha="center",
    
)
plt.tight_layout()  # Do not cutoff bottom text


# Save the data to a CSV file
filename = f"sonar_data_{datetime.now().strftime('%H_%M_%S')}.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Sweep", "Angle (degrees)", "Distance (cm)"])
    writer.writerows(rows)

# Save the plot ass an image
pic_name = f"sonar_plot_{datetime.now().strftime('%H_%M_%S')}.png"
plt.savefig(pic_name, bbox_inches="tight", facecolor=fig.get_facecolor())

# Display final telemetry dashboard
print("\n================================")
print("       SONAR TELEMETRY")
print("================================")
print("Connection:    DISCONNECTED")
print(f"Sweep:         {sweeps} / {MAX_SWEEPS}")
print(f"Angle:         {last_angle}°")
print(f"Distance:      {last_distance} cm")
print(f"Measurements:  {measurements}")
print(f"Invalid:       {invalid_measurements}")
print(f"Minimum:       {min(distances)} cm")
print(f"Maximum:       {max(distances)} cm")
print(f"Average:       {sum(distances) / len(distances):.0f} cm")
print("================================")

plt.show() # Keep the graph on the screen
print("\nTelemetry stopped.")