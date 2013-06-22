import numpy as np


class Sinusoid(object):
    """
    A single sinusoid.

    The sinusoid is of the form: $A\sin(2\pi f t + \delta)$, where $A$ is the
    amplitude, $f$ is the frequency (*not* the angular frequency) and
    $\delta$ is the phase.

    Parameters
    ----------
    frequency : float
        Frequency (*not* angular frequency) of the sinusoid.
    amplitude : float
        Semi-amplitude of the sinusoid.
    delta : float
        Phase of the sinusoid (radians).

    Attributes
    ----------
    angular_frequency : float
        Angular frequency of the sinusoid.
    """
    def __init__(self, frequency, amplitude, phase):
        self.amplitude = amplitude
        self.phase = phase
        self.frequency = frequency
        self.angular_frequency = 2 * np.pi * self.frequency

    def __repr__(self):
        return "{} sin(2pi {} t + {})".format(self.amplitude,
                                              self.frequency, self.phase)

    def __call__(self, t):
        return self.amplitude * np.sin(self.angular_frequency * t + self.phase)


class SinusoidModel(object):
    """
    Represent a combination of sinusoids

    Every model contains, at a minimum, a zero-frequency (i.e. DC) mode.

    >>> from sinusoid import SinusoidModel
    >>> model = SinusoidModel()
    >>> f1 = 1.1    #  frequency, NOT angular frequency
    >>> f2 = 1.7
    >>> f3 = 3.5
    >>> model.frequencies =[f1, f2, f3] # "base" frequencies -- NOT angular
    >>> model.modes = [[1,0,0],     # first mode has frequency f1;
                        [1, 0, 2]]  # second mode has frequency f1 + 2*f2
    >>> model._fit_parameters = [0.5, 1., # 1st mode amplitude 0.5, phase 1 rad
                                1.0, 0]   # 2nd mode amplitude 1.0, phase 0 rad
    """
    def __init__(self, frequencies=None, modes=None, amp_phase=None):
        self._sinusoids = []
        self.frequencies = (frequencies or [])
        self.modes = (modes or [])
        self.dc_offset = 0
        if amp_phase:
            self._fit_parameters = amp_phase

    def __repr__(self):
        default_format = "{:^{width}}{:^{width}}{:^{width}}{:^{width}}"
        width = 20
        output = [default_format.format("Mode", "Frequency", "Amplitude",
                                        "Phase", width=width)]
        dashes = (width - 4) * "-"
        output.append(default_format.format(dashes, dashes, dashes, dashes,
                                            width=width))
        DC = default_format.format("DC", "--", self.dc_offset,
                                   "--", width=width)
        output.append(DC)
        sinusoids = [default_format.format(self._pretty_mode(mode),
                                           sinusoid.frequency,
                                           sinusoid.amplitude,
                                           sinusoid.phase,
                                           width=width)
                     for mode, sinusoid in zip(self.modes, self._sinusoids)]
        output.extend(sinusoids)
        return "\n".join(output)

    def __call__(self, t):
        v = 0
        for sinusoid in self._sinusoids:
            v += sinusoid(t)

        v += self.dc_offset

        return v

    def _pretty_mode(self, mode):
        """
        Generate nice looking string for mode
        """
        mode_str = []
        for freq_num, weight in enumerate(mode):
            if weight != 0:
                if weight == 1:
                    mode_str.append("+f{}".format(freq_num))
                elif weight == -1:
                    mode_str.append("-f{}".format(freq_num))
                else:
                    mode_str.append("{:+}f{}".format(weight, freq_num))
        return "".join(mode_str)

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, freq):
        try:
            self._frequencies = tuple([f for f in freq])
        except TypeError:
            self._frequencies = (freq)

    def add_frequency(self, *frequencies):
        """
        Add one or more frequencies to model

        Parameters
        ----------

        frequencies : float
            One or more frequencies to be appended to the model

        """
        all_frequencies = list(self.frequencies)
        for frequency in frequencies:
            all_frequencies.append(frequency)
        self.frequencies = all_frequencies

    @property
    def modes(self):
        return self._modes

    @modes.setter
    def modes(self, mode_list):
        self._modes = []
        self._sinusoids = []
        for mode in mode_list:
            if len(mode) != len(self.frequencies):
                raise ValueError('Wrong number of modes in mode setter' +
                                 ' for mode {}'.format(mode))
            frequency = (np.array(self.frequencies) * np.array(mode)).sum()
            if not (frequency > 0):
                raise ValueError('Zero frequency mode given.')
            self._sinusoids.append(Sinusoid(frequency, 0., 0.))
            self._modes.append(tuple(mode))
        self._modes = tuple(self._modes)

    @property
    def _fit_parameters(self):
        p = [self.dc_offset]
        for sinusoid in self._sinusoids:
            p.append(sinusoid.amplitude)
            p.append(sinusoid.phase)
        return p

    @_fit_parameters.setter
    def _fit_parameters(self, p):
        self.dc_offset = p[0]
        sines = p[1:]
        if  (len(sines) % 2) == 1:
            raise ValueError('Must supply an even number of fit parameters')
        for i in range(len(sines) / 2):
            self._sinusoids[i].amplitude = sines[2 * i]
            self._sinusoids[i].phase = sines[2 * i + 1]

    def value(self, t):
        v = 0
        for sinusoid in self._sinusoids:
            v += sinusoid(t)

        v += self.dc_offset

        return v

    def fit_to_data(self, time, data, initial_parameters=[]):
        from scipy import optimize

        if not initial_parameters:
            initial_parameters = 0 * np.array(self._fit_parameters) + 1.

        self._fit_parameters = initial_parameters

        def errfunc(p, model, t, dat):
            model._fit_parameters = p
            return model.value(t) - dat

        params, junk = optimize.leastsq(errfunc, initial_parameters,
                                        args=(self, time, data))

        self._fit_parameters = params

        for sinusoid in self._sinusoids:
            if sinusoid.amplitude < 0:
                sinusoid.amplitude *= -1
                sinusoid.phase += np.pi

            while sinusoid.phase > 2 * np.pi:
                sinusoid.phase -= 2 * np.pi

            while sinusoid.phase < 0:
                sinusoid.phase += 2 * np.pi
