from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Measurement:
    """
    Stores the results of temperature and thermo-emf measurements,
    in degrees Celsius and mV, respectively.
    """
    temperature: Decimal
    thermo_emf: Decimal


@dataclass
class Result:
    """
    Stores the results of calculating temperatures and thermo-emf,
    in degrees Celsius and mV, respectively.
    """
    temperature_free_end: Decimal
    thermo_emf: Decimal
    correction: Decimal
    result_thermo_emf: Decimal
    temperature: Decimal

    def __lt__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.temperature < other.temperature

    def __str__(self):
        return (f'Temperature free end: {self.temperature_free_end} °C; '
                f'Thermo-emf: {self.thermo_emf} mV; '
                f'Correction: {self.correction} mV; '
                f'Result thermo-emf: {self.result_thermo_emf} mV; '
                f'Temperature: {self.temperature} °C')
