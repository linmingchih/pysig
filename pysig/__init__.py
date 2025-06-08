import numpy as np
import plotly.graph_objects as go

__all__ = [
    "BaseSeries",
    "Signal",
    "Spectrum",
    "create",
    "nrange",
    "plot",
    "db",
    "sin",
    "cos",
    "exp",
]


class BaseSeries:
    """Base class for ordered data used by :class:`Signal` and :class:`Spectrum`."""

    def __init__(self, axis, values):
        self.x = np.asarray(axis, dtype=float)
        self.values = np.asarray(values)
        if self.x.shape != self.values.shape:
            raise ValueError("axis and values must have same length")

    # ---- internal helpers -------------------------------------------------
    def _interp(self, x):
        if np.iscomplexobj(self.values):
            real = np.interp(x, self.x, self.values.real)
            imag = np.interp(x, self.x, self.values.imag)
            return real + 1j * imag
        return np.interp(x, self.x, self.values)

    def _binary_op(self, other, func):
        if isinstance(other, self.__class__):
            x = np.union1d(self.x, other.x)
            v1 = self._interp(x)
            v2 = other._interp(x)
            return self.__class__(x, func(v1, v2))
        raise TypeError(f"Can only operate with {self.__class__.__name__}")

    # ---- arithmetic operations --------------------------------------------
    def __add__(self, other):
        return self._binary_op(other, lambda a, b: a + b)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self._binary_op(other, lambda a, b: a - b)

    def __rsub__(self, other):
        if isinstance(other, self.__class__):
            return other.__sub__(self)
        raise TypeError(f"Can only subtract {self.__class__.__name__}")

    def __mul__(self, other):
        if np.isscalar(other):
            return self.__class__(self.x, self.values * other)
        raise TypeError("Can only multiply by scalar")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if np.isscalar(other):
            return self.__class__(self.x, self.values / other)
        raise TypeError("Can only divide by scalar")

    def __rtruediv__(self, other):
        if np.isscalar(other):
            return self.__class__(self.x, other / self.values)
        raise TypeError("Can only divide by scalar numerator")

    def __neg__(self):
        return self.__class__(self.x, -self.values)

class Signal(BaseSeries):
    """Simple signal class representing values over time."""

    def __init__(self, times, values):
        super().__init__(times, np.asarray(values, dtype=float))

    @property
    def times(self):
        return self.x


    def value(self, time):
        """Return signal value interpolated at given time."""
        return float(np.interp(time, self.times, self.values))

    def time(self, value):
        """Return time closest to the given value."""
        idx = np.argmin(np.abs(self.values - value))
        return float(self.times[idx])

    def fft(self, n=None):
        """Return the spectrum using FFT. Resamples to a uniform grid."""
        if n is None:
            n = len(self.values)
        # create uniform grid
        t_min = self.times.min()
        t_max = self.times.max()
        uniform_t = np.linspace(t_min, t_max, len(self.values))
        uniform_v = np.interp(uniform_t, self.times, self.values)
        freqs = np.fft.rfftfreq(n, d=(uniform_t[1] - uniform_t[0]))
        spec = np.fft.rfft(uniform_v, n)
        return Spectrum(freqs, spec)


class Spectrum(BaseSeries):
    """Frequency spectrum with complex values."""

    def __init__(self, freqs, values):
        super().__init__(freqs, np.asarray(values, dtype=complex))

    @property
    def freqs(self):
        return self.x


    def ifft(self, n=None):
        """Return the time-domain signal using IFFT."""
        if n is None:
            n = 2 * (len(self.freqs) - 1)
        if len(self.freqs) > 1:
            dt = 1.0 / ((self.freqs[1] - self.freqs[0]) * n)
        else:
            dt = 1.0
        times = np.arange(n) * dt
        values = np.fft.irfft(self.values, n)
        return Signal(times, values)


def _apply_unary(func, obj):
    if isinstance(obj, BaseSeries):
        return obj.__class__(obj.x, func(obj.values))
    raise TypeError("Unsupported type for unary operation")


def sin(obj):
    """Return the sine of a signal or spectrum."""
    return _apply_unary(np.sin, obj)


def cos(obj):
    """Return the cosine of a signal or spectrum."""
    return _apply_unary(np.cos, obj)


def exp(obj):
    """Return the exponential of a signal or spectrum."""
    return _apply_unary(np.exp, obj)


def db(spectrum):
    """Return magnitude of spectrum in dB."""
    return 20 * np.log10(np.abs(spectrum.values))


def plot(*items):
    """Plot signals or spectra using plotly.

    The resulting figure supports interactive changes to color and line
    style through the plotly UI."""
    fig = go.Figure()
    for idx, item in enumerate(items):
        if isinstance(item, Signal):
            fig.add_trace(
                go.Scatter(
                    x=item.times,
                    y=item.values,
                    mode="lines",
                    name=f"Signal {idx}",
                )
            )
        elif isinstance(item, Spectrum):
            fig.add_trace(
                go.Scatter(
                    x=item.freqs,
                    y=np.abs(item.values),
                    mode="lines",
                    name=f"Spectrum {idx}",
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    y=np.asarray(item),
                    mode="lines",
                    name=f"Data {idx}",
                )
            )
    fig.update_layout(
        xaxis_title="Time/Frequency",
        yaxis_title="Amplitude",
    )
    fig.show()


def nrange(start, stop, step):
    """Return inclusive range similar to :func:`numpy.arange`."""
    return np.arange(start, stop + step, step)


def create(expr, axis):
    """Create a :class:`Signal` or :class:`Spectrum` from an expression.

    Parameters
    ----------
    expr : str
        Expression involving either variable ``t`` for time or ``f`` for
        frequency.  The expression may use numpy functions such as ``sin``,
        ``cos`` and ``exp``.
    axis : array_like
        Values for ``t`` or ``f``.

    Returns
    -------
    Signal or Spectrum
        The newly generated object depending on the variable used in
        ``expr``.
    """

    axis = np.asarray(axis, dtype=float)
    env = {
        "np": np,
        "sin": np.sin,
        "cos": np.cos,
        "exp": np.exp,
    }

    if "t" in expr and "f" in expr:
        raise ValueError("expression should not contain both 't' and 'f'")

    if "t" in expr:
        env["t"] = axis
        values = eval(expr, {"__builtins__": {}}, env)
        return Signal(axis, values)
    if "f" in expr:
        env["f"] = axis
        values = eval(expr, {"__builtins__": {}}, env)
        return Spectrum(axis, values)

    raise ValueError("expression must contain either 't' or 'f'")
