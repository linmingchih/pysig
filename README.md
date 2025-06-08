# pysig

`pysig` provides simple classes for working with signals and spectra.  Signals
store values against time while spectra store complex magnitudes against
frequency.  The library includes FFT/IFFT conversion, arithmetic on aligned axes
and interactive plotting with Plotly.  Data can also be saved to JSON or CSV.

## Installation

This project has no special installation steps; just copy the `pysig` package
somewhere on your Python path.

## Example

```python
import numpy as np
import pysig as ps

# build two signals with different sample times
s1 = ps.Signal([1e-3, 2e-3, 3e-3], [1.2, 2.3, 1.9])
s2 = ps.Signal([1e-3, 2.1e-3, 2.3e-3, 4e-3], [1.3, 2.3, 1.9, 4])

# convert to spectra and combine
sp = s1.fft() + s2.fft()
ps.plot(ps.db(sp))

# operate in the time domain
s3 = s1 + s2
s4 = 2 * s1
ps.plot(s3, s4)

# look up interpolated value and nearest time
val = s3.value(time=1.3e-3)
nearest = s3.time(1.8)
print(val, nearest)

# save and load
s3.dump("signal.json")
restored = ps.Signal.load("signal.json")
```

Additional helper functions `create` and `nrange` make it easy to generate
test signals:

```python
# generate a sine wave from an expression
t_axis = ps.nrange(0, 0.1, 0.001)
sine = ps.create("sin(200*t)", t_axis)
```

See [help.md](help.md) for API details.
