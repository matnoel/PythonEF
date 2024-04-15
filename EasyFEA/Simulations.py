"""This module contains all available simulation classes."""

from .simulations._simu import _Simu, Load_Simu
from .simulations._utils import Save_Force_Displacement, Load_Force_Displacement

# ----------------------------------------------
# Elastic
# ----------------------------------------------

from .simulations._elastic import ElasticSimu, Mesh_Optim_ZZ1

# ----------------------------------------------
# PhaseField
# ----------------------------------------------

from .simulations._phasefield import PhaseFieldSimu

# ----------------------------------------------
# Beam
# ----------------------------------------------

from .simulations._beam import BeamSimu

# ----------------------------------------------
# Thermal
# ----------------------------------------------

from .simulations._thermal import ThermalSimu

# ----------------------------------------------
# DIC
# ----------------------------------------------

try:
    from .simulations._dic import DIC, Load_DIC, Get_Circle
except ModuleNotFoundError:
    # you must install opencv-python
    pass