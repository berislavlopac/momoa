from datetime import datetime, timezone
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

import pytest

from momoa.format import StringFormat


@pytest.mark.parametrize(
    "format_name, value, deserialized",
    (
        pytest.param("date-time", "2002-05-22", datetime(2002, 5, 22), id="date"),
        pytest.param(
            "date-time",
            "2002-05-22T11:45:00",
            datetime(2002, 5, 22, 11, 45),
            id="datetime",
        ),
        pytest.param(
            "date-time",
            "2002-05-22T11:45:00Z",
            datetime(2002, 5, 22, 11, 45, tzinfo=timezone.utc),
            id="datetime with timezone",
        ),
        pytest.param("ipv4", "192.168.0.1", IPv4Address("192.168.0.1"), id="IPv4"),
        pytest.param("ipv6", "2001:db8::1000", IPv6Address("2001:db8::1000"), id="IPv6"),
        pytest.param(
            "uuid",
            "4cbf6ab8-1785-4264-a011-ee655edbe4f5",
            UUID("4cbf6ab8-1785-4264-a011-ee655edbe4f5"),
            id="UUID",
        ),
        pytest.param("unknown", "blabla", "blabla", id="unknown format"),
    ),
)
def test_strings_are_deserialised_to_correct_value(format_name, value, deserialized):
    fmt = StringFormat(format_name)
    assert fmt.from_(value) == deserialized


@pytest.mark.parametrize(
    "format_name, serialized, value",
    (
        pytest.param("date-time", "2002-05-22", datetime(2002, 5, 22), id="date"),
        pytest.param(
            "date-time",
            "2002-05-22T11:45:00",
            datetime(2002, 5, 22, 11, 45),
            id="datetime",
        ),
        pytest.param(
            "date-time",
            "2002-05-22T11:45:00+00:00",
            datetime(2002, 5, 22, 11, 45, tzinfo=timezone.utc),
            id="datetime with timezone",
        ),
        pytest.param("unknown", "blabla", "blabla", id="unknown format"),
        pytest.param(
            "uuid",
            "4cbf6ab8-1785-4264-a011-ee655edbe4f5",
            UUID("4cbf6ab8-1785-4264-a011-ee655edbe4f5"),
            id="UUID",
        ),
    ),
)
def test_values_are_serialized_to_correct_format(format_name, serialized, value):
    fmt = StringFormat(format_name)
    assert fmt.to_(value) == serialized
