import numpy as np
import pysig as ps


def sample_signals():
    """Return two example signals of different lengths."""
    s1 = ps.Signal([1e-3, 2e-3, 3e-3], [1.2, 2.3, 1.9])
    s2 = ps.Signal([1e-3, 2.1e-3, 2.3e-3, 4e-3], [1.3, 2.3, 1.9, 4])
    return s1, s2


def test_fft_plot():
    """Combine spectra of two signals and plot in dB."""
    s1, s2 = sample_signals()
    sp = s1.fft() + s2.fft()
    ps.plot(ps.db(sp))


def test_time_ops():
    """Perform simple arithmetic on signals and display results."""
    s1, s2 = sample_signals()
    s3 = s1 + s2
    s4 = 2 * s1
    ps.plot(s3, s4)
    print("value at 1.3e-3:", s3.value(1.3e-3))
    print("closest time to 1.8:", s3.time(1.8))


def test_create_save_load():
    """Generate a sine wave, save and reload from JSON."""
    axis = ps.nrange(0, 0.01, 0.001)
    sig = ps.create("sin(200*t)", axis)
    filename = "temp_signal.json"
    sig.dump(filename)
    restored = ps.Signal.load(filename)
    print("round-trip equal:", np.allclose(sig.values, restored.values))


if __name__ == "__main__":
    test_fft_plot()
    test_time_ops()
    test_create_save_load()
