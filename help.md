# pysig Help

`pysig` is a small utility library for manipulating time signals and frequency spectra.

## Classes

### `Signal`
Represents a signal sampled at specific time points. Supports arithmetic operations, FFT conversion to `Spectrum`, and saving/loading to JSON or CSV.

### `Spectrum`
Represents a frequency spectrum with complex values. Supports arithmetic operations, IFFT conversion to `Signal`, and saving/loading.

### `BaseSeries`
Common base class used internally by `Signal` and `Spectrum`.

## Functions

- `create(expr, axis)`: Evaluate an expression using variable `t` (time) or `f` (frequency) to quickly build a `Signal` or `Spectrum`.
- `nrange(start, stop, step)`: Inclusive numerical range, similar to `numpy.arange` but includes the stop value.
- `plot(*items)`: Display signals or spectra using Plotly. The plot is saved as `plot.html` and opened automatically, allowing interactive changes to color and line style.
- `db(spectrum)`: Magnitude of a spectrum in decibels.
- `sin`, `cos`, `exp`: Apply corresponding NumPy functions to a `Signal` or `Spectrum`.

## Persistence

Both `Signal` and `Spectrum` provide `dump(filename)` and `load(filename)` methods for storing data in JSON or CSV format. When saving complex spectra to JSON, the real and imaginary parts are stored in separate `real` and `imag` arrays.

