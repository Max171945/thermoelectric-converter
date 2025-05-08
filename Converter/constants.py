from pathlib import Path

DEFAULT_THERMOCOUPLE: str = 'ТПП(S)'
THERMOCOUPLES: dict[str: str] = {
     'ТПП(S)': Path('../Data/TPP(S).txt'),
     'ТВР ВР(А)-1': Path('../Data/TVR VR(A)-1.txt'),
}

QUANTITY: int = 3
TEMP_FREE_END: float = 22.0
STANDARD_DEVIATION_TEMP_FREE_END: float = 0.5
STANDARD_DEVIATION_TEMP: float = 1.4
