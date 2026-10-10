import serial
import time

# For Plotting
import numpy as np
import csv
from datetime import datetime

# Connect to the dashboard
from dashboard import SonarDashboard

# Serial port connected to the ATmega328PB
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

# Number of complete sweeps to receive
MAX_SWEEPS = 3

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

# Give the serial connection time to initialize
time.sleep(2)

# Clear old data from the serial buffer
ser.reset_input_buffer()

print("Connected to ATmega328PB")
print("Waiting for telemetry...\n")

# Count complete sweeps
sweeps = 0

# Keep track of the previous angle
previous_angle = None

# Wait for the first angle of the sweep
started = False

# Arrays to hold angles, distances, and times
angles = []
distances = []
times = []
rows = []

# Telemetry statistics
measurements = 0
invalid_measurements = 0
last_angle = 0
last_distance = 0

title_time = datetime.now().strftime('%H_%M_%S')
start = time.time()

# Create the dashboard
dashboard = SonarDashboard(title_time)

print("Starting telemetry...")
print(f"Starting time: {title_time}\n")

# Send start command to ATmega
# Do not send X first because the firmware may exit when it receives X
ser.write(b"S\n")

while sweeps < MAX_SWEEPS and dashboard.is_open():

    # Read one line from the ATmega
    line = ser.readline().decode("utf-8", errors="ignore").strip()

    if line:
        try:
            # Separate the angle and distance
            angle_part, distance_part = line.split(",")

            # Get the numbers
            angle = int(angle_part.replace("Angle:", "").strip())
            distance = int(distance_part.replace("Distance:", "").strip())

        except ValueError:
            continue

        # Wait until the servo is at 0 degrees before recording data
        if not started:
            if angle != 0:
                continue

            started = True

        print(line)

        # Keep track of the latest measurement
        last_angle = angle
        last_distance = distance
        measurements += 1

        # Record timestamp and validity for every measurement
        elapsed_time = time.time() - start
        valid = distance != 999

        rows.append([
            round(elapsed_time, 3),
            sweeps + 1,
            angle,
            distance,
            valid
        ])

        # Do not plot invalid distance measurements
        if valid:
            angles.append(np.radians(angle))
            distances.append(distance)
            times.append(elapsed_time)
        else:
            invalid_measurements += 1

        # A sweep is complete when the servo returns to 0 degrees
        if previous_angle == 5 and angle == 0:
            sweeps += 1
            print(f"Completed sweep: {sweeps}\n")

        previous_angle = angle

    # Update the dashboard with the latest data
    dashboard.update(
        angles=angles,
        distances=distances,
        times=times,
        sweeps=sweeps,
        max_sweeps=MAX_SWEEPS,
        last_angle=last_angle,
        last_distance=last_distance,
        measurements=measurements,
        invalid_measurements=invalid_measurements,
        elapsed_seconds=time.time() - start,
        connected=ser.is_open
    )

print(f"Ending time: {datetime.now().strftime('%H_%M_%S')}")
print("Ending telemetry...\n")

end = time.time()

# Stop the ATmega and close the serial connection
if ser.is_open:
    ser.write(b"X\n")
    ser.close()

# Update the dashboard connection status
dashboard.update(
    angles=angles,
    distances=distances,
    times=times,
    sweeps=sweeps,
    max_sweeps=MAX_SWEEPS,
    last_angle=last_angle,
    last_distance=last_distance,
    measurements=measurements,
    invalid_measurements=invalid_measurements,
    elapsed_seconds=end - start,
    connected=False
)

print("Export data to CSV and image")

# Save the data to a CSV file
filename = f"sonar_data_{datetime.now().strftime('%H_%M_%S')}.csv"

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Elapsed Time (s)",
        "Sweep",
        "Angle (degrees)",
        "Distance (cm)",
        "Valid"
    ])
    writer.writerows(rows)

# Save the dashboard as an image
pic_name = f"sonar_plot_{datetime.now().strftime('%H_%M_%S')}.png"
dashboard.save(pic_name)

# Display final telemetry summary
print("\n================================")
print("       SONAR TELEMETRY")
print("================================")
print("Connection:    DISCONNECTED")
print(f"Sweep:         {sweeps} / {MAX_SWEEPS}")
print(f"Measurements:  {measurements}")
print(f"Invalid:       {invalid_measurements}")

if distances:
    print(f"Minimum:       {min(distances)} cm")
    print(f"Maximum:       {max(distances)} cm")
    print(f"Average:       {sum(distances) / len(distances):.0f} cm")
else:
    print("Minimum:       --")
    print("Maximum:       --")
    print("Average:       --")

print(f"Time Elapsed:  {end - start:.1f} seconds")
print("================================")

print(f"\nCSV saved as: {filename}")
print(f"Dashboard saved as: {pic_name}")

# Keep the dashboard on the screen
dashboard.show()

print("\nTelemetry stopped.")