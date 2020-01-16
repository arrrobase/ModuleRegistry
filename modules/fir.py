import numpy as np
from nems.modules.fir import _offset_coefficients, per_channel

from modulebase import ModuleBase
from registry import register_module


class FIRBase(ModuleBase):
    # because not passed to registry, only children who are in registry need to implement interface
    def offset_coefficients(self, coefficients, offsets, fs, pad_bins):
        return _offset_coefficients(coefficients, offsets, fs, pad_bins=pad_bins)

    def per_channel(self, signal, coefficients, bank_count=1, non_causal=False, rate=1, cross_channels=False):
        return per_channel(signal, coefficients, bank_count, non_causal, rate, cross_channels)


@register_module(kw='fir')
class FIRBasic(FIRBase):
    name = 'FIR Basic'
    phi_labels = ['coefficients']
    kwarg_labels = ['fs', 'non_causal', 'offsets']
    kw = 'fir'

    def get_fn(self, phis, kwargs):
        coefficients = phis['coefficients']
        offsets = kwargs['offsets']

        if not np.all(offsets == 0):
            coefficients = self.offset_coefficients(coefficients, offsets, kwargs['fs'])

        def fn(signal):
            return self.per_channel(signal, coefficients, non_causal=kwargs['non_causal'], rate=1)

        return fn
