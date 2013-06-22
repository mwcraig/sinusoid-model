>>> from sinusoid import SinusoidModel

# there are three ways to set up the model:

# 1. when you create the model

>>> a_model = SinusoidModel(frequencies=[1.2, 2.3],
                        modes=[[1, 0], [0, 1], [1, 1]]
                        )

# note that each mode is a list (or a tuple or a numpy array) with two
# elements, one for each frequency.

# frequencies and modes are immutable 

>>> a_model.frequencies
(1.2, 2.3)
>>> a_model.modes
((1, 0), (0, 1), (1, 1))

# The number of components of each mode must match the number of 
# frequencies:

>>> bad_model = SinusoidModel(frequencies=[1.2, 2.3],
                              modes=[[1, 0, 0]])
ValueError: Wrong number of modes in mode setter for mode [1, 0, 0]

# 2. After you create the model by adding frequencies and modes

>>> another_model = SinusoidModel()
>>> another_model.add_frequency(1.2, 2.3)
>>> another_model.frequencies
(1.2, 2.3)
>>> another_model.modes
()

# 3. Create a new model using another model as initializer

>>> a_model_extended = SinusoidModel(a_model)

>>> a_model_extended.add_frequency(3.4)

# Adding a frequency when modes already exist adds a weight of zero
# to the new frequency

>>> a_model_extended.modes
((1, 0, 0), (0, 1, 0), (1, 1, 0))

# this behavior can be prevented by setting the appropriate keyword

>>> a_model_extended.add_frequency(3.4, extend_modes=False)

# in this case all of the modes are simply deleted:

>>> a_model_extended.modes

()

# TThere is similar behavior if you set the frequencies directly:
# If there is an unambiguous way to generate additional modes with zero,
# or if the number of frequencies doesn't change, then the frequencies
# are updated and the modes unchanged.
#

>>> a_model_extended = SinusoidModel(a_model)
>>> a_model_extended.frequencies
(1.2, 2.3)

# note that in addition to adding a frequency, I've changed the value
# of another.
>>> a_model_extended.frequencies = [1.1, 2.3, 3.4]

>>> a_model_extended.modes
((1, 0, 0), (0, 1, 0), (1, 1, 0))


# If the number of frequencies set is inconsistent with the number of
# components in each mode then an error is generated.
# For example, if a model has three frequencies and modes defined, and one of
# the frequencies is removed an error is generated.
#

>>> a_model_extended.frequencies = [1.1, 2.3]
ValueError: Number of mode components (3) does not match new number of
#   frequencies. Try first setting modes to None and then change the
#   frequencies.

>>> a_model_extended.modes = None

>>> a_model_extended.frequencies = [1.1, 2.3]

>>> a_model_extended.frequencies
(1.1, 2.3)

# To avoid the error, first set the modes to None then change the frequencies.
# Regardless of how initialization was done, modes are added like this:

>>> a_model.add_mode(2, 0)

>>> a_model.add_mode(2, 0, 0)  # number of entries must match number of frequencies

TypeError: Number of components in mode does not match number of frequencies.


