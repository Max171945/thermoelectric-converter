from decimal import Decimal, ROUND_HALF_UP
from random import gauss

from constants import STD_TEMP, TEMP_FREE_END, STD_TEMP_FREE_END
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
            return Result(data.temperature, data.thermo_emf, correction, result_thermo_emf, temperature)


    def calculate(self, *data: Measurement) -> list[Result]:
        """
        Calculates temperatures based on the received measurement list
        """
        return [self._calculate_one(_) for _ in data]

    def _generate_one(self, temp: float, temp_en: float) -> Result | str:
        """
        Generates a temperature calculation at a single point
        """
        try:
            temp = Decimal(temp).quantize(Decimal('1.0'), ROUND_HALF_UP)
            temp_en = Decimal(temp_en).quantize(Decimal('1.0'), ROUND_HALF_UP)
            correction = self._thermocouple_table.get_thermo_emf(temp_en)
            result_thermo_emf = self._thermocouple_table.get_thermo_emf(temp)
        except ThermoException as e:
            return f'Input data error: {e}'
        except Exception as e:
            return f'Unexpected error: {e}'
        else:
            return Result(temp_en, result_thermo_emf-correction, correction, result_thermo_emf, temp)



    def generate(self, temperature: float, quantity: int = 3,
                 std_temp: float = STD_TEMP,
                 temp_free_end: float = TEMP_FREE_END,
                 std_free_end: float = STD_TEMP_FREE_END) -> list[Result]:
        """
        Generates temperature calculations at multiple points.
        The quantity parameter defines the number of points.
        """
        temperatures = [(gauss(temperature, std_temp),  gauss(temp_free_end, std_free_end))
                        for _ in range(quantity)]
        return [self._generate_one(*temp) for temp in temperatures]


def test_calculate():
    m1, m2 = Measurement(Decimal('-21.9'), Decimal('12.0648')), Measurement(Decimal('22.6'), Decimal('12.0534'))
    m3 = Measurement(Decimal('22.8'), Decimal('12.1014'))
    converter = TEConverter()
    res = converter.calculate(m1, m2, m3)
    print(*res, sep='\n')

def test_generate():
    temperature = float(input('Input temperature: '))
    converter = TEConverter()
    res = converter.generate(temperature)
    print(*res, sep='\n')
    t1, t2 = max(res).temperature, min(res).temperature
    print(f'∆T = {t1}°C - {t2}°C = {t1-t2}°C')

if __name__ == '__main__':
    test_calculate()
    test_generate()
