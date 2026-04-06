# ==============================================================================
# vehicles/__init__.py
# ==============================================================================
# Package initializer for the vehicles module.
# Demonstrates ENCAPSULATION at the package level by exposing only the public
# classes that external code needs, hiding internal implementation details.
# ==============================================================================

from vehicles.abstract_vehicle import AbstractVehicle  # Abstract base class (ABSTRACTION)
from vehicles.car import Car                            # Concrete car class (INHERITANCE)
from vehicles.truck import Truck                        # Concrete truck class (POLYMORPHISM)

# __all__ restricts what is exported when using 'from vehicles import *'
# This is ENCAPSULATION at the module level — we control the public interface
__all__ = ["AbstractVehicle", "Car", "Truck"]
