from bisect import bisect_left
from decimal import Decimal, ROUND_HALF_UP

import constants


class ThermocoupleTable:
    """
    The class contains a type of thermocouple,
    a table for converting temperature to thermal energy
    at a free-end temperature of 0 degrees Celsius
    """

    def __init__(self, thermocouple='ТПП(S)'):
        self.thermocouple = thermocouple
        self.data_table = self._load_data()

    def _load_data(self):
        result = []
        with open(constants.THERMOCOUPLE[self.thermocouple], 'r') as file:
            for line in file:
                line = line.replace(',', '.')
                result.extend([Decimal(_) for _ in line.split()])
        return result

    def get_thermo_emf(self, temperature: str):
        temperature = Decimal(temperature.replace(',', '.'))
        index_prev = int(temperature)
        index_next = index_prev + 1
        emf_prev = self.data_table[index_prev]
        emf_next = self.data_table[index_next]
        step = emf_next - emf_prev
        delta = temperature - index_prev
        return (emf_prev + step * delta).quantize(Decimal('1.0000'), ROUND_HALF_UP)

    def get_temperature(self, thermo_emf: str):
        thermo_emf = Decimal(thermo_emf)
        index = bisect_left(self.data_table, thermo_emf)
        if self.data_table[index] == thermo_emf:
            return Decimal(thermo_emf).quantize(Decimal('1.0'))
        prev = self.data_table[index-1]
        next = self.data_table[index]
        diff = thermo_emf - prev
        delta = next - prev
        return (index-1 + diff/delta).quantize(Decimal('1.0'), ROUND_HALF_UP)





if __name__ == '__main__':
    th = ThermocoupleTable()
    print(th.get_thermo_emf('10'))
    t = th.get_thermo_emf('10,9')
    print(t)
    print(th.get_temperature(str(t)))
