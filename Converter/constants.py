from pathlib import Path

CWD = Path().cwd()
CWD = CWD if 'Converter' not in CWD.parts else CWD.parent

DEFAULT_THERMOCOUPLE: str = 'ТПП(S)'
THERMOCOUPLES: dict[str: str] = {
     'ТПП(S)': CWD / Path('Data/TPP(S).txt'),
     'ТВР ВР(А)-1': CWD / Path('Data/TVR VR(A)-1.txt'),
}

QUANTITY: int = 3
TEMP_FREE_END: float = 22.0
STANDARD_DEVIATION_TEMP_FREE_END: float = 0.5
STANDARD_DEVIATION_TEMP: float = 1.4
