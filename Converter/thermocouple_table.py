from bisect import bisect_left
from decimal import Decimal, ROUND_HALF_UP

from constants import THERMOCOUPLES, DEFAULT_THERMOCOUPLE
from thermoexceptions import ThermoException


class ThermocoupleTable:
    """
    The class contains a type of thermocouple,
    a table for converting temperature to thermal energy
    at a free-end temperature of 0 degrees Celsius
    """

    def __init__(self, thermocouple: str = DEFAULT_THERMOCOUPLE):
        self.thermocouple = thermocouple
        self._data_table = self._load_data()

    def _load_data(self) -> list[Decimal]:
        result = []
        file_path = THERMOCOUPLES.get(self.thermocouple, '')
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.replace(',', '.')
                    result.extend([Decimal(_) for _ in line.split()])
            return result
        except FileNotFoundError:
            raise FileNotFoundError(f'The file - {file_path}  does not exist.')

    def get_thermo_emf(self, temperature: Decimal)->Decimal:
        """
        Returns the thermal efficiency value depending on the temperature.
        Throws an exception - ThermoException
        if the temperature is outside the range of the thermocouple conversion table.
        """
        if not 0 <= temperature <= len(self._data_table)-1:
            raise ThermoException(
                f'The temperature should be in the range from 0 to {len(self._data_table)-1} degrees Celsius. '
                f'Current temperature: {temperature} degrees Celsius.'
            )

        index_prev = int(temperature)
        index_next = (index_prev + 1) % len(self._data_table)
        emf_prev = self._data_table[index_prev]
        emf_next = self._data_table[index_next]
        step = emf_next - emf_prev
        delta = temperature - index_prev
        return (emf_prev + step * delta).quantize(Decimal('1.0000'), ROUND_HALF_UP)

    def get_temperature(self, thermo_emf: Decimal)->Decimal:
        """
        Returns the temperature value depending on the thermo-emf.
        Throws an exception - ThermoException
        if the thermo-emf is outside the range of the thermocouple conversion table.
        """

        if not 0 <= thermo_emf <= self._data_table[-1]:
            raise ThermoException(f'The thermo-emf should be in the range from {self._data_table[0]}'
                                  f' to {self._data_table[-1]} mV. '
                                  f'Current thermo-emf: {thermo_emf} mV.'
            )

        index = bisect_left(self._data_table, thermo_emf)
        if self._data_table[index] != thermo_emf:
            prev_emf = self._data_table[index-1]
            next_emf = self._data_table[index]
            diff = thermo_emf - prev_emf
            delta = next_emf - prev_emf
            return (index-1 + diff/delta).quantize(Decimal('1.0'), ROUND_HALF_UP)
        return Decimal(index).quantize(Decimal('1.0'))
