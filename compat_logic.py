"""Pure compatibility / GPU classification helpers (unit-testable without decky)."""

from __future__ import annotations

import re

DEFAULT_FSR4_VARIANT = "rdna23-int8"

RDNA4_NAME_MARKERS = [
    "rx 90",
    "radeon rx 9",
    "9070",
    "9060",
    "navi 44",
    "navi 48",
]
RDNA35_NAME_MARKERS = [
    "radeon 890m",
    "radeon 880m",
    "strix",
    "krackan",
    "ryzen ai",
]
RDNA3_NAME_MARKERS = [
    "radeon 780m",
    "radeon 760m",
    "radeon 740m",
    "rx 7",
    "navi 3",
    "phoenix",
    "hawk",
]
RDNA2_NAME_MARKERS = [
    "van gogh",
    "steam deck",
    "aerith",
    "sephiroth",
    "rx 6",
    "navi 2",
    "680m",
    "660m",
]

AMD_DEVICE_ID_MAP = {
    "0x163f": ("RDNA2 (Van Gogh / Steam Deck)", "rdna23-int8"),
    "0x15bf": ("RDNA3 (Phoenix)", "rdna23-int8"),
    "0x15c8": ("RDNA3 (Phoenix2)", "rdna23-int8"),
    "0x150e": ("RDNA3.5 (Strix Point)", "rdna23-int8"),
    "0x1586": ("RDNA3.5 (Strix)", "rdna23-int8"),
    "0x7550": ("RDNA4 (Navi 48)", "rdna4-native"),
    "0x7551": ("RDNA4 (Navi 48)", "rdna4-native"),
    "0x7590": ("RDNA4 (Navi 44)", "rdna4-native"),
}


def normalize_game_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def parse_curated_markdown(raw: str) -> set[str]:
    """Extract normalized game names from the first column of the wiki table."""
    names: set[str] = set()
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if not first or set(first) <= set("-: "):
            continue
        link_match = re.match(r"\[([^\]]+)\]\([^)]*\)", first)
        if link_match:
            first = link_match.group(1)
        first = first.strip().strip("*").strip()
        low = first.lower()
        if low in ("game", "name") or first.startswith("#"):
            continue
        normalized = normalize_game_name(first)
        if len(normalized) >= 2:
            names.add(normalized)
    return names


def is_curated_match(game_name: str, curated_names: set[str]) -> bool:
    return normalize_game_name(game_name) in curated_names


def classify_game_compat(
    *,
    scan_hit: bool,
    curated_hit: bool,
    override: str | None,
) -> str:
    """Return verified | compatible | incompatible | unknown."""
    if override == "incompatible":
        return "incompatible"
    if override == "compatible":
        return "compatible"
    if curated_hit:
        return "verified"
    if scan_hit:
        return "compatible"
    return "unknown"


def classify_amd_gpu(gpu_name: str, amd_devices: list[dict]) -> tuple[str, str]:
    """Map a GPU name / device ids to (generation, recommended_variant)."""
    name_low = (gpu_name or "").lower()

    def matches(markers: list[str]) -> bool:
        return any(marker in name_low for marker in markers)

    if matches(RDNA4_NAME_MARKERS):
        return "RDNA4", "rdna4-native"
    if matches(RDNA35_NAME_MARKERS):
        return "RDNA3.5", "rdna23-int8"
    if matches(RDNA3_NAME_MARKERS):
        return "RDNA3", "rdna23-int8"
    if matches(RDNA2_NAME_MARKERS):
        return "RDNA2", "rdna23-int8"

    for device in amd_devices:
        mapped = AMD_DEVICE_ID_MAP.get(device.get("device", ""))
        if mapped:
            return mapped[0], mapped[1]

    return "AMD (generic)", DEFAULT_FSR4_VARIANT
