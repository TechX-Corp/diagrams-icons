#!/usr/bin/env python3
"""
Render .docx, .xlsx, and .pptx files to PNG images for visual QA.

This script uses LibreOffice (soffice) to convert Office documents to PDF,
then uses pdf2image (poppler) to convert PDF pages to PNG images. Each page
is saved as a separate PNG file for visual inspection.

Usage:
    python scripts/render_docs.py output/proposal_REVIEW.docx
    python scripts/render_docs.py output/ --output-dir custom/renders --dpi 200
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None
    logging.warning("pdf2image not available. PDF to PNG conversion will be disabled.")


logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def check_soffice() -> Optional[str]:
    """
    Check if LibreOffice soffice is available.
    
    Returns:
        Path to soffice executable if found, None otherwise
    """
    soffice_path = shutil.which('soffice')
    if soffice_path is None:
        # Try common installation paths
        common_paths = [
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',  # macOS
            '/usr/bin/soffice',  # Linux
            'C:\\Program Files\\LibreOffice\\program\\soffice.exe',  # Windows
        ]
        for path in common_paths:
            if Path(path).exists():
                return path
    return soffice_path


def convert_to_pdf(
    input_file: Path,
    output_dir: Path,
    soffice_path: str
) -> Optional[Path]:
    """
    Convert Office document to PDF using LibreOffice.
    
    Args:
        input_file: Path to input .docx, .xlsx, or .pptx file
        output_dir: Directory to save the PDF
        soffice_path: Path to soffice executable
        
    Returns:
        Path to generated PDF file, or None if conversion failed
    """
    input_file = Path(input_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary directory for LibreOffice conversion
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Run soffice conversion
            cmd = [
                soffice_path,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_dir,
                str(input_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"soffice conversion failed for {input_file}: {result.stderr}")
                return None
            
            # Find the generated PDF (soffice names it based on input filename)
            pdf_filename = input_file.stem + '.pdf'
            temp_pdf = Path(temp_dir) / pdf_filename
            
            if not temp_pdf.exists():
                logger.error(f"PDF not generated: {temp_pdf}")
                return None
            
            # Move PDF to output directory
            output_pdf = output_dir / pdf_filename
            temp_pdf.rename(output_pdf)
            
            logger.info(f"Converted {input_file} to PDF: {output_pdf}")
            return output_pdf
            
        except subprocess.TimeoutExpired:
            logger.error(f"Conversion timeout for {input_file}")
            return None
        except Exception as e:
            logger.error(f"Error converting {input_file} to PDF: {e}")
            return None


def get_sheet_names(pdf_path: Path, soffice_path: str) -> List[str]:
    """
    Extract sheet names from Excel PDF (if possible).
    
    Note: LibreOffice PDFs don't always preserve sheet names in a way we can extract.
    This is a placeholder for future enhancement. For now, we'll use page numbers.
    
    Args:
        pdf_path: Path to PDF file
        soffice_path: Path to soffice executable (for potential future use)
        
    Returns:
        List of sheet names (or empty list if not available)
    """
    # TODO: Could potentially use pdftk or other tools to extract metadata
    # For now, return empty list and use page numbers
    return []


def pdf_to_png(
    pdf_path: Path,
    output_dir: Path,
    dpi: int = 150
) -> List[Dict[str, Any]]:
    """
    Convert PDF pages to PNG images.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save PNG images
        dpi: DPI for PNG output (default: 150)
        
    Returns:
        List of dictionaries containing page metadata
    """
    if convert_from_path is None:
        logger.error("pdf2image is not installed. Cannot convert PDF to PNG.")
        return []
    
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = []
    filename_stem = pdf_path.stem
    
    try:
        # Convert PDF pages to PIL Images
        images = convert_from_path(
            str(pdf_path),
            dpi=dpi,
            fmt='png'
        )
        
        # Save each page as PNG
        for page_num, image in enumerate(images, start=1):
            output_filename = f"{filename_stem}_page_{page_num}.png"
            output_path = output_dir / output_filename
            
            image.save(str(output_path), 'PNG')
            
            manifest.append({
                "page_num": page_num,
                "sheet_name_or_slide_num": str(page_num),  # Default to page number
                "png_path": str(output_path),
                "source_file": str(pdf_path)
            })
            
            logger.info(f"Rendered page {page_num}: {output_path}")
        
        return manifest
        
    except Exception as e:
        logger.error(f"Error converting PDF {pdf_path} to PNG: {e}")
        return []


def process_file(
    file_path: Path,
    output_dir: Path,
    dpi: int,
    soffice_path: str,
    keep_pdf: bool = False
) -> List[Dict[str, Any]]:
    """
    Process a single Office document file and render to PNG.
    
    Args:
        file_path: Path to .docx, .xlsx, or .pptx file
        output_dir: Directory to save PNG images
        dpi: DPI for PNG output
        soffice_path: Path to soffice executable
        keep_pdf: Whether to keep intermediate PDF files (default: False)
        
    Returns:
        List of dictionaries containing page metadata
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    suffix = file_path.suffix.lower()
    
    if suffix not in ['.docx', '.xlsx', '.pptx']:
        logger.warning(f"Unsupported file type: {suffix}. Skipping {file_path}")
        return []
    
    # Step 1: Convert to PDF
    pdf_output_dir = output_dir / 'pdfs' if keep_pdf else Path(tempfile.mkdtemp())
    pdf_path = convert_to_pdf(file_path, pdf_output_dir, soffice_path)
    
    if pdf_path is None:
        return []
    
    try:
        # Step 2: Convert PDF pages to PNG
        manifest = pdf_to_png(pdf_path, output_dir, dpi)
        
        # Update source_file in manifest to point to original Office file
        for item in manifest:
            item['source_file'] = str(file_path)
        
        return manifest
        
    finally:
        # Clean up PDF if not keeping it
        if not keep_pdf and pdf_path.exists():
            try:
                pdf_path.unlink()
                # Try to remove parent directory if empty
                pdf_dir = pdf_path.parent
                if pdf_dir.exists() and not any(pdf_dir.iterdir()):
                    pdf_dir.rmdir()
            except Exception as e:
                logger.warning(f"Could not clean up PDF {pdf_path}: {e}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Render .docx, .xlsx, and .pptx files to PNG images for visual QA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/render_docs.py output/proposal_REVIEW.docx
  python scripts/render_docs.py output/ --output-dir custom/renders --dpi 200
  python scripts/render_docs.py output/proposal_REVIEW.docx --dpi 300 --keep-pdf
        """
    )
    
    parser.add_argument(
        'input_path',
        type=str,
        help='Path to a .docx/.xlsx/.pptx file or directory containing such files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='tmp/renders',
        help='Output directory for PNG images (default: tmp/renders)'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='DPI for PNG output (default: 150)'
    )
    
    parser.add_argument(
        '--keep-pdf',
        action='store_true',
        help='Keep intermediate PDF files in output-dir/pdfs/'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    # Check for soffice
    soffice_path = check_soffice()
    if soffice_path is None:
        logger.error(
            "LibreOffice soffice not found. Please install LibreOffice:\n"
            "  macOS: brew install --cask libreoffice\n"
            "  Linux: sudo apt-get install libreoffice\n"
            "  Windows: Download from https://www.libreoffice.org/"
        )
        sys.exit(1)
    
    # Check for pdf2image
    if convert_from_path is None:
        logger.error(
            "pdf2image not installed. Please install it:\n"
            "  pip install pdf2image\n"
            "  Also install poppler:\n"
            "    macOS: brew install poppler\n"
            "    Linux: sudo apt-get install poppler-utils\n"
            "    Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases"
        )
        sys.exit(1)
    
    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)
    
    all_manifest = []
    
    # Process single file or directory
    if input_path.is_file():
        manifest = process_file(
            input_path,
            output_dir,
            args.dpi,
            soffice_path,
            args.keep_pdf
        )
        all_manifest.extend(manifest)
    elif input_path.is_dir():
        # Find all supported files in directory
        docx_files = list(input_path.glob('*.docx'))
        xlsx_files = list(input_path.glob('*.xlsx'))
        pptx_files = list(input_path.glob('*.pptx'))
        
        all_files = docx_files + xlsx_files + pptx_files
        
        if not all_files:
            logger.warning(f"No .docx, .xlsx, or .pptx files found in {input_path}")
        else:
            for file_path in all_files:
                manifest = process_file(
                    file_path,
                    output_dir,
                    args.dpi,
                    soffice_path,
                    args.keep_pdf
                )
                all_manifest.extend(manifest)
    else:
        logger.error(f"Input path is neither a file nor a directory: {input_path}")
        sys.exit(1)
    
    # Output JSON manifest to stdout
    print(json.dumps(all_manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
