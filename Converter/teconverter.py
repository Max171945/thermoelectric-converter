from decimal import Decimal

from thermoexceptions import ThermoException
from data_classes import Measurement, Result
from termocouple_table import ThermocoupleTable


class TEConverter:
    """
    It is responsible for calculating the temperature based on the values of the thermo-emf and
    the temperature of the free end other than zero degrees Celsius,
    and also generates calculations for a given temperature.
    """

    def __init__(self):
        self._thermocouple_table = ThermocoupleTable()

    def change_thermocouple_table(self, thermocouple: str) -> None:
        """
        Changes the type of thermocouple table used
        """
        self._thermocouple_table = ThermocoupleTable(thermocouple)
        return

    def _calculate_one(self, data: Measurement) -> Result | str:
        """
        Calculates the temperature from the received measurement
        """
        try:
            correction = self._thermocouple_table.get_thermo_emf(data.temperature)
            result_thermo_emf = correction + data.thermo_emf
            temperature = self._thermocouple_table.get_temperature(result_thermo_emf)
        except ThermoException as e:
            return f'Input data error: {e}'
        except Exception as e:
            return f'Unexpected error: {e}'
        else:
            return Result(data.thermo_emf, correction, result_thermo_emf, temperature)

    def calculate(self, *data: Measurement) -> list[Result]:
        """
        Calculates temperatures based on the received measurement list
        """
        return [self._calculate_one(_) for _ in data]

    def _generate_one(self, temperature: str) -> Result:
        """
        Generates a temperature calculation at a single point
        """
        pass

    def generate(self, temperature: str, quantity: int = 3) -> list[Result]:
        """
        Generates temperature calculations at multiple points.
        The quantity parameter defines the number of points.
        """
        pass

if __name__ == '__main__':
    m1, m2 = Measurement('22,2', Decimal('12.189')), Measurement('23,1', Decimal('12.194'))
    m3 = Measurement('22,5', Decimal('12.202'))
    converter = TEConverter()
    res = converter.calculate(m1, m2, m3)
    print(*res, sep='\n')
