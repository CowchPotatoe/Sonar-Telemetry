import matplotlib.pyplot as plt

GREEN = "#00ff41"
RED = "#ff4444"
DIM_GREEN = "#0a5c1f"
BLACK = "black"


class SonarDashboard:

    def __init__(self, title_time):
        # Enable live plotting.
        plt.ion()

        self.fig = plt.figure(figsize=(13, 8), facecolor=BLACK)
        self.fig.suptitle(
            f"SONAR TELEMETRY - {title_time}",
            color=GREEN,
            fontsize=16
        )

        # Give the radar the whole left side of the window.
        # Put the graph and statistics on the right.
        grid = self.fig.add_gridspec(
            2, 2,
            width_ratios=[1.2, 1]
        )

        # Radar
        self.ax_radar = self.fig.add_subplot(
            grid[:, 0],
            projection="polar",
            facecolor=BLACK
        )

        # Use the same angle settings as the original plot.
        self.ax_radar.set_thetamin(0)
        self.ax_radar.set_thetamax(180)

        self.ax_radar.set_title("180 Degree Sonar Sweep", color=GREEN)
        self.ax_radar.grid(True, color=DIM_GREEN)
        self.ax_radar.tick_params(colors=GREEN)

        for spine in self.ax_radar.spines.values():
            spine.set_color(GREEN)

        # Start with no points. update() adds the sensor readings.
        self.radar_points = self.ax_radar.scatter(
            [], [], s=20, color=GREEN
        )

        # The radar distance scale starts empty and expands as needed.
        self.radar_limit = 0

        # Distance over time
        self.ax_time = self.fig.add_subplot(
            grid[0, 1],
            facecolor=BLACK
        )

        self.ax_time.set_title("Distance vs. Time", color=GREEN)
        self.ax_time.set_xlabel("Time (s)", color=GREEN)
        self.ax_time.set_ylabel("Distance (cm)", color=GREEN)
        self.ax_time.tick_params(colors=GREEN)
        self.ax_time.grid(True, color=DIM_GREEN)

        self.time_line, = self.ax_time.plot([], [], color=GREEN)

        # Statistics
        self.ax_info = self.fig.add_subplot(
            grid[1, 1],
            facecolor=BLACK
        )
        self.ax_info.axis("off")

        # Connection status
        self.status_text = self.ax_info.text(
            0.02, 0.98, "",
            color=GREEN,
            fontsize=10,
            family="monospace",
            verticalalignment="top"
        )

        # Current distance
        self.distance_text = self.ax_info.text(
            0.02, 0.82, "",
            color=GREEN,
            fontsize=10,
            family="monospace",
            verticalalignment="top"
        )

        # Other statistics
        self.info_text = self.ax_info.text(
            0.02, 0.68, "",
            color=GREEN,
            fontsize=10,
            family="monospace",
            verticalalignment="top"
        )

        # Leave room for the title and make the plots less crowded.
        self.fig.subplots_adjust(
            top=0.88,
            left=0.05,
            right=0.97,
            bottom=0.08,
            wspace=0.30,
            hspace=0.35
        )

    def update(
        self,
        angles,
        distances,
        times,
        sweeps,
        max_sweeps,
        last_angle,
        last_distance,
        measurements,
        invalid_measurements,
        elapsed_seconds,
        connected=True
    ):
        # Stop updating if the user closes the window.
        if not self.is_open():
            return

        # Update the radar with valid angles and distances.
        if distances:
            points = list(zip(angles, distances))
            self.radar_points.set_offsets(points)

            # Expand the distance scale when a farther object is detected.
            # The scale never has a fixed maximum such as 300 cm.
            new_limit = max(distances) * 1.15

            if new_limit > self.radar_limit:
                self.radar_limit = new_limit
                self.ax_radar.set_ylim(0, self.radar_limit)

        # Update the distance-over-time graph.
        if times:
            self.time_line.set_data(times, distances)

            self.ax_time.set_xlim(0, max(10, times[-1] * 1.05))
            self.ax_time.set_ylim(
                0, max(50, max(distances) * 1.1)
            )

        # Show the connection status
        if connected:
            self.status_text.set_text("Connection: CONNECTED")
            self.status_text.set_color(GREEN)
        else:
            self.status_text.set_text("Connection: DISCONNECTED")
            self.status_text.set_color(RED)

        # Show the most recent distance
        if last_distance == 999:
            self.distance_text.set_text("Distance: NO ECHO/INVALID")
            self.distance_text.set_color(RED)
        else:
            self.distance_text.set_text(f"Distance: {last_distance} cm")
            self.distance_text.set_color(GREEN)

        # Calculate statistics from valid readings only.
        if distances:
            minimum = f"{min(distances)} cm"
            maximum = f"{max(distances)} cm"
            average = f"{sum(distances) / len(distances):.1f} cm"
        else:
            minimum = "--"
            maximum = "--"
            average = "--"

        # Update the remaining statistics.
        self.info_text.set_text(
            f"Sweep:        {sweeps} / {max_sweeps}\n"
            f"Angle:        {last_angle} degrees\n"
            f"Measurements: {measurements}\n"
            f"Invalid:      {invalid_measurements}\n"
            f"Minimum:      {minimum}\n"
            f"Maximum:      {maximum}\n"
            f"Average:      {average}\n"
            f"Elapsed:      {elapsed_seconds:.1f} s"
        )

        # Refresh the window.
        self.fig.canvas.draw_idle()
        plt.pause(0.001)

    def is_open(self):
        return plt.fignum_exists(self.fig.number)

    def save(self, filename):
        self.fig.savefig(
            filename,
            bbox_inches="tight",
            facecolor=self.fig.get_facecolor()
        )

    def show(self):
        plt.ioff()
        plt.show()
