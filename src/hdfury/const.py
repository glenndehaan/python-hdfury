"""HDFury Client Constants."""

OPERATION_MODES = {
    "0": "Mode 0 - Splitter TX0/TX1 FRL5 VRR",
    "1": "Mode 1 - Splitter TX0/TX1 UPSCALE FRL5",
    "2": "Mode 2 - Matrix TMDS",
    "3": "Mode 3 - Matrix FRL->TMDS",
    "4": "Mode 4 - Matrix DOWNSCALE",
    "5": "Mode 5 - Matrix RX0:FRL5 + RX1-3:TMDS",
}

TX0_INPUT_PORTS = {
    "0": "Input 0",
    "1": "Input 1",
    "2": "Input 2",
    "3": "Input 3",
    "4": "Copy TX1",
}

TX1_INPUT_PORTS = {
    "0": "Input 0",
    "1": "Input 1",
    "2": "Input 2",
    "3": "Input 3",
    "4": "Copy TX0",
}

OLED_PAGES = {
    "0": "Info",
    "1": "IP",
    "2": "RX Info",
    "3": "HDR 1",
    "4": "HDR 2",
    "5": "IP Info",
}
