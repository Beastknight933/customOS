# Horizon OS — Visual Identity & Aesthetics

## Aesthetic Vision
Horizon OS fuses:
1. **Original Horizon Desktop**: High clarity, modern Linux performance, focused minimalism.
2. **Celestia**: Precision curves, geometric status indicators, floating panels.
3. **Lord of the Mysteries (LOTM)**: Arcane tarot tones, mystical dark Victorian undertones, deep shadows.
4. **Dishonored / Steampunk**: Clockwork mechanics, whale-oil blue and amber accents, brass/gold highlights, moody fog and controlled atmospheric transparency.

## Color Palette
| Semantic Name | Hex Code | Purpose |
|---------------|----------|---------|
| Deep Void | `#0a0a0d` | Base background, deep screen canvas |
| Obsidian Surface | `#121218` | Window background, primary panels |
| Elevated Charcoal | `#181822` | Popovers, contextual menus, modals |
| Steampunk Border | `#252533` | Restrained subtle component borders |
| Dunwall Mist | `#5a8cba` | Primary accent, focused highlights, indicators |
| Tarot Amethyst | `#9b72aa` | Secondary accent, badges, audio glow |
| Clockwork Brass | `#b89058` | Highlights, clockwork gears, warning states |
| Whisper Teal | `#4db8a8` | Active states, successful connections |
| Atmospheric Text | `#e8e8ed` | Primary readable typography |
| Muted Gray | `#8c8c9e` | Secondary / placeholder labels |

## Desktop Geometry & Behavior
- **Top Panel**: Caelestia Quickshell bar pinned to the top screen edge, with `showOnHover: true` and `persistent: false` for maximum desktop immersion.
- **Dock**: Floating center-bottom dock, empty pinned applications (`pinnedApps: []`) to keep the workspace clean and unopinionated.
- **KDE Plasma Foundation**: Plasma widgets remain functional; Caelestia's background canvas is disabled (`background.enabled: false`) to avoid layering conflicts.
- **Login Screen**: Ryoku Orbital Clockwork SDDM theme with pure black background.
- **Splash Screen**: Overload Look-and-Feel splash for smooth transition into KDE Plasma.
- **Icon Suite**: Candy Bar (`candy-icons`) vibrant gradient icons.
- **Wallpapers**: Atmospheric wallpapers stored under `/usr/share/wallpapers/horizon/`.
