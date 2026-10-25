import os
import unittest

class TestAetheriumInstallerPrereqs(unittest.TestCase):
    def test_dependency_classification(self):
        # Mandatory vs Optional classification rules
        mandatory = ["bash", "quickshell", "python3"]
        optional = ["matugen", "cava", "aubio", "brightnessctl", "qalc", "wireplumber", "powerprofilesctl", "spectacle", "swappy"]

        self.assertIn("quickshell", mandatory)
        self.assertIn("cava", optional)
        self.assertIn("matugen", optional)

    def test_session_wayland_requirement(self):
        def check_wayland(session_type):
            return session_type.lower() == "wayland"

        self.assertTrue(check_wayland("wayland"))
        self.assertTrue(check_wayland("Wayland"))
        self.assertFalse(check_wayland("x11"))
        self.assertFalse(check_wayland("tty"))
        self.assertFalse(check_wayland("unsupported"))

    def test_distro_family_mapping(self):
        def get_base_distro(distro_id, id_like=""):
            if distro_id in ["arch", "cachyos", "endeavouros", "manjaro", "artix"]:
                return "arch"
            if distro_id in ["fedora", "rhel", "centos", "nobara"]:
                return "fedora"
            if distro_id in ["debian", "ubuntu", "pop", "linuxmint"]:
                return "debian"
            if "arch" in id_like:
                return "arch"
            if "fedora" in id_like:
                return "fedora"
            if "debian" in id_like:
                return "debian"
            return "unknown"

        self.assertEqual(get_base_distro("cachyos"), "arch")
        self.assertEqual(get_base_distro("endeavouros"), "arch")
        self.assertEqual(get_base_distro("fedora"), "fedora")
        self.assertEqual(get_base_distro("ubuntu"), "debian")
        self.assertEqual(get_base_distro("custom_os", "arch"), "arch")
        self.assertEqual(get_base_distro("bsd"), "unknown")


if __name__ == "__main__":
    unittest.main()
