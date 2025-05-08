from decimal import Decimal
from re import findall, fullmatch, search

from data_classes import Measurement, out_result
from constants import QUANTITY, STANDARD_DEVIATION_TEMP, TEMP_FREE_END, STANDARD_DEVIATION_TEMP_FREE_END, THERMOCOUPLES
from teconverter import TEConverter


# For float and int
PATTERN: str = r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)'


def _calculate(con: TEConverter) -> None:
    """
    The handler for the calculate command.
    """
    data = input('Enter the measured values in a format like this 22.4-0.1274: ')
    temps = data.replace(',', '.')
    temps = findall(r'(-?\d+[.]?\d*)\s*-+\s*(-?\d+[.]?\d*)', temps)
    if temps:
        measurements = (Measurement(*(Decimal(_) for _ in temp)) for temp in temps)
        res = con.calculate(*measurements)
        print(out_result(res))
    else:
        print(f'Incorrect data entry format: {data}.')


def _generate(con: TEConverter) -> None:
    """
    The handler for the generate command.
    """
    temp = input('Input temperature, °C: ').replace(',', '.')
    if fullmatch(PATTERN, temp):
        res = con.generate(float(temp))
        print(out_result(res))
    else:
        print('Incorrect temperature value entered.')


def _generate_extend(con: TEConverter) -> None:
    """
    The handler for the calculate command with additional parameters for generating.
    """
    default = {'temperature': 1200.0,
               'quantity': QUANTITY,
               'std_temp': STANDARD_DEVIATION_TEMP,
               'temp_free_end': TEMP_FREE_END,
               'std_free_end': STANDARD_DEVIATION_TEMP_FREE_END, }
    params = {}
    for param in default.keys():
        data = input(f'Enter {param}{",°C" if param in ("temperature", "temp_free_end") else ""}: ')
        data = search(PATTERN, data.replace(',', '.'))
        data = float(data[0]) if data else default[param]
        params[param] = data if param != 'quantity' else int(data)
    res = con.generate(**params)
    print(out_result(res))

def _change_thermocouple_table(con: TEConverter) -> None:
    """
    The handler for the change thermocouple table.
    """
    thermocouple = input('Enter the type of thermocouple: ')
    if thermocouple in THERMOCOUPLES:
        con.change_thermocouple_table(thermocouple)
        print(f'Current type of thermocouple - {thermocouple}')
    else:
        print(f'This type of thermocouple - {thermocouple} is not supported')


def console_converter(con: TEConverter) -> None:
    """
    Processes commands entered by the user and outputs the result to the console.
    """
    while True:
        cmd = input(f'Select the operating mode (e - exit, c - calculate, g - generate, '
                    f'ge - generate with additional parameters, t - change thermocouple): ')
        match cmd:
            case 'c':
                _calculate(con)
            case 'g':
                _generate(con)
            case 'ge':
                _generate_extend(con)
            case 't':
                _change_thermocouple_table(con)
            case 'e'| '\x1b':
                exit()
            case _:
                print(f'The {cmd} command is not supported')

if __name__ == '__main__':
    try:
        converter = TEConverter()
        console_converter(converter)
    except (Exception, KeyboardInterrupt) as exc:
        print(exc)