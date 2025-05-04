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

    def _calculate_one(self, data: Measurement) -> Result:
        """
        Calculates the temperature from the received measurement
        """
        pass

    def calculate(self, data: list[Measurement]) -> list[Result]:
        """
        Calculates temperatures based on the received measurement list
        """
        pass

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