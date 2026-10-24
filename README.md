# ContextIQ

ContextIQ is a Python project designed to help extract, organize, and prepare document context from PDF and DOCX files for downstream analysis, indexing, or AI-driven workflows.

This repository is currently a lightweight foundation for the project and includes the Python project configuration and the dependencies needed to work with documents.

## Features

- PDF document parsing with PyMuPDF
- DOCX document handling with python-docx
- Clean project setup for Python 3.13
- Simple dependency management with uv
- Ready for extension into extraction, chunking, indexing, or search workflows

## Project status

This project is in an early stage. The repository currently contains the base configuration and package metadata, and it is prepared for implementing document-processing functionality.

## Requirements

- Python 3.13
- uv (recommended for dependency management)

## Installation

Clone the repository and install the dependencies:

```bash
cd projeto3
uv sync
```

If you prefer to use the virtual environment directly:

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Usage

The current project scaffold is ready to be extended with your document-processing logic. A typical workflow might look like this:

```python
from pathlib import Path

# Example placeholder for future PDF/DOCX processing logic
pdf_path = Path("documents/example.pdf")
docx_path = Path("documents/example.docx")
```

## Project structure

```text
projeto3/
├── .venv/              # Local virtual environment
├── .gitignore
├── .python-version
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock             # Lock file for reproducible installs
├── README.md           # Project documentation
└── src/                # To be added for application code
```

## Development

To run tests (when implemented):

```bash
pytest
```

To add new dependencies:

```bash
uv add <package-name>
```

## Dependencies

The current dependencies are:

- pymupdf
- python-docx
- pytest (development only)

## License

This project does not currently declare a license. Add one if you plan to distribute it publicly.

## Contributing

Contributions are welcome. If you want to help build the project, open an issue or submit a pull request with your proposed changes.
