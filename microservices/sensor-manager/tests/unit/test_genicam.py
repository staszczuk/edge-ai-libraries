# SPDX-FileCopyrightText: (C) 2026 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import subprocess
from typing import cast
from unittest.mock import MagicMock, patch

from src.core.genicam import GenICamCameraDiscovery
from src.core.internal_types import InternalCameraType, InternalGenICamCameraDetails

RUN = "src.core.genicam.subprocess.run"

LIST_OUTPUT = """Basler-acA1300-22gm-21234567 (192.168.1.10)
Basler-acA1920-40uc-22003456 ()
FLIR-Blackfly S BFS-U3-16S2M-20123456 ((null))
"""


def _result(stdout="", returncode=0):
    return MagicMock(returncode=returncode, stdout=stdout)


def _details(camera) -> InternalGenICamCameraDetails:
    return cast(InternalGenICamCameraDetails, camera.details)


def test_parse_list_output():
    cameras = GenICamCameraDiscovery._parse_list_output(LIST_OUTPUT)

    assert [c.device_id for c in cameras] == [
        "genicam-camera-basler-aca1300-22gm-21234567",
        "genicam-camera-basler-aca1920-40uc-22003456",
        "genicam-camera-flir-blackfly-s-bfs-u3-16s2m-20123456",
    ]
    assert all(c.device_type == InternalCameraType.GENICAM for c in cameras)
    assert cameras[0].device_name == "Basler-acA1300-22gm-21234567"
    assert _details(cameras[0]) == InternalGenICamCameraDetails(
        aravis_id="Basler-acA1300-22gm-21234567",
        protocol="GigEVision",
        address="192.168.1.10",
    )
    assert (_details(cameras[1]).protocol, _details(cameras[1]).address) == ("USB3Vision", None)
    assert (_details(cameras[2]).protocol, _details(cameras[2]).address) == ("USB3Vision", None)


def test_parse_list_output_ignores_unrelated_lines():
    assert GenICamCameraDiscovery._parse_list_output("") == []
    assert GenICamCameraDiscovery._parse_list_output("No device found\n\n") == []


@patch(RUN)
def test_discover_cameras(mock_run):
    mock_run.return_value = _result(LIST_OUTPUT)

    cameras = GenICamCameraDiscovery().discover_cameras()

    assert len(cameras) == 3
    assert mock_run.call_args.args[0] == ["arv-tool-0.8"]


@patch(RUN)
def test_discover_cameras_nonzero_exit(mock_run):
    mock_run.return_value = _result(LIST_OUTPUT, returncode=1)
    assert GenICamCameraDiscovery().discover_cameras() == []


@patch(RUN, side_effect=FileNotFoundError)
def test_discover_cameras_missing_tool(mock_run):
    assert GenICamCameraDiscovery().discover_cameras() == []


@patch(RUN, side_effect=subprocess.TimeoutExpired(cmd="arv-tool-0.8", timeout=10))
def test_discover_cameras_timeout(mock_run):
    assert GenICamCameraDiscovery().discover_cameras() == []
