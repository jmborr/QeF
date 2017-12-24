from __future__ import (absolute_import, division, print_function)

from distutils.version import LooseVersion as version
import numpy as np
import lmfit
from lmfit.models import (Model, index_of)


def delta_dirac(x, amplitude=1.0, center=0.0):
    r"""function is zero except for the x-value closest to center.

    At value-closest-to-center, the function evaluates to the amplitude
    divided by the x-spacing.

    Parameters
    ----------
    x sequence of floats
        domain of the function, energy
    amplitude : float
        Integrated intensity of the curve
    center : float
        position of the peak

    Returns
    -------
    values: sequence of floats
        function over the domain
    """
    dx = (x[-1] - x[0]) / (len(x) - 1)  # domain spacing
    y = np.zeros(len(x))
    y[np.abs(x - center).argmin()] = amplitude / dx
    return y


class DeltaDiracModel(Model):
    r"""A function that is zero everywhere except for the x-value closest
    to the center parameter.

    At value-closest-to-center, the model evaluates to the amplitude
    parameter divided by the x-spacing.

    Fitting parameters:
        - integrated intensity ``amplitude`` :math:`A`
        - position of the peak ``center`` :math:`E_0`
    """
    def __init__(self, independent_vars=['x'], prefix='', missing=None,
                 name=None,  **kwargs):
        kwargs.update({'prefix': prefix, 'missing': missing,
                       'independent_vars': independent_vars})
        super(DeltaDiracModel, self).__init__(delta_dirac, **kwargs)

    if version(lmfit.__version__) > version('0.9.5'):
        __init__.__doc__ = lmfit.models.COMMON_INIT_DOC

    def guess(self, y, x=None, **kwargs):
        r"""Guess starting values for the parameters of a model.

        Parameters
        ----------
        y : sequence of floats
            Intensities
        x : sequence of floats
            energy values
        kwargs : dict
            additional optional arguments, passed to model function.

        Returns
        -------
        Parameters
            parameters with guessed values
        """
        amplitude = max(y)
        center = 0.0
        if x is not None:
            center = x[index_of(y, max(y))]
            dx = (x[-1] - x[0]) / (len(x) - 1)  # x-spacing
            amplitude /= dx
        return self.make_params(amplitude=amplitude, center=center)