import os
import json
import unittest
import re

class TestAetheriumTokens(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.tokens_path = os.path.join(self.root_dir, "desktop", "config", "tokens.json")

    def test_tokens_file_exists(self):
        self.assertTrue(os.path.exists(self.tokens_path), f"Tokens file missing: {self.tokens_path}")

    def test_tokens_valid_json(self):
        with open(self.tokens_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertIn("appearance", data)
        self.assertIn("semantics", data)

    def test_appearance_tokens_structure(self):
        with open(self.tokens_path, "r", encoding="utf-8") as f:
            data = json.load(f)["appearance"]

        for category in ["rounding", "spacing", "padding", "fontSize", "animDurations"]:
            self.assertIn(category, data, f"Missing category: {category}")
            self.assertIsInstance(data[category], dict)

        # Ensure positive values
        for key, val in data["rounding"].items():
            self.assertGreater(val, 0)
        for key, val in data["spacing"].items():
            self.assertGreater(val, 0)
        for key, val in data["padding"].items():
            self.assertGreater(val, 0)
        for key, val in data["animDurations"].items():
            self.assertGreater(val, 0)

    def test_semantic_colors(self):
        with open(self.tokens_path, "r", encoding="utf-8") as f:
            colors = json.load(f)["semantics"]["color"]

        required_keys = [
            "surfaceBase", "surfacePanel", "surfaceElevated", "surfaceContainer",
            "textPrimary", "textSecondary", "textDim",
            "accentPrimary", "accentSecondary", "accentHighlight",
            "borderSubtle", "borderFocused"
        ]
        for key in required_keys:
            self.assertIn(key, colors, f"Missing semantic color key: {key}")
            val = colors[key]
            # Must be valid hex or rgba
            is_hex = bool(re.match(r"^#[0-9a-fA-F]{6}$", val))
            is_rgba = bool(val.startswith("rgba(") or val.startswith("rgb("))
            self.assertTrue(is_hex or is_rgba, f"Invalid color format for {key}: {val}")


if __name__ == "__main__":
    unittest.main()
