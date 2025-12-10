# Versioning Strategy

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version Format: `MAJOR.MINOR.PATCH`

*   **MAJOR**: Incompatible API changes.
*   **MINOR**: Functionality added in a backward compatible manner.
*   **PATCH**: Backward compatible bug fixes.

## How to Bump Version

1.  **Update Code**:
    Edit `src/version.py`:
    ```python
    __version__ = "0.2.0"
    ```

2.  **Commit**:
    ```bash
    git commit -m "chore: bump version to 0.2.0"
    ```

3.  **Tag**:
    ```bash
    git tag v0.2.0
    git push origin v0.2.0
    ```

## Current Version
Check the current version by running:
```bash
python run.py --version
```
