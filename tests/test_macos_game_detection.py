from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import patch

from macos.game_detection import _get_window_titles


class MacOSGameDetectionTests(unittest.TestCase):
    def test_largest_gfn_window_is_checked_before_small_auxiliary_window(self) -> None:
        quartz = types.ModuleType("Quartz")
        setattr(quartz, "kCGNullWindowID", 0)
        setattr(quartz, "kCGWindowListExcludeDesktopElements", 1)
        setattr(quartz, "kCGWindowListOptionOnScreenOnly", 2)
        setattr(
            quartz,
            "CGWindowListCopyWindowInfo",
            lambda *_: [
                {
                    "kCGWindowOwnerPID": 42,
                    "kCGWindowName": "Window",
                    "kCGWindowBounds": {"Width": 66, "Height": 20},
                },
                {
                    "kCGWindowOwnerPID": 42,
                    "kCGWindowName": "ARC Raiders on GeForce NOW",
                    "kCGWindowBounds": {"Width": 1920, "Height": 1080},
                },
            ],
        )

        with patch.dict(sys.modules, {"Quartz": quartz}):
            titles = _get_window_titles([42])

        self.assertEqual(
            titles,
            ["ARC Raiders on GeForce NOW", "Window"],
        )


if __name__ == "__main__":
    unittest.main()
