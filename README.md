This is a fork of image_to_web, I figured out the changes I wanted to make to it changed the focus too much.

# Web Media Optimizer

A Python script that converts image files (JPG, JPEG, PNG, GIF) to WebP format and video files (MP4, AVI, MOV, MKV) to WebM format. It supports both batch and recursive directory processing, with options to delete original files after a successful conversion and to preserve file metadata.

## Features

- Converts JPG, PNG, and GIF images to WebP format.
- Converts MP4, AVI, MOV, MKV to WebM format.
- Supports animated GIF to WebP conversion using `ffmpeg`.
- Recursive directory processing for batch conversions.
- Includes optional flags to convert only images, only videos, or specific file formats.
- Option to delete original files after successful conversion.
- Preserves file metadata (timestamps) during conversion.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/danelsanchez/web_media_optimizer.git
   cd web_media_optimizer
   ```

2. Install dependencies:
   ```bash
   pip install .
   ```

3. Ensure `ffmpeg` is installed for GIF conversion:
   - On Ubuntu/Debian/Linux Mint:
     ```bash
     sudo apt install ffmpeg
     ```
   - On Arch Linux
     ```bash
     sudo pacman -S ffmpeg
     ```
   - On Fedora
     ```bash
     sudo dnf install ffmpeg
     ```

## Usage

Run the script from the command line:

```bash
python -m web_media_optimizer /path/to/images [options]
```

### Options

- `-o`, `--output_dir`: Set a different output directory.
- `-r`, `--recursive`: Process directories recursively.
- `-d`, `--delete`: Delete original files after successful conversion.
- `-i`, `--images`: Convert only images.
- `-v`, `--videos`: Convert only videos.
- `-f`, `--formats`: Convert only specified formats (e.g., jpg png mp4).

### Example

Convert all images in a directory (non-recursive):
```bash
python -m web_media_optimizer /path/to/images
```

Convert all images recursively and delete originals:
```bash
python -m web_media_optimizer /path/to/images -r -d
```

## License

This project is licensed under the **GNU General Public License v2 (GPL-2.0)**. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.