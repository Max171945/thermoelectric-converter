from decimal import Decimal, ROUND_HALF_UP
from random import gauss

from decorators import try_exc
from constants import STD_TEMP, TEMP_FREE_END, STD_TEMP_FREE_END
from data_classes import Measurement, Result
from termocouple_table import ThermocoupleTable


class TEConverter:
    """
    It is responsible for calculating the temperature based on the values of the thermo-emf and
    the temperature of the free end other than zero degrees Celsius,
    and also generates calculations for a given temperature.
    Contains an object of the ThermocoupleЕable class,
    which can throw a FileNotFoundError exception and others.
    """

    def __init__(self):
        self._thermocouple_table = ThermocoupleTable()


    def change_thermocouple_table(self, thermocouple: str) -> None:
        """
        Changes the type of thermocouple table used
        """
        self._thermocouple_table = ThermocoupleTable(thermocouple)
        return


    @try_exc
    def _calculate_one(self, data: Measurement) -> Result | str:
        """
        Calculates the temperature from the received measurement
        """
        correction = self._thermocouple_table.get_thermo_emf(data.temperature)
        result_thermo_emf = correction + data.thermo_emf
        temperature = self._thermocouple_table.get_temperature(result_thermo_emf)
        return Result(data.temperature, data.thermo_emf, correction, result_thermo_emf, temperature)


    def calculate(self, *data: Measurement) -> list[Result]:
        """
        Calculates temperatures based on the received measurement list
        """
        return [self._calculate_one(_) for _ in data]


    @try_exc
    def _generate_one(self, temp: float, temp_en: float) -> Result | str:
        """
        Generates a temperature calculation at a single point
        """
        temp = Decimal(temp).quantize(Decimal('1.0'), ROUND_HALF_UP)
        temp_en = Decimal(temp_en).quantize(Decimal('1.0'), ROUND_HALF_UP)
        correction = self._thermocouple_table.get_thermo_emf(temp_en)
        result_thermo_emf = self._thermocouple_table.get_thermo_emf(temp)
        return Result(temp_en, result_thermo_emf - correction, correction, result_thermo_emf, temp)


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

