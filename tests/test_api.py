"""Tests for the HDFury api."""

import time
from asyncio import TimeoutError
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError
from aioresponses import aioresponses

from hdfury.api import HDFuryAPI
from hdfury.exceptions import HDFuryConnectionError, HDFuryParseError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def client():
    """HDFury client fixture."""
    api = HDFuryAPI("192.168.1.123")
    # Disable debounce delay to keep tests fast and deterministic
    api._debounce_delay = 0
    yield api
    await api.close()

# ---------------------------------------------------------------------------
# _normalize_state tests
# ---------------------------------------------------------------------------

def test_normalize_state_text_on():
    """Verify that text-based 'on' states are normalized correctly."""
    api = HDFuryAPI("x", session=MagicMock())
    assert api._normalize_state("1") == "on"
    assert api._normalize_state("on") == "on"
    assert api._normalize_state("ON") == "on"

def test_normalize_state_text_off():
    """Verify that text-based 'off' states are normalized correctly."""
    api = HDFuryAPI("x", session=MagicMock())
    assert api._normalize_state("0") == "off"
    assert api._normalize_state("off") == "off"
    assert api._normalize_state("OFF") == "off"

def test_normalize_state_number_output():
    """Verify that states are correctly converted to numeric output."""
    api = HDFuryAPI("x", session=MagicMock())
    assert api._normalize_state("on", output="number") == "1"
    assert api._normalize_state("1", output="number") == "1"
    assert api._normalize_state("off", output="number") == "0"
    assert api._normalize_state("0", output="number") == "0"

@pytest.mark.parametrize("bad", ["yes", "no", "", "2"])
def test_normalize_state_invalid_raises(bad):
    """Verify that invalid state values raise a HDFuryParseError."""
    api = HDFuryAPI("x", session=MagicMock())
    with pytest.raises(HDFuryParseError):
        api._normalize_state(bad)  # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# _request and _request_json tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_request_json_success(client: HDFuryAPI):
    """Verify _request_json returns parsed JSON on success."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/test", body='{"a": 1}')

        result = await client._request_json("/test")
        assert result == {"a": 1}

@pytest.mark.asyncio
async def test_request_json_invalid_json_raises(client: HDFuryAPI):
    """Verify _request_json raises HDFuryParseError for invalid JSON."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/test", body="not-json")

        with pytest.raises(HDFuryParseError):
            await client._request_json("/test")

@pytest.mark.asyncio
async def test_request_non_200_raises_connection_error(client: HDFuryAPI):
    """Verify _request raises HDFuryConnectionError on non-200 responses."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/test", status=500)

        with pytest.raises(HDFuryConnectionError) as exc:
            await client._request("/test")

        assert "Unexpected response from" in str(exc.value)

@pytest.mark.asyncio
async def test_request_timeout(client):
    """Verify that _request raises HDFuryConnectionError on a timeout."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/test", exception=TimeoutError())

        with pytest.raises(HDFuryConnectionError) as exc:
            await client._request("/test")

        assert "Timeout while fetching" in str(exc.value)

@pytest.mark.asyncio
async def test_request_client_error(client):
    """Verify that _request raises HDFuryConnectionError on aiohttp ClientError."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/test", exception=ClientError("Error"))

        with pytest.raises(HDFuryConnectionError) as exc:
            await client._request("/test")

        assert "Request failed" in str(exc.value)

# ---------------------------------------------------------------------------
# get_info / get_board basic behavior
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_info_success(client: HDFuryAPI):
    """Verify get_info returns the correct info dictionary."""
    with aioresponses() as mock:
        mock.get(
            "http://192.168.1.123/ssi/infopage.ssi",
            body='{"opmode": "0"}',
        )

        result = await client.get_info()
        assert result == {"opmode": "0"}

@pytest.mark.asyncio
async def test_get_board_success(client: HDFuryAPI):
    """Verify get_board returns the correct board info dictionary."""
    with aioresponses() as mock:
        mock.get(
            "http://192.168.1.123/ssi/brdinfo.ssi",
            body='{"hostname": "VRROOM-02"}',
        )

        result = await client.get_board()
        assert result == {"hostname": "VRROOM-02"}

# ---------------------------------------------------------------------------
# get_config merge behavior
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_config_merges_cec_and_config(client: HDFuryAPI):
    """Verify get_config merges standard config and CEC config correctly."""
    with aioresponses() as mock:
        mock.get(
            "http://192.168.1.123/ssi/confpage.ssi",
            body='{"autosw": "1", "oled": "1"}',
        )
        mock.get(
            "http://192.168.1.123/ssi/cecpage.ssi",
            body='{"cec0en": "1"}',
        )

        result = await client.get_config()
        assert result == {
            "cec0en": "1",
            "autosw": "1",
            "oled": "1",
        }

@pytest.mark.asyncio
async def test_get_config_cec_failure_is_ignored(client: HDFuryAPI):
    """Verify get_config ignores CEC page errors and returns available config."""
    with aioresponses() as mock:
        mock.get(
            "http://192.168.1.123/ssi/confpage.ssi",
            body='{"autosw": "1"}',
        )
        # cecpage returns 500 -> ignored
        mock.get(
            "http://192.168.1.123/ssi/cecpage.ssi",
            status=500,
        )

        result = await client.get_config()
        assert result == {"autosw": "1"}

@pytest.mark.asyncio
async def test_get_config_cec_invalid_json_is_ignored(client: HDFuryAPI):
    """Verify get_config ignores invalid JSON from CEC page."""
    with aioresponses() as mock:
        mock.get(
            "http://192.168.1.123/ssi/confpage.ssi",
            body='{"autosw": "1"}',
        )
        mock.get(
            "http://192.168.1.123/ssi/cecpage.ssi",
            body="not-json",
        )

        result = await client.get_config()
        assert result == {"autosw": "1"}

# ---------------------------------------------------------------------------
# Command and setter tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_issue_reboot(client: HDFuryAPI):
    """Verify issue_reboot sends the correct command to the device."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/cmd?reboot=", status=200)

        await client.issue_reboot()

