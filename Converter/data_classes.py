from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Measurement:
    temperature: Decimal
    thermo_emf: Decimal


@dataclass
class Result:
    temperature_free_end: Decimal
    thermo_emf: Decimal
    correction: Decimal
    result_thermo_emf: Decimal
    temperature: Decimal

    def __lt__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.temperature < other.temperature
