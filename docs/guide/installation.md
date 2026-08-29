# Installation

PokeLance targets Python 3.10+ and ships with full inline type hints, so your type checker (`ty`, `pyright`, `mypy`) picks up the API surface immediately after install.

## Requirements

- Python `>=3.10`
- [`niquests`](https://github.com/jawah/niquests) for modern sync and async HTTP (with HTTP/2 and HTTP/3 support)
- [`attrs`](https://www.attrs.org/) for structured models
- [`aiofiles`](https://github.com/Tinche/aiofiles) for non-blocking disk cache I/O

PokeLance keeps its runtime footprint minimal so it drops cleanly into bots, web services, and scripts.

## Install from PyPI

=== "uv"

    ```bash
    uv add pokelance
    ```

=== "pip"

    ```bash
    python -m pip install -U pokelance
    ```

=== "poetry"

    ```bash
    poetry add pokelance
    ```

## Installing from source

If you want the latest development version:

=== "uv"

    ```bash
    uv add git+https://github.com/FallenDeity/PokeLance.git
    ```

=== "pip"

    ```bash
    python -m pip install -U git+https://github.com/FallenDeity/PokeLance.git
    ```

=== "Local Development"

    ```bash
    git clone https://github.com/FallenDeity/PokeLance.git
    cd PokeLance
    uv sync --all-groups
    ```

## Verifying the install

Verify that PokeLance is installed properly by checking its version:

```python exec="true" source="above" result="text"
import pokelance

print(f"PokeLance version: {pokelance.__version__}")
```

If that outputs a version string, you're ready for the [Quickstart](quickstart.md).
