import numpy as np
import pysig as ps

# Generate a beat signal by summing two sine waves with slightly different frequencies
axis = ps.nrange(0, 1, 0.001)
wave1 = ps.create("sin(2*np.pi*50*t)", axis)
wave2 = ps.create("sin(2*np.pi*55*t)", axis)
beat = wave1 + wave2

# Plot the resulting beat signal
ps.plot(beat)
