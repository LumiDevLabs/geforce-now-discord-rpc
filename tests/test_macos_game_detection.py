from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import patch

from macos.game_detection import _get_window_titles


class MacOSGameDetectionTests(unittest.TestCase):
    def test_window_query_includes_gfn_windows_on_other_spaces(self) -> None:
        received_options: list[int] = []
        quartz = types.ModuleType("Quartz")
        setattr(quartz, "kCGNullWindowID", 0)
        setattr(quartz, "kCGWindowListExcludeDesktopElements", 1)
        setattr(quartz, "kCGWindowListOptionOnScreenOnly", 2)

        def copy_window_info(options: int, _: int) -> list[dict[str, object]]:
            received_options.append(options)
            return []

        setattr(quartz, "CGWindowListCopyWindowInfo", copy_window_info)

        with patch.dict(sys.modules, {"Quartz": quartz}):
            _get_window_titles([42])

        self.assertEqual(received_options, [1])

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
