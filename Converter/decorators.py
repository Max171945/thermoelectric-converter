from thermoexceptions import ThermoException


def try_exc(func):
    def wrap(*args):
        try:
            return func(*args)
        except ThermoException as e:
            return f'Input data error: {e}'
        except Exception as e:
            return f'Unexpected error: {e}'
    return wrap
