# CoreHR Application Pack PDF Splitter

[![CI](https://github.com/synthetic-society/corehr-pdf-split/workflows/CI/badge.svg)](https://github.com/synthetic-society/corehr-pdf-split/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/corehr-pdf-split.svg)](https://badge.fury.io/py/corehr-pdf-split)

A Python package to extract individual applications from a combined PDF file, such as for Oxford HR application packs.


## Installation and Usage

### Option 1: Using uvx (Recommended)

If you have [uv](https://docs.astral.sh/uv/) installed, you can run the tool directly without installing it:

```bash
uvx corehr-pdf-split --input-pdf applicationspack.pdf --output-dir output
```

### Option 2: Install from PyPI

Install the package globally or in a virtual environment:

```bash
pip install corehr-pdf-split
```

Then run:

```bash
corehr-pdf-split --input-pdf applicationspack.pdf --output-dir output
```

### Option 3: Using uv (for development or local use)

```bash
uv tool install corehr-pdf-split
```

Then run:

```bash
corehr-pdf-split --input-pdf applicationspack.pdf --output-dir output
```

## How it works

The tool processes the input PDF file and saves individual applications in the specified output directory. The output folder will be created if it does not exist yet. Each applicant's PDF is saved with a filename format: `LastName,FirstName [ApplicantID].pdf`.

## Example

```bash
uvx corehr-pdf-split --input-pdf applicationspack.pdf --output-dir output
```

This will process the `applicationspack.pdf` file and save individual applications in the `output` directory.

## Development

If you want to contribute to or modify this project:

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for dependency management

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/synthetic-society/corehr-pdf-split.git
   cd corehr-pdf-split
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the tool in development mode:
   ```bash
   uv run corehr-pdf-split --input-pdf <path_to_input_pdf> --output-dir <path_to_output_directory>
   ```

### Building and Publishing

To build the package:

```bash
uv build
```

To publish to PyPI (maintainers only):

```bash
uv publish
```

## License

This project is available under the [MIT License](LICENSE).

## Contributing

Contributions, issues, and feature requests are welcome.
