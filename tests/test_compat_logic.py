"""Unit tests for compatibility parsing and classification."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from compat_logic import (
    classify_amd_gpu,
    classify_game_compat,
    is_curated_match,
    normalize_game_name,
    parse_curated_markdown,
)

FIXTURES = Path(__file__).parent / "fixtures"
CURATED_FIXTURE = FIXTURES / "Compatibility-List.md"


class NormalizeGameNameTests(unittest.TestCase):
    def test_strips_punctuation_and_case(self):
        self.assertEqual(normalize_game_name("Alan Wake 2"), "alanwake2")
        self.assertEqual(normalize_game_name("007 First Light"), "007firstlight")

    def test_empty(self):
        self.assertEqual(normalize_game_name(""), "")


class ParseCuratedMarkdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not CURATED_FIXTURE.exists():
            raise unittest.SkipTest(f"Missing fixture: {CURATED_FIXTURE}")
        cls.raw = CURATED_FIXTURE.read_text(encoding="utf-8")
        cls.names = parse_curated_markdown(cls.raw)

    def test_parses_hundreds_of_real_entries(self):
        self.assertGreaterEqual(len(self.names), 600)

    def test_known_verified_titles(self):
        for title in (
            "171",
            "Alan Wake 2",
            "Cyberpunk 2077",
            "Clair Obscur: Expedition 33",
            "Hogwarts Legacy",
        ):
            self.assertIn(
                normalize_game_name(title),
                self.names,
                msg=f"Expected curated entry for {title!r}",
            )

    def test_ignores_table_header(self):
        self.assertNotIn("game", self.names)

    def test_sample_table_rows(self):
        sample = "\n".join(
            [
                "| Game | Compatibility | Notes |",
                "| --- | --- | --- |",
                "| [Alan Wake 2](Alan-Wake-2) | ✅ | DLSS |",
                "| Plain Title | ✅ | XeSS |",
                "| *Bold Title* | ✅ | FSR |",
            ]
        )
        names = parse_curated_markdown(sample)
        self.assertEqual(
            names,
            {
                normalize_game_name("Alan Wake 2"),
                normalize_game_name("Plain Title"),
                normalize_game_name("Bold Title"),
            },
        )


class ClassifyGameCompatTests(unittest.TestCase):
    def test_verified_beats_scan(self):
        self.assertEqual(
            classify_game_compat(scan_hit=True, curated_hit=True, override=None),
            "verified",
        )

    def test_compatible_from_scan_only(self):
        self.assertEqual(
            classify_game_compat(scan_hit=True, curated_hit=False, override=None),
            "compatible",
        )

    def test_verified_from_curated_only(self):
        self.assertEqual(
            classify_game_compat(scan_hit=False, curated_hit=True, override=None),
            "verified",
        )

    def test_unknown_when_no_signals(self):
        self.assertEqual(
            classify_game_compat(scan_hit=False, curated_hit=False, override=None),
            "unknown",
        )

    def test_manual_override_wins(self):
        self.assertEqual(
            classify_game_compat(scan_hit=True, curated_hit=True, override="incompatible"),
            "incompatible",
        )
        self.assertEqual(
            classify_game_compat(scan_hit=False, curated_hit=False, override="compatible"),
            "compatible",
        )


class CuratedMatchIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not CURATED_FIXTURE.exists():
            raise unittest.SkipTest(f"Missing fixture: {CURATED_FIXTURE}")
        cls.curated_names = parse_curated_markdown(CURATED_FIXTURE.read_text(encoding="utf-8"))

    def test_steam_library_name_matches_fixture(self):
        steam_names = [
            ("Cyberpunk 2077", "verified"),
            ("Counter-Strike 2", "unknown"),  # not on OptiScaler curated list
            ("Alan Wake 2", "verified"),
        ]
        for name, expected in steam_names:
            curated_hit = is_curated_match(name, self.curated_names)
            compat = classify_game_compat(scan_hit=False, curated_hit=curated_hit, override=None)
            if expected == "verified":
                self.assertEqual(compat, "verified", msg=name)
            else:
                self.assertEqual(compat, "unknown", msg=name)


class UpscalerScanIntegrationTests(unittest.TestCase):
    def test_detects_nvngx_in_fake_game_tree(self):
        # Import main only inside the test so decky can be mocked.
        import sys
        from unittest.mock import MagicMock

        sys.modules.setdefault("decky", MagicMock())
        from main import Plugin  # noqa: WPS433

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nvngx_dlss.dll").write_bytes(b"")
            upscalers = Plugin()._scan_game_upscalers(root)
            self.assertEqual(upscalers, ["dlss"])
            compat = classify_game_compat(scan_hit=True, curated_hit=False, override=None)
            self.assertEqual(compat, "compatible")


class ClassifyAmdGpuTests(unittest.TestCase):
    def test_strix_point_device_id(self):
        gen, variant = classify_amd_gpu("", [{"device": "0x150e"}])
        self.assertEqual(gen, "RDNA3.5 (Strix Point)")
        self.assertEqual(variant, "rdna23-int8")

    def test_legion_go_style_name(self):
        gen, variant = classify_amd_gpu("AMD Radeon 890M Graphics", [])
        self.assertEqual(gen, "RDNA3.5")
        self.assertEqual(variant, "rdna23-int8")

    def test_rdna4_discrete(self):
        gen, variant = classify_amd_gpu("Radeon RX 9070 XT", [])
        self.assertEqual(gen, "RDNA4")
        self.assertEqual(variant, "rdna4-native")


if __name__ == "__main__":
    unittest.main()
