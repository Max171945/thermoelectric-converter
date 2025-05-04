from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Measurement:
    temperature: str
    thermo_emf: Decimal


@dataclass
class Result:
    thermo_emf: Decimal
    correction: Decimal
    result_thermo_emf: Decimal
    temperature: Decimal
