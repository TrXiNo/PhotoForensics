# Photo Forensics Tool

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A Python-based command line tool for digital photo forensic analysis.

## Features

- File information
- Camera information
- EXIF metadata
- SHA256 hash
- GPS information
- Google Maps link
- Error Level Analysis (ELA)
- HEIC Support

## Installation

```bash
git clone https://github.com/USERNAME/PhotoForensics.git

cd PhotoForensics

pip install -r requirements.txt
```

## Usage

```bash
python photo_forensics.py image.jpg
```

or

```bash
python photo_forensics.py "C:\Photos\image.heic"
```

## Example

```
PHOTO FORENSICS TOOL

Camera : Canon EOS R50
Resolution : 6000x4000
SHA256 : ...
```

## Requirements

- Python 3.11+
- Pillow
- Rich
- pillow-heif

## License

MIT
