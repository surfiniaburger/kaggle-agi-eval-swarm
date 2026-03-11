import matplotlib.pyplot as plt
import numpy as np

# Define the data point
y_max = 10
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

# Create the plot
fig, ax = plt.subplots()

# Plot the data
ax.plot(x, y, label='Data')

# Define the wave parameters
frequency = 5
amplitude = 0.08
speed = 0.05
starting_point = 0

# Generate the wave
time = np.arange(0, 2 * np.pi, speed)
wave = amplitude * np.sin(frequency * time + starting_point)

# Find the index of the maximum value
max_index = np.argmax(y)
max_time = time[max_index]

# Plot the wave
ax.plot(time, wave, color='red', label='Wave')

# Add a vertical line to highlight the peak
ax.axvline(max_time, color='blue', linestyle='--', label='Peak')

# Add labels and legend
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.legend()

# Show the plot
plt.show()