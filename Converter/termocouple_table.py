from bisect import bisect_left
from decimal import Decimal, ROUND_HALF_UP

import constants
from thermoexceptions import ThermoException


class ThermocoupleTable:
    """
    The class contains a type of thermocouple,
    a table for converting temperature to thermal energy
    at a free-end temperature of 0 degrees Celsius
    """

    def __init__(self, thermocouple=constants.DEFAULT_THERMOCOUPLE):
        self.thermocouple = thermocouple if thermocouple in constants.THERMOCOUPLES else constants.DEFAULT_THERMOCOUPLE
        self.data_table = self._load_data()

    def _load_data(self):
        result = []
        with open(constants.THERMOCOUPLES[self.thermocouple], 'r') as file:
            for line in file:
                line = line.replace(',', '.')
                result.extend([Decimal(_) for _ in line.split()])
        return result

    def get_thermo_emf(self, temperature: str)->Decimal:
        """
        Returns the thermal efficiency value depending on the temperature.
        Throws an exception - ThermoException
        if the temperature is outside the range of the thermocouple conversion table.
        """

        temperature: Decimal = Decimal(temperature.replace(',', '.'))

        if not 0 <= temperature <= len(self.data_table)-1:
            raise ThermoException(
                f'The temperature should be in the range from 0 to {len(self.data_table)-1} degrees Celsius. '
                f'Current temperature: {temperature} degrees Celsius.'
            )

        index_prev = int(temperature)
        index_next = (index_prev + 1) % len(self.data_table)
        emf_prev = self.data_table[index_prev]
        emf_next = self.data_table[index_next]
        step = emf_next - emf_prev
        delta = temperature - index_prev
        return (emf_prev + step * delta).quantize(Decimal('1.0000'), ROUND_HALF_UP)

    def get_temperature(self, thermo_emf: str | Decimal)->Decimal:
        """
        Returns the temperature value depending on the thermo-emf.
        Throws an exception - ThermoException
        if the thermo-emf is outside the range of the thermocouple conversion table.
        """

        if isinstance(thermo_emf, str):
            thermo_emf = Decimal(thermo_emf.replace(',', '.'))

        if not 0 <= thermo_emf <= self.data_table[-1]:
            raise ThermoException(f'The thermo-emf should be in the range from {self.data_table[0]}'
                                  f' to {self.data_table[-1]} mV.'
                                  f'Current thermo-emf: {thermo_emf} mV.'
            )

        index = bisect_left(self.data_table, thermo_emf)
        if self.data_table[index] != thermo_emf:
            prev_emf = self.data_table[index-1]
            next_emf = self.data_table[index]
            diff = thermo_emf - prev_emf
            delta = next_emf - prev_emf
            return (index-1 + diff/delta).quantize(Decimal('1.0'), ROUND_HALF_UP)
        return Decimal(index).quantize(Decimal('1.0'))





if __name__ == '__main__':
    th = ThermocoupleTable()
    assert th.get_thermo_emf('1700') == Decimal('17.942')
    assert th.get_temperature(Decimal('17.942')) == Decimal('1700')
    assert th.get_thermo_emf('1220.5') == Decimal('12.194')
    assert th.get_temperature('12.194') == Decimal('1220.5')

