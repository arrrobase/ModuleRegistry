import numpy as np

from registry import register_module
from modulebase import ModuleBase


@register_module(kw='sig')
class Sigmoid(ModuleBase):
    name = 'Sigmoid'
    phi_labels = ['base', 'amplitude', 'shift', 'kappa']
    kwarg_labels = None

    def get_fn(self, phis, kwargs):

        def fn(signal):
            return phis['base'] \
                   + (0.5 * phis['amplitude']) * 1 \
                   + np.tanh(phis['kappa'] * (signal - phis['shift']))

        return fn