@pytest.mark.asyncio
async def test_issue_hotplug(client: HDFuryAPI):
    """Verify issue_hotplug sends the correct command to the device."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/cmd?hotplug=", status=200)

        await client.issue_hotplug()

@pytest.mark.asyncio
async def test_set_operation_mode(client: HDFuryAPI):
    """Verify set_operation_mode sends the correct operation mode command."""
    with aioresponses() as mock:
        mock.get("http://192.168.1.123/cmd?opmode=3", status=200)

        await client.set_operation_mode("3")

@pytest.mark.asyncio
async def test_set_port_selection(client: HDFuryAPI):
    """Verify set_port_selection sends the correct input selection command."""
    with aioresponses() as mock:
        # Note: space encoded as %20 in implementation
        mock.get("http://192.168.1.123/cmd?insel=0%204", status=200)

        await client.set_port_selection("0", "4")

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("autosw", "set_auto_switch_inputs", "on"),
        ("autosw", "set_auto_switch_inputs", "off"),
    ],
)
async def test_set_auto_switch_inputs(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_auto_switch_inputs sends the correct command for each state."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("htpcmode0", "set_htpc_mode_rx0", "on"),
        ("htpcmode1", "set_htpc_mode_rx1", "on"),
        ("htpcmode2", "set_htpc_mode_rx2", "on"),
        ("htpcmode3", "set_htpc_mode_rx3", "on"),
        ("htpcmode0", "set_htpc_mode_rx0", "off"),
        ("htpcmode1", "set_htpc_mode_rx1", "off"),
        ("htpcmode2", "set_htpc_mode_rx2", "off"),
        ("htpcmode3", "set_htpc_mode_rx3", "off"),
    ],
)
async def test_set_htpc_mode(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_htpc_mode commands are sent correctly for each input and state."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("mutetx0audio", "set_mute_tx0_audio", "on"),
        ("mutetx1audio", "set_mute_tx1_audio", "on"),
        ("mutetx0audio", "set_mute_tx0_audio", "off"),
        ("mutetx1audio", "set_mute_tx1_audio", "off"),
    ],
)
async def test_set_mute_tx_audio(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_mute_tx_audio commands are sent correctly for each transmitter and state."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("oled", "set_oled", "on"),
        ("oled", "set_oled", "off"),
    ],
)
async def test_set_oled(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_oled sends the correct command for each OLED state."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("iractive", "set_ir_active", "on"),
        ("iractive", "set_ir_active", "off"),
    ],
)
async def test_set_ir_active(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_ir_active sends the correct command for IR activation states."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("relay", "set_relay", "on"),
        ("relay", "set_relay", "off"),
    ],
)
async def test_set_relay(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_relay sends the correct command for relay states."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("endpoint", "method", "value"),
    [
        ("cec0en", "set_cec_rx0", "1"),
        ("cec1en", "set_cec_rx1", "1"),
        ("cec2en", "set_cec_rx2", "0"),
        ("cec3en", "set_cec_rx3", "0"),
    ],
)
async def test_set_cec_rx(client: HDFuryAPI, endpoint: str, method: str, value: str):
    """Verify set_cec_rx commands are sent correctly for each CEC input."""
    with aioresponses() as mock:
        mock.get(f"http://192.168.1.123/cmd?{endpoint}={value}", status=200)

        await getattr(client, method)(value)

# ---------------------------------------------------------------------------
# Debounce behavior
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_wait_for_debounce_sleeps_when_called_too_fast(client: HDFuryAPI):
    """Verify that _wait_for_debounce sleeps if commands are called too quickly."""
    client._debounce_delay = 2
    client._last_command_time = time.time()

    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        await client._wait_for_debounce()
        sleep_mock.assert_called_once()
