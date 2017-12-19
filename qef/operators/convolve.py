import numpy as np
from lmfit import CompositeModel


def convolve(model, resolution):
    r"""Convolution of resolution with model data.

    It is assumed that the resolution FWHM is energy independent.

    .. math:: (model \otimes resolution)[n] = \sum_m model[m] * resolution[m-n]

    Parameters
    ----------
    model : numpy.ndarray
        model data
    resolution : numpy.ndarray
        resolution data

    Returns
    -------
    numpy.ndarray
    """
    c = np.convolve(model, resolution, mode='valid')
    if len(model) % len(resolution) == 0:
        c = c[:-1]
    return c / sum(resolution)


class Convolve(CompositeModel):
    r"""Convolution between model and resolution.
    It is assumed that the resolution FWHM is energy independent.
    Non-symmetric energy ranges are allowed (when the range of negative values
    is different than that of positive values)
    """

    def __init__(self, resolution, model, **kws):
        super(Convolve, self).__init__(resolution, model, convolve, **kws)
        self.resolution = resolution
        self.model = model

    def eval(self, params=None, **kwargs):
        res_data = self.resolution.eval(params=params, **kwargs)
        # evaluate model on an extended energy range to avoid boundary effects
        independent_var = self.resolution.independent_vars[0]
        e = kwargs[independent_var]  # energy values
        neg_e = min(e) - np.flip(e[np.where(e > 0)], axis=0)
        pos_e = max(e) - np.flip(e[np.where(e < 0)], axis=0)
        i_start = int(len(e)/2) - len(neg_e)
        i_end = i_start + len(e)
        e = np.concatenate((neg_e, e, pos_e))
        kwargs.update({independent_var: e})
        model_data = self.model.eval(params=params, **kwargs)
        return convolve(model_data, res_data)#[i_start: i_end]
