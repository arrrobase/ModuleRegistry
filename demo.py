import logging
from pathlib import Path

import numpy as np
from nems.signal import PointProcess

from registry import ModuleRegistry

# not sure why NEMS defaults logging level so low
logging.getLogger().setLevel(level=logging.WARNING)

# this would be done depending on dirs listed in settings.py
default_module_dir = Path(r'modules').absolute()
ModuleRegistry.load_directory(default_module_dir)

# Example of loading by single file. This will override the keywords and generate a
# warning. Notice the different path specs since couldn't resolve spec dir.
fir_module = Path(r'modules/fir.py').absolute()
sig_module = Path(r'modules/nonlinearity.py').absolute()
ModuleRegistry.load_module(fir_module)
ModuleRegistry.load_module(sig_module)

# setup a test signal
points = np.random.randint(0, 100, size=(10, 600))
names = [f'channel{i}' for i in range(points.shape[0])]
data = dict(zip(names, points))
s = PointProcess(fs=60, data=data, name='test', recording='test')

# setup and activate registry, and display registry contents
module_registry = ModuleRegistry().activate()
print()
print(module_registry, end='\n\n')
print(module_registry.kw_registry, end='\n\n')

# Sigmoid
sig_phis = {'base': 0, 'amplitude': 1, 'shift': 0, 'kappa': 1}
sig_kwargs = None

m_sig = module_registry.kw_registry['sig']  # find a module by keyword
tx = s.transform(m_sig(phis=sig_phis, kwargs=sig_kwargs))
print(f'{m_sig.name} applied')

# FIR Basic
fir_phis = {'coefficients': np.array(range(30)).reshape((10, 3))}
fir_kwargs = {'fs': 60, 'non_causal': False, 'offsets': 0}

m_fir = module_registry['modules.fir.FIRBasic']  # find a module by pathspec
tx2 = s.transform(m_fir(phis=fir_phis, kwargs=fir_kwargs))
print(f'{m_fir.name} applied')

# alternatively, piping
s = (s.transform(m_sig(phis=sig_phis, kwargs=sig_kwargs))
      .transform(m_fir(phis=fir_phis, kwargs=fir_kwargs))
     )

print()
print(module_registry.get_by_kw('wc').parse_kw('5x2.g'))
