import os
import sys
import argparse
import logging
import subprocess
import shutil
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_output_directory(output_dir):
    """
    Creates the output directory if it does not exist.

    Args:
        output_dir (str): The path to the output directory.

    Returns:
        str: The path to the output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    return output_dir

def copy_file_metadata(input_path, output_path):
    """
    Copies file metadata (timestamps) from the input file to the output file.

    Args:
        input_path (str): The path to the input file.
        output_path (str): The path to the output file.
    """
    try:
        stat_info = os.stat(input_path)
        os.utime(output_path, (stat_info.st_atime, stat_info.st_mtime))
    except Exception as e:
        logging.error(f"Error copying metadata from {input_path} to {output_path}: {e}")

def convert_image_to_webp(input_path, output_path):
    """
    Converts an image to WebP format.

    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path to the output WebP file.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        with Image.open(input_path) as img:
            img.save(output_path, format="WEBP", quality=85)
        logging.info(f"Successfully converted: {input_path} → {output_path}")
        copy_file_metadata(input_path, output_path)
        return True
    except Exception as e:
        logging.error(f"Error converting {input_path}: {e}")
        return False

def convert_gif_to_webp(input_path, output_path):
    """
    Converts an animated GIF to WebP format using ffmpeg.

    Args:
        input_path (str): The path to the input GIF file.
        output_path (str): The path to the output WebP file.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        which_ffmpeg = shutil.which("ffmpeg")
        if not which_ffmpeg:
            raise FileNotFoundError("ffmpeg not found. Please install ffmpeg.")

        command = [
            "ffmpeg",
            "-i", input_path,
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libwebp",
            "-lossless", "0",  # Lossy compression
            "-compression_level", "6",  # Compression level (0-6)
            "-q:v", "75",  # Quality (0-100)
            "-loop", "0",  # Infinite loop
            "-vsync", "0", # Prevents frame drops or duplicates
            output_path
        ]

        subprocess.run(command, check=True)

        logging.info(f"Successfully converted: {input_path} → {output_path}")
        copy_file_metadata(input_path, output_path)
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_path}: {e}")
        return False
    except FileNotFoundError:
         logging.error(f"ffmpeg not found. Please install ffmpeg.")
         return False

def convert_video_to_webm(input_path, output_path):
    """
    Converts a video to WebM format using ffmpeg.

    Args:
        input_path (str): The path to the input video file.
        output_path (str): The path to the output WebM file.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        command = [
            "ffmpeg", "-loglevel", "error", "-y", "-i", input_path,
            "-c:v", "libvpx-vp9", "-b:v", "1M",  # Video codec and bitrate
            "-c:a", "libvorbis", "-b:a", "128k", # Audio codec and bitrate
            output_path
        ]
        subprocess.run(command, check=True)
        logging.info(f"Successfully converted: {input_path} → {output_path}")
        copy_file_metadata(input_path, output_path)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_path}: {e}")
        return False

def process_file(input_path, output_path, delete_after_conversion):
    """
    Processes a single file based on its extension.

    Args:
        input_path (str): The path to the input file.
        output_path (str): The path to the output file.
        delete_after_conversion (bool): Whether to delete the original file after conversion.
    """
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".gif":
        converted = convert_gif_to_webp(input_path, output_path)
    elif ext in {".mp4", ".flv", ".avi", ".mov", ".mkv"}:
        converted = convert_video_to_webm(input_path, output_path)
    else:
        converted = convert_image_to_webp(input_path, output_path)

    if converted and delete_after_conversion:
        os.remove(input_path)
        logging.info(f"Deleted original file: {input_path}")

def process_files(input_dir, output_dir, delete_after_conversion, convert_images, convert_videos, formats):
    """
    Processes all files in the input directory based on the specified criteria.

    Args:
        input_dir (str): The path to the input directory.
        output_dir (str): The path to the output directory.
        delete_after_conversion (bool): Whether to delete the original files after conversion.
        convert_images (bool): Whether to convert only images.
        convert_videos (bool): Whether to convert only videos.
        formats (list): List of specific formats to convert.
    """
    supported_formats = {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".flv", ".avi", ".mov", ".mkv"} # Add the dot (.)

    if formats:  # If specific formats are provided
        supported_formats = {fmt.lower() for fmt in formats if fmt.lower() in supported_formats}
    elif not convert_images and not convert_videos:  # If no conversion type or formats are specified, convert all
        pass  # Keep the default supported formats
    elif convert_images:
        supported_formats = supported_formats.intersection({".jpg", ".jpeg", ".png", ".gif"})
    elif convert_videos:
        supported_formats = supported_formats.intersection({".mp4", ".avi", ".mov", ".mkv", ".flv"})

    has_supported_files = any(
        os.path.splitext(file)[1].lower() in supported_formats
        for file in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, file))
    )
    if not has_supported_files:
        logging.info("No supported files found.")
        return

    with ThreadPoolExecutor() as executor:
        futures = []
        for file_name in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file_name)
            ext = os.path.splitext(file_name)[1].lower()
            if ext in supported_formats:
                output_file = os.path.join(output_dir, os.path.splitext(file_name)[0] + (".webm" if ext in {".mp4", ".flv",".avi", ".mov", ".mkv"} else ".webp"))
                if not os.path.exists(output_file):
                    futures.append(executor.submit(process_file, file_path, output_file, delete_after_conversion))

        for future in futures:
            future.result()

def main():
    """
    Main function to parse arguments and process files.
    """
    parser = argparse.ArgumentParser(description="Convert images and videos.")
    parser.add_argument("input_dir", type=str, help="Input directory.")
    parser.add_argument("-o", "--output_dir", type=str, help="Output directory.", default=None)
    parser.add_argument("-d", "--delete", action="store_true", help="Delete originals after conversion.")
    parser.add_argument("-i", "--images", action="store_true", help="Convert only images.")
    parser.add_argument("-v", "--videos", action="store_true", help="Convert only videos.")
    parser.add_argument("-f", "--formats", nargs="*", help="Convert only specified formats (e.g., jpg png mp4).")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        logging.error(f"The specified input path is not a valid directory: {args.input_dir}")
        sys.exit(1)

    output_dir = args.input_dir if args.output_dir is None else args.output_dir
    if output_dir:
        create_output_directory(output_dir)

    try:
        process_files(args.input_dir, output_dir, args.delete, args.images, args.videos, args.formats)
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
