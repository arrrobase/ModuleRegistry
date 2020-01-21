import re

import numpy as np

from modulebase import ModuleBase
from registry import register_module, KeywordFormatError


@register_module(kw='wc')
class WCBasic(ModuleBase):
    name = 'WC Basic'
    phi_labels = ['coefficients']
    kwarg_labels = None

    def get_fn(self, phis, kwargs):

        def fn(signal):
            return phis['coefficients'] @ signal

        return fn

    def parse_kw(self, kw_string: str):
        regex = r'^(?P<inputs>\d+)x(?P<outputs>\d+)(?:x(?P<bank>\d+))?(?P<options>(?:\.[a-zA-Z])*)$'
        groups = re.match(regex, kw_string)

        if groups is None:
            raise KeywordFormatError(f'Unable to parse kw string "{kw_string}".')
        else:
            groups = groups.groupdict()

        coeff_mean = np.empty((int(groups['inputs']), int(groups['outputs'])))
        coeff_sd = np.empty((int(groups['inputs']), int(groups['outputs'])))

        if groups['options']:
            options = re.findall(r'([a-zA-Z])', groups['options'])

            available_options = {'c', 'g', 'n', 'z', 'o'}
            if not available_options >= set(options):
                raise KeywordFormatError(f'Error in options specified. Specified: "{groups["options"]}".'
                                         f' Available: "{available_options}".')

            if 'g' in options:
                if 'c' in options:
                    raise KeywordFormatError(f'{str(self)} keyword cannot have both "g" and "c": {kw_string}"')

                # make gaussian coefficients here

            if 'c' in options:
                # do 'c' stuff here
                pass

        return {'mean': coeff_mean,
                'sd': coeff_sd}
