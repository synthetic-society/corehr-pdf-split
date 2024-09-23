# CoreHR Application Pack PDF Splitter

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A Python script to extract individual applications from a combined PDF file, such as for Oxford HR application packs.

## Requirements

- Python 3.7+
- PyPDF2
- click

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/synthetic-society/corehr-pdf-split.git
   cd corehr-pdf-split
   ```

2. Install dependencies with [pixi](https://latest.pixi.sh):
   ```
   pixi install
   ```

## Usage

Run the script from the command line:

```
pixi run python main.py --input-pdf <path_to_input_pdf> --output-dir <path_to_output_directory>
```

For example:

```
pixi run python main.py --input-pdf applicationspack.pdf --output-dir output
```

This will process the `applicationspack.pdf` file and save individual applications in the `output` directory. The output folder will be created if it does not exist yet. Each applicant's PDF is saved with a filename format: "LastName,FirstName [ApplicantID].pdf"

## License

This project is available under the [MIT License](LICENSE).

## Contributing

Contributions, issues, and feature requests are welcome.
