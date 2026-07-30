# Installation

PokeLance targets Python 3.9+ and ships with full inline type hints (`py.typed`), so your
type checker picks up the API surface immediately after install, no stub packages
required.

## Requirements

- Python `>=3.9,<4`
- [`aiohttp`](https://docs.aiohttp.org/) `>=3.13.5` for the async HTTP layer
- [`attrs`](https://www.attrs.org/) `>=23.1.0,<24` for the (frozen, slotted) models
- [`aiofiles`](https://github.com/Tinche/aiofiles) `>=23.1.0,<24` for non-blocking disk cache I/O

These are the *only* runtime dependencies. PokeLance intentionally keeps its footprint
small so it drops cleanly into bots, web services, and scripts alike.

## Install from PyPI

=== "pip"

    ```bash
    python -m pip install -U pokelance
    ```

=== "uv"

    ```bash
    uv add pokelance
    ```

=== "poetry"

    ```bash
    poetry add pokelance
    ```

## Verifying the install

```python exec="true" source="above" result="text"
import subprocess

print(subprocess.run(["uv", "run", "python", "-c", "import pokelance; print(pokelance.__version__)"], capture_output=True, text=True).stdout.strip())
```

If that prints a version string, you're ready for the [Quickstart](quickstart.md).

## Installing from source

Useful if you want the bleeding-edge `master` branch or plan to contribute:

=== "Master/Pre-release"

    === "pip"

        ```bash
        python -m pip install -U git+https://github.com/FallenDeity/PokeLance.git
        ```

    === "uv"

        ```bash
        uv add git+https://github.com/FallenDeity/PokeLance.git
        ```

    === "poetry"

        ```bash
        poetry add git+https://github.com/FallenDeity/PokeLance.git
        ```

=== "Development"

    ```bash
    git clone https://github.com/FallenDeity/PokeLance.git
    cd PokeLance
    uv sync --all-groups
    ```
