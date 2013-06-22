import pytest
import numpy as np
import sinusoid


class TestSinusoid(object):

    def setup_class(self):
        self.freq = 2.1  # there is no logic to this value
        self.ampl = 1.4
        self.phase = np.pi / 3

    def value(self, x):
        return self.ampl * np.sin(2 * np.pi * self.freq * x + self.phase)

    def test_call(self):
        sinu = sinusoid.Sinusoid(self.freq, self.ampl, self.phase)
        x = np.linspace(-2/self.freq, 3*self.freq, num=1000)
        print self.freq
        assert ((sinu(x) - self.value(x)) == 0).all()

    def teardown_class(self):
        pass


class TestSinusoidalModel(object):

# Add setup of a single mode
# Add test of value of single mode -- can't, no way to assign
# amplitude/phase except by fitting.
# Commit this package of changes.

    def setup_class(self):
        self.f1 = 2.1
        self.ampl = 1.4
        self.phase = 0
        self.double_mode = {'freq': [1.2, 2.3],
                            'modes':[[1, 0], [0, 1], [1, 1]]}
        self.double_model = sinusoid.SinusoidModel(frequencies=self.double_mode['freq'],
                                       modes=self.double_mode['modes'])
# Then...
#   + Change all things that are currently lists to immutable tuples
#   + Add tests for immutability of frequencies, modes
#   + Add method for adding frequency that returns new instance.
#   + Add method for adding new mode that returns new instance.
#   + Add method for calculating "mode" frequencies.
    def test_frequencies_are_immutable(self):
        assert self.double_model.frequencies == tuple(self.double_mode['freq'])

    def test_modes_are_immutable(self):
        ## make sure it is impossible to change mode defitions.
        model = sinusoid.SinusoidModel(frequencies=self.double_mode['freq'],
                                       modes=self.double_mode['modes'])
        expected_modes = tuple([tuple(mode) for mode in self.double_mode['modes']])
        assert (model.modes == expected_modes)

    def test_number_modes_matches_frequencies(self):
        with pytest.raises(ValueError):
            bad_model = sinusoid.SinusoidModel(frequencies=self.double_mode['freq'],
                                               modes=[[1, 0, 0 ]])

    def test_add_frequency_to_empty_model(self):
        empty_model = sinusoid.SinusoidModel()
        empty_model.add_frequency(self.double_mode['freq'][0],
                                  self.double_mode['freq'][1])
        assert empty_model.frequencies == tuple(self.double_mode['freq'])
