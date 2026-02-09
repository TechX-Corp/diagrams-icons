#!/usr/bin/env python3
"""
Extract images from .docx and .pdf files.

This script extracts images from Word documents (.docx) and PDF files (.pdf),
saves them to a specified output directory, and outputs a JSON manifest
containing metadata about each extracted image.

Usage:
    python scripts/extract_images.py input/file.docx
    python scripts/extract_images.py input/file.pdf
    python scripts/extract_images.py input/ --output-dir custom/path
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import parse_xml
except ImportError:
    Document = None
    logging.warning("python-docx not available. .docx extraction will be disabled.")

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logging.warning("pymupdf not available. .pdf extraction will be disabled.")


logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def extract_docx_images(docx_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
    """
    Extract images from a .docx file.
    
    Args:
        docx_path: Path to the .docx file
        output_dir: Directory to save extracted images
        
    Returns:
        List of dictionaries containing image metadata
    """
    if Document is None:
        logger.error("python-docx is not installed. Cannot extract from .docx files.")
        return []
    
    manifest = []
    docx_path = Path(docx_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        doc = Document(str(docx_path))
        filename_stem = docx_path.stem
        
        # Track image counter
        img_counter = 0
        
        # Extract images from inline shapes
        for i, inline_shape in enumerate(doc.inline_shapes):
            try:
                if inline_shape.type == 3:  # Type 3 is picture
                    img_counter += 1
                    
                    # Get image data from related parts
                    rId = inline_shape._inline.graphic.graphicData.pic.nvPicPr.cNvPr.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                    if rId:
                        image_part = doc.part.related_parts[rId]
                        image_data = image_part.blob
                        
                        # Get dimensions
                        width = inline_shape.width
                        height = inline_shape.height
                        
                        # Generate output filename
                        output_filename = f"docx_{filename_stem}_img_{img_counter}.png"
                        output_path = output_dir / output_filename
                        
                        # Save image
                        output_path.write_bytes(image_data)
                        
                        # Get alt text if available
                        alt_text = ""
                        try:
                            cNvPr = inline_shape._inline.graphic.graphicData.pic.nvPicPr.cNvPr
                            alt_text = cNvPr.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}title', '')
                        except Exception:
                            pass
                        
                        manifest.append({
                            "path": str(output_path),
                            "source_file": str(docx_path),
                            "location": f"inline_shape_{i}",
                            "alt_text": alt_text,
                            "width": width,
                            "height": height
                        })
                        
            except Exception as e:
                logger.warning(f"Skipping corrupt image {i} in {docx_path}: {e}")
                continue
        
        # Also check for images in related parts (headers, footers, etc.)
        for rId, part in doc.part.related_parts.items():
            try:
                if part.content_type.startswith('image/'):
                    img_counter += 1
                    image_data = part.blob
                    
                    # Try to get dimensions from image data
                    try:
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(image_data))
                        width, height = img.size
                    except Exception:
                        width = None
                        height = None
                    
                    # Generate output filename
                    output_filename = f"docx_{filename_stem}_img_{img_counter}.png"
                    output_path = output_dir / output_filename
                    
                    # Save image
                    output_path.write_bytes(image_data)
                    
                    manifest.append({
                        "path": str(output_path),
                        "source_file": str(docx_path),
                        "location": f"related_part_{rId}",
                        "alt_text": "",
                        "width": width,
                        "height": height
                    })
            except Exception as e:
                logger.warning(f"Skipping related part {rId} in {docx_path}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error processing {docx_path}: {e}")
        return []
    
    return manifest


def extract_pdf_images(pdf_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
    """
    Extract images from a .pdf file.
    
    Args:
        pdf_path: Path to the .pdf file
        output_dir: Directory to save extracted images
        
    Returns:
        List of dictionaries containing image metadata
    """
    if fitz is None:
        logger.error("pymupdf is not installed. Cannot extract from .pdf files.")
        return []
    
    manifest = []
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        doc = fitz.open(str(pdf_path))
        filename_stem = pdf_path.stem
        
        # Iterate through pages
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                image_list = page.get_images()
                
                # Extract each image on this page
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_data = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Get image dimensions
                        width = base_image.get("width")
                        height = base_image.get("height")
                        
                        # Generate output filename
                        output_filename = f"pdf_{filename_stem}_page{page_num + 1}_img_{img_index + 1}.png"
                        output_path = output_dir / output_filename
                        
                        # Save image (convert to PNG if needed)
                        if image_ext.lower() != 'png':
                            try:
                                from PIL import Image
                                import io
                                img_pil = Image.open(io.BytesIO(image_data))
                                img_pil.save(str(output_path), 'PNG')
                            except Exception:
                                # Fallback: save as-is
                                output_path.write_bytes(image_data)
                        else:
                            output_path.write_bytes(image_data)
                        
                        manifest.append({
                            "path": str(output_path),
                            "source_file": str(pdf_path),
                            "location": f"page_{page_num + 1}_image_{img_index + 1}",
                            "alt_text": "",
                            "width": width,
                            "height": height
                        })
                        
                    except Exception as e:
                        logger.warning(f"Skipping image {img_index} on page {page_num + 1} in {pdf_path}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error processing page {page_num + 1} in {pdf_path}: {e}")
                continue
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
        return []
    
    return manifest


def process_file(file_path: Path, output_dir: Path) -> List[Dict[str, Any]]:
    """
    Process a single file and extract images.
    
    Args:
        file_path: Path to the file to process
        output_dir: Directory to save extracted images
        
    Returns:
        List of dictionaries containing image metadata
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    suffix = file_path.suffix.lower()
    
    if suffix == '.docx':
        return extract_docx_images(file_path, output_dir)
    elif suffix == '.pdf':
        return extract_pdf_images(file_path, output_dir)
    else:
        logger.warning(f"Unsupported file type: {suffix}. Skipping {file_path}")
        return []


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Extract images from .docx and .pdf files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/extract_images.py input/file.docx
  python scripts/extract_images.py input/file.pdf
  python scripts/extract_images.py input/ --output-dir custom/path
        """
    )
    
    parser.add_argument(
        'input_path',
        type=str,
        help='Path to a .docx/.pdf file or directory containing such files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='tmp/images',
        help='Output directory for extracted images (default: tmp/images)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)
    
    all_manifest = []
    
    # Process single file or directory
    if input_path.is_file():
        manifest = process_file(input_path, output_dir)
        all_manifest.extend(manifest)
    elif input_path.is_dir():
        # Find all .docx and .pdf files in directory
        docx_files = list(input_path.glob('*.docx'))
        pdf_files = list(input_path.glob('*.pdf'))
        
        for file_path in docx_files + pdf_files:
            manifest = process_file(file_path, output_dir)
            all_manifest.extend(manifest)
    else:
        logger.error(f"Input path is neither a file nor a directory: {input_path}")
        sys.exit(1)
    
    # Output JSON manifest to stdout
    print(json.dumps(all_manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
