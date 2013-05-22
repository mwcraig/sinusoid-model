import numpy as np


class Sinusoid(object):
    def __init__(self, frequency, amplitude, phase):
        self.amplitude = amplitude
        self.phase = phase
        self.frequency = frequency
        self.angular_frequency = 2 * np.pi * self.frequency

    def __repr__(self):
        return "{} sin(2pi {} t + {})".format(self.amplitude,
                                              self.frequency, self.phase)

    def value(self, t):
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
    >>> model.fit_parameters = [0.5, 1.,  # 1st mode amplitude 0.5, phase 1 rad
                                1.0, 0]   # 2nd mode amplitude 1.0, phase 0 rad
    """
    def __init__(self, frequencies=[], modes=[], amp_phase=[]):
        self._sinusoids = []
        self._frequencies = []
        self.frequencies = frequencies
        self._modes = []
        self.modes = modes
        self.dc_offset = 0
        if amp_phase:
            self.fit_parameters = amp_phase

    def __repr__(self):
        #separator = "\t\t"
        default_format = "{:^{width}}{:^{width}}{:^{width}}{:^{width}}"
        width = 20
        #output = [separator.join(["Mode","Frequency","Amplitude","Phase"])]
        output = [default_format.format("Mode","Frequency","Amplitude","Phase", width=width)]
        dashes = (width-4)*"-"
        output.append(default_format.format(dashes, dashes, dashes, dashes, width=width))
        #DC = separator.join(["DC", "--",str(self.dc_offset),"--"])
        DC = default_format.format("DC", "--",self.dc_offset,"--", width=width)
        output.append(DC)
        # sinusoids = [separator.join([self._pretty_mode(mode),
        #                             str(sinusoid.frequency),
        #                             str(sinusoid.amplitude),
        #                             str(sinusoid.phase)])
        #              for mode, sinusoid in zip(self.modes, self._sinusoids)]
        sinusoids = [default_format.format(self._pretty_mode(mode),
                                           sinusoid.frequency,
                                           sinusoid.amplitude,
                                           sinusoid.phase,
                                           width=width)
                     for mode, sinusoid in zip(self.modes, self._sinusoids)]
        output.extend(sinusoids)
        return "\n".join(output)

    def _pretty_mode(self, mode):
        """
        Generate nice looking string for mode
        """
        mode_str = []
        for freq_num, weight in enumerate(mode):
            if weight>0:
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
        self._frequencies = [f for f in freq]

    @property
    def modes(self):
        return self._modes

    @modes.setter
    def modes(self, mode_list):
        self._modes = []
        self._sinusoids = []
        for mode in mode_list:
            if len(mode) != len(self.frequencies):
                raise ValueError('Wrong number of modes in mode setter in mode {}'.format(mode))
            frequency = (np.array(self.frequencies) * np.array(mode)).sum()
            if not (frequency > 0):
                raise ValueError('Zero frequency mode given.')
            self._sinusoids.append(Sinusoid(frequency, 0., 0.))
            self._modes.append(mode)

    @property
    def fit_parameters(self):
        p = []
        for sinusoid in self._sinusoids:
            p.append(sinusoid.amplitude)
            p.append(sinusoid.phase)
        return p

    @fit_parameters.setter
    def fit_parameters(self, p):
        if  (len(p) % 2) == 1:
            raise ValueError('Must supply an even number of fit parameters')
        for i in range(len(p) / 2):
            self._sinusoids[i].amplitude = p[2*i]
            self._sinusoids[i].phase = p[2*i+1]

    def value(self, t):
        v = 0
        for sinusoid in self._sinusoids:
            v += sinusoid.value(t)

        v += self.dc_offset

        return v

    def fit_to_data(self, time, data, initial_parameters=[]):
        from scipy import optimize

        #data_mean = data.mean()
        fit_data = data #- data_mean
        if not initial_parameters:
            initial_parameters = 0 * np.array(self.fit_parameters) + 1.

        initial_parameters = np.insert(initial_parameters, 0, 1.)

        self.fit_parameters = initial_parameters[1:]
        self.dc_offset = initial_parameters[0]
        print self.fit_parameters

        def errfunc(p, model, t, dat):
            model.fit_parameters = p[1:]
            model.dc_offset = p[0]
            return model.value(t) - dat

        params, junk = optimize.leastsq(errfunc, initial_parameters,
                                        args=(self, time, fit_data))

        self.fit_parameters = params[1:]
        self.dc_offset = params[0]

        for sinusoid in self._sinusoids:
            if sinusoid.amplitude < 0:
                sinusoid.amplitude *= -1
                sinusoid.phase += np.pi

            while sinusoid.phase > 2*np.pi:
                sinusoid.phase -= 2*np.pi

            while sinusoid.phase < 0:
                sinusoid.phase += 2*np.pi



