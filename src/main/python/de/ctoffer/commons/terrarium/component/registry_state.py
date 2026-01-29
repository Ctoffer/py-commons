from enum import Enum


class TerrariumState(Enum):
    SCANNING = 1
    INITIALIZING = 2
    INITIALIZED = 3
    POST_CONSTRUCTING = 4
    POST_CONSTRUCTED = 5
    PRE_DESTROYING = 6
    DESTROYED = 5