# SPDX-FileCopyrightText: (C) 2026 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import ipaddress
import logging
import re
import subprocess
from typing import List, Optional

from slugify import slugify

from src.core.internal_types import (
    InternalCamera,
    InternalCameraType,
    InternalGenICamCameraDetails,
)

logger = logging.getLogger("genicam")

ARV_TOOL = "arv-tool-0.8"
GENICAM_CAMERA_ID_PREFIX = "genicam-camera-"
PROTOCOL_GIGE_VISION = "GigEVision"
PROTOCOL_USB3_VISION = "USB3Vision"

# arv-tool prints one "<device_id> (<address>)" line per device.
_DEVICE_LINE_RE = re.compile(r"^(?P<id>\S.*?) \((?P<address>.*)\)$")


def _parse_address(address: str) -> Optional[str]:
    address = address.strip()
    if not address or address == "(null)":
        return None
    return address


def _is_ip_address(address: Optional[str]) -> bool:
    if address is None:
        return False
    try:
        ipaddress.ip_address(address)
    except ValueError:
        return False
    return True


class GenICamCameraDiscovery:
    """Enumerates GigE Vision and USB3 Vision cameras with Aravis `arv-tool-0.8`."""

    @staticmethod
    def _parse_list_output(output: str) -> List[InternalCamera]:
        """Parse the device list printed by `arv-tool-0.8` without arguments."""
        cameras: List[InternalCamera] = []
        for line in output.splitlines():
            m = _DEVICE_LINE_RE.match(line.strip())
            if not m:
                continue

            aravis_id = m.group("id")
            address = _parse_address(m.group("address"))
            # arv-tool does not print the interface; only GigE Vision devices have an IP address.
            protocol = PROTOCOL_GIGE_VISION if _is_ip_address(address) else PROTOCOL_USB3_VISION

            cameras.append(
                InternalCamera(
                    device_id=f"{GENICAM_CAMERA_ID_PREFIX}{slugify(aravis_id)}",
                    device_name=aravis_id,
                    device_type=InternalCameraType.GENICAM,
                    details=InternalGenICamCameraDetails(
                        aravis_id=aravis_id,
                        protocol=protocol,
                        address=address,
                    ),
                )
            )
        return cameras

    def discover_cameras(self) -> List[InternalCamera]:
        cameras: List[InternalCamera] = []
        try:
            result = subprocess.run(
                [ARV_TOOL],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                logger.warning(f"{ARV_TOOL} failed with exit code {result.returncode}")
            else:
                cameras = self._parse_list_output(result.stdout or "")
        except FileNotFoundError:
            logger.error(f"{ARV_TOOL} not found, cannot discover GenICam cameras")
        except subprocess.TimeoutExpired:
            logger.error(f"{ARV_TOOL} command timed out")
        except Exception as e:
            logger.error(f"Error discovering GenICam cameras: {e}", exc_info=True)

        logger.debug(f"Discovered {len(cameras)} GenICam camera(s)")
        return cameras
