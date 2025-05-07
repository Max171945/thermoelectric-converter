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


def out_result(results: list[str | Result]) -> str:
    """
    Creates a row for the list of results in a reasoned form.
    If the list consists of more than just instances of the Result class,
    then the row will consist of list objects,
    otherwise the row will look like a table with calculated values.
    """
    if all([isinstance(_, Result) for _ in results]):
        res_len = len(results)
        lines = 25
        message = f'{"-" * lines * res_len}\n'
        for attr in Result.__dict__['__annotations__'].keys():
            if attr in ('thermo_emf','result_thermo_emf','temperature'):
                message += f'{"-" * lines * res_len}\n'
            message += f'{attr:25}'
            for result in results:
                message += f'{"+" if attr == "correction" else "":1}{getattr(result, attr):8}{" " * 10}'
            message += f'\n'
        message += f'\n'

        t1, t2 = max(results).temperature, min(results).temperature
        message += f'∆T = {t1}°C - {t2}°C = {t1-t2}°C'
        return message
    return '\n'.join((str(res) for res in results))

