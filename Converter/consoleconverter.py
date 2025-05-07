from decimal import Decimal
from re import findall, fullmatch, search

from data_classes import Measurement, out_result
from constants import QUANTITY, STD_TEMP, TEMP_FREE_END, STD_TEMP_FREE_END, THERMOCOUPLES
from teconverter import TEConverter

pattern = r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)' #for float and int

def console_converter(con: TEConverter) -> None:
    while True:
        cmd = input(f'Select the operating mode (e - exit, c - calculate, g - generate, '
                    f'ge - generate with additional parameters, t - change thermocouple): ')
        match cmd:
            case 'c':
                data = input('Enter the measured values in a format like this 22.4-0.1274: ')
                temps = data.replace(',', '.')
                temps = findall(r'(-?\d+[.]?\d*)\s*-+\s*(-?\d+[.]?\d*)', temps)
                if temps:
                    measurements = (Measurement(*(Decimal(_) for _ in temp)) for temp in temps)
                    res = con.calculate(*measurements)
                    print(out_result(res))
                else:
                    print(f'Incorrect data entry format: {data}.')

            case 'g':
                temp = input('Input temperature, °C: ').replace(',', '.')
                if fullmatch(pattern, temp):
                    res = con.generate(float(temp))
                    print(out_result(res))
                else:
                    print('Incorrect temperature value entered.')

            case 'ge':
                default = {'temperature': 1200.0,
                           'quantity': QUANTITY,
                           'std_temp': STD_TEMP,
                           'temp_free_end': TEMP_FREE_END,
                           'std_free_end': STD_TEMP_FREE_END,}
                params = {}
                for param in default.keys():
                    data = input(f'Enter {param}{",°C" if param in ("temperature", "temp_free_end") else ""}: ')
                    data = search(pattern, data.replace(',', '.'))
                    data = float(data[0]) if data else default[param]
                    params[param] = data if param != 'quantity' else int(data)
                res = con.generate(**params)
                print(out_result(res))

            case 't':
                thermocouple = input('Enter the type of thermocouple: ')
                if thermocouple in THERMOCOUPLES:
                    con.change_thermocouple_table(thermocouple)
                    print(f'Current type of thermocouple - {thermocouple}')
                else:
                    print(f'This type of thermocouple - {thermocouple} is not supported')

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