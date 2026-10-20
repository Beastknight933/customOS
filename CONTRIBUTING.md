# Contributing to Horizon OS

Thank you for contributing to Horizon OS!

## Principles
1. **Architectural Purity**: KDE Plasma 6 and KWin remain the core desktop foundation; Caelestia acts as the custom interactive shell.
2. **Exclusion Invariants**: Never restore Caelestia's upstream SDDM theme or lockscreen hijacks. Ryoku SDDM and KScreenLocker are mandatory defaults.
3. **Reproducibility**: Pinned dependencies and clear patches are required for all custom components.
4. **Safety**: Destructive operations must always require explicit confirmation.

## Testing Your Changes
Run the comprehensive test suite before submitting pull requests:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
