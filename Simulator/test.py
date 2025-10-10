import matplotlib.pyplot as plt
import numpy as np

# Define the basis vectors
v1 = np.array([1, -1])
v2 = np.array([1, 1])

# Calculate the point corresponding to -v1 + 3v2
point = -1 * v1 + 3 * v2

# Plot the basis vectors
plt.quiver(0, 0, v1[0], v1[1], angles='xy', scale_units='xy', scale=1, color='r', label='v1')
plt.quiver(0, 0, v2[0], v2[1], angles='xy', scale_units='xy', scale=1, color='b', label='v2')

# Plot the point corresponding to -v1 + 3v2
plt.scatter(point[0], point[1], color='g', s=100, label='(-1,3)')

# Configure plot limits
plt.xlim(-5, 5)
plt.ylim(-5, 5)

# Draw the coordinate grid
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)
plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

# Add labels to the axes and a title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Problem 1')

# Add a legend
plt.legend()

# Show the plot
plt.show()