from pathlib import Path

DEFAULT_THERMOCOUPLE = 'ТПП(S)'
THERMOCOUPLES = {
     'ТПП(S)': Path('../Data/TPP(S).txt'),
     'ТВР ВР(А)-1': Path('../Data/TVR VR(A)-1.txt'),
}

TEMP_FREE_END = 22.0
STD_TEMP_FREE_END = 0.5
STD_TEMP = 1.4
