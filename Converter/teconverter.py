from decimal import Decimal, ROUND_HALF_UP
from random import gauss
from re import findall, fullmatch

from constants import STD_TEMP, TEMP_FREE_END, STD_TEMP_FREE_END, DEFAULT_THERMOCOUPLE, THERMOCOUPLES
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
            return Result(data.temperature, data.thermo_emf, correction, result_thermo_emf, temperature)
        except ThermoException as e:
            return f'Input data error: {e}'
        except Exception as e:
            return f'Unexpected error: {e}'


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
            return Result(temp_en, result_thermo_emf - correction, correction, result_thermo_emf, temp)
        except ThermoException as e:
            return f'Input data error: {e}'
        except Exception as e:
            return f'Unexpected error: {e}'



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


def out_result(results: list[str | Result]) -> str:
    if all([isinstance(_, Result) for _ in results]):
        res_len = len(results)
        message = f'{"-" * 25 * res_len}\n'
        for attr in Result.__dict__['__annotations__'].keys():
            if attr in ('thermo_emf','result_thermo_emf','temperature'):
                message += f'{"-" * 25 * res_len}\n'
            message += f'{attr:25}'
            for result in results:
                message += f'{"+" if attr == "correction" else "":1}{getattr(result, attr):8}{" " * 10}'
            message += f'\n'
        message += f'\n'

        t1, t2 = max(results).temperature, min(results).temperature
        message += f'∆T = {t1}°C - {t2}°C = {t1-t2}°C'
        return message
    return '\n'.join((str(res) for res in results))


def main():
    converter = TEConverter()
    while True:
        cmd = input(f'Select the operating mode (c - calculate, g - generate, '
                    f'ge - generate with additional parameters, t - change thermocouple): ')
        match cmd:
            case 'c':
                temps = input('Enter the measured values in a format like this 22,4-0,1274: ')
                temps = temps.replace(',', '.')
                temps = findall(r'(\d+[.]?\d*)\s*-+\s*(\d+[.]?\d*)', temps)
                measurements = (Measurement(*(Decimal(_) for _ in temp)) for temp in temps)
                res = converter.calculate(*measurements)
                print(out_result(res))

            case 'g':
                temp = input('Input temperature, °C: ').replace(',', '.')
                if fullmatch(r'\d+[.]?\d*', temp):
                    res = converter.generate(float(temp))
                    print(out_result(res))
                else:
                    print('Incorrect temperature value entered.')

            case 'ge':
                default = {'temperature': 1200.0,
                           'quantity': 3,
                           'std_temp': STD_TEMP,
                           'temp_free_end': TEMP_FREE_END,
                           'std_free_end': STD_TEMP_FREE_END,}
                params = {}
                for param in default.keys():
                    data = input(f'Enter {param}{",°C" if param in ("temperature", "temp_free_end") else ""}: ')
                    data = findall(r'\d+[.]?\d*' , data.replace(',', '.'))
                    data = float(data[0]) if data else default[param]
                    params[param] = data if param != 'quantity' else int(data)
                res = converter.generate(**params)
                print(out_result(res))

            case 't':
                thermocouple = input('Enter the type of thermocouple: ')
                if thermocouple in THERMOCOUPLES:
                    converter.change_thermocouple_table(thermocouple)
                    print(f'Current type of thermocouple - {thermocouple}')
                else:
                    print(f'This type of thermocouple - {thermocouple} is not supported')

            case _:
                 print('Unexpected command')
                 exit()


if __name__ == '__main__':
    main()
