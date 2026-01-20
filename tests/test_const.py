"""Tests for the HDFury constants."""

from hdfury import OPERATION_MODES, TX0_INPUT_PORTS, TX1_INPUT_PORTS


def test_operation_modes_structure():
    """Ensure correct operation modes structure."""
    assert isinstance(OPERATION_MODES, dict)
    assert len(OPERATION_MODES) > 0

def test_operation_modes_keys_are_numeric_strings():
    """Ensure correct operation mode keys."""
    for key in OPERATION_MODES.keys():
        assert isinstance(key, str)
        assert key.isdigit()

def test_operation_modes_values_are_descriptions():
    """Ensure correct operation mode values."""
    for value in OPERATION_MODES.values():
        assert isinstance(value, str)
        assert "Mode" in value

def test_tx0_input_ports_structure():
    """Ensure correct TX0 structure."""
    assert isinstance(TX0_INPUT_PORTS, dict)
    assert len(TX0_INPUT_PORTS) > 0

def test_tx1_input_ports_structure():
    """Ensure correct TX1 structure."""
    assert isinstance(TX1_INPUT_PORTS, dict)
    assert len(TX1_INPUT_PORTS) > 0

def test_tx_input_ports_keys_are_numeric_strings():
    """Ensure correct TX keys."""
    for ports in (TX0_INPUT_PORTS, TX1_INPUT_PORTS):
        for key in ports.keys():
            assert isinstance(key, str)
            assert key.isdigit()

def test_tx_input_ports_values_are_descriptions():
    """Ensure correct TX values."""
    for ports in (TX0_INPUT_PORTS, TX1_INPUT_PORTS):
        for value in ports.values():
            assert isinstance(value, str)
            assert "Input" in value or "Copy" in value

def test_tx_copy_ports_are_symmetric():
    """Ensure Copy TX0/TX1 are correctly mirrored."""
    assert TX0_INPUT_PORTS["4"] == "Copy TX1"
    assert TX1_INPUT_PORTS["4"] == "Copy TX0"
