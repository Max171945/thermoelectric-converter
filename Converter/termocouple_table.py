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
                result.extend([float(_) for _ in line.split()])
        return result

    def get_thermo_emf(self, temperature):
        pass

    def get_temperature(self, thermo_emf):
        pass


if __name__ == '__main__':
    th = ThermocoupleTable('ТВР ВР(А)-1')
    print(th.thermocouple, th.data_table)
