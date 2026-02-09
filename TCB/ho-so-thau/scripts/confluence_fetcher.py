#!/usr/bin/env python3
"""
Confluence Page Fetcher

Pre-fetch Confluence pages and their descendants to local HTML files for offline processing.
Supports both OAuth 2.0 (via Atlassian Rovo MCP session) and API token authentication.

Usage:
    python scripts/confluence_fetcher.py --url "https://site.atlassian.net/wiki/spaces/SPACE/pages/12345/Title"
    python scripts/confluence_fetcher.py --page-id 12345 --site yourcompany.atlassian.net
    python scripts/confluence_fetcher.py --url "..." --depth 1  # Only direct children
    python scripts/confluence_fetcher.py --url "..." --no-attachments  # Skip attachments
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("Error: 'requests' package not found. Install with: uv pip install requests")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: 'pyyaml' package not found. Install with: uv pip install pyyaml")
    sys.exit(1)


class ConfluenceFetcher:
    """Fetch Confluence pages via REST API v2."""

    def __init__(self, site: str, email: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize Confluence API client.
        
        Args:
            site: Atlassian site domain (e.g., "yourcompany.atlassian.net")
            email: User email (for API token auth)
            api_token: API token (for API token auth)
        """
        self.site = site
        self.base_url = f"https://{site}/wiki/api/v2"
        self.auth = HTTPBasicAuth(email, api_token) if email and api_token else None
        self.session = requests.Session()
        if self.auth:
            self.session.auth = self.auth

    def parse_confluence_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Extract page ID and space key from Confluence URL.
        
        Formats:
        - https://site.atlassian.net/wiki/spaces/SPACE/pages/12345/Title
        - https://site.atlassian.net/wiki/pages/12345
        
        Returns:
            {"page_id": "12345", "space_key": "SPACE"} or None if invalid
        """
        pattern = r'/pages/(\d+)'
        match = re.search(pattern, url)
        if not match:
            return None
        
        page_id = match.group(1)
        
        # Try to extract space key
        space_pattern = r'/spaces/([A-Z0-9]+)/'
        space_match = re.search(space_pattern, url)
        space_key = space_match.group(1) if space_match else None
        
        return {"page_id": page_id, "space_key": space_key}

    def get_page(self, page_id: str) -> Optional[Dict]:
        """
        Get page content by ID.
        
        Returns:
            Page data dict with id, title, body, version, etc.
        """
        url = f"{self.base_url}/pages/{page_id}"
        params = {
            "body-format": "storage",  # HTML format
            "include-labels": "true"
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_id}: {e}")
            return None

    def get_page_children(self, page_id: str) -> List[Dict]:
        """
        Get direct child pages (non-recursive).
        
        Returns:
            List of child page dicts with id, title, etc.
        """
        url = f"{self.base_url}/pages/{page_id}/children"
        params = {"limit": 250}  # Max per request
        
        children = []
        try:
            while url:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "results" in data:
                    children.extend(data["results"])
                
                # Check for next page
                url = data.get("_links", {}).get("next")
                if url:
                    url = f"https://{self.site}{url}"
                params = {}  # Next URL already has params
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching children for page {page_id}: {e}")
        
        return children

    def get_page_descendants_recursive(
        self, page_id: str, max_depth: Optional[int] = None, current_depth: int = 0
    ) -> List[Dict]:
        """
        Get all descendant pages recursively.
        
        Args:
            page_id: Parent page ID
            max_depth: Maximum depth to fetch (None = unlimited)
            current_depth: Current recursion depth (internal)
        
        Returns:
            List of all descendant page dicts with depth info
        """
        if max_depth is not None and current_depth >= max_depth:
            return []
        
        children = self.get_page_children(page_id)
        all_descendants = []
        
        for child in children:
            child["depth"] = current_depth + 1
            all_descendants.append(child)
            
            # Recursively fetch grandchildren
            grandchildren = self.get_page_descendants_recursive(
                child["id"], max_depth, current_depth + 1
            )
            all_descendants.extend(grandchildren)
        
        return all_descendants

    def get_page_attachments(self, page_id: str) -> List[Dict]:
        """Get all attachments for a page."""
        url = f"{self.base_url}/pages/{page_id}/attachments"
        params = {"limit": 250}
        
        attachments = []
        try:
            while url:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "results" in data:
                    attachments.extend(data["results"])
                
                url = data.get("_links", {}).get("next")
                if url:
                    url = f"https://{self.site}{url}"
                params = {}
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching attachments for page {page_id}: {e}")
        
        return attachments

    def download_attachment(self, attachment: Dict, output_dir: Path) -> Optional[str]:
        """
        Download an attachment file.
        
        Returns:
            Relative path to downloaded file or None if failed
        """
        download_url = attachment.get("_links", {}).get("download")
        if not download_url:
            return None
        
        # Make absolute URL
        if not download_url.startswith("http"):
            download_url = f"https://{self.site}{download_url}"
        
        filename = attachment.get("title", "attachment")
        file_path = output_dir / filename
        
        try:
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return filename
        except requests.exceptions.RequestException as e:
            print(f"Error downloading attachment {filename}: {e}")
            return None


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]  # Limit length


def load_config() -> Dict:
    """Load configuration from config.yaml if it exists."""
    config_path = Path("config.yaml")
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Confluence pages and descendants to local HTML files"
    )
    parser.add_argument(
        "--url",
        help="Confluence page URL (e.g., https://site.atlassian.net/wiki/spaces/SPACE/pages/12345/Title)"
    )
    parser.add_argument("--page-id", help="Page ID (alternative to --url)")
    parser.add_argument("--site", help="Atlassian site domain (e.g., yourcompany.atlassian.net)")
    parser.add_argument(
        "--depth",
        default="all",
        help="Depth to fetch: 0 (parent only), 1 (direct children), 'all' (recursive, default)"
    )
    parser.add_argument(
        "--output",
        default="input/confluence",
        help="Output directory (default: input/confluence)"
    )
    parser.add_argument(
        "--no-attachments",
        action="store_true",
        help="Skip downloading attachments"
    )
    parser.add_argument("--email", help="Confluence user email (for API token auth)")
    parser.add_argument("--api-token", help="Confluence API token")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load config for defaults
    config = load_config()
    confluence_config = config.get("confluence", {})
    
    # Determine site and page ID
    site = args.site or confluence_config.get("site")
    page_id = args.page_id
    
    if args.url:
        parsed = ConfluenceFetcher("dummy", None, None).parse_confluence_url(args.url)
        if not parsed:
            print(f"Error: Invalid Confluence URL: {args.url}")
            print("Expected format: https://site.atlassian.net/wiki/spaces/SPACE/pages/12345/Title")
            sys.exit(1)
        page_id = parsed["page_id"]
        
        # Extract site from URL if not provided
        if not site:
            parsed_url = urlparse(args.url)
            site = parsed_url.netloc
    
    if not site:
        print("Error: Site domain required. Provide via --site or --url")
        sys.exit(1)
    
    if not page_id:
        print("Error: Page ID required. Provide via --page-id or --url")
        sys.exit(1)
    
    # Parse depth
    max_depth = None if args.depth == "all" else int(args.depth)
    
    # Authentication
    email = args.email or confluence_config.get("email")
    api_token = args.api_token or confluence_config.get("api_token")
    
    if not (email and api_token):
        print("Warning: No API token provided. Requests will be unauthenticated.")
        print("For authenticated access:")
        print("  1. Add email and api_token to config.yaml, OR")
        print("  2. Pass --email and --api-token flags")
        print()
    
    # Initialize fetcher
    fetcher = ConfluenceFetcher(site, email, api_token)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    attachments_dir = output_dir / "attachments"
    if not args.no_attachments:
        attachments_dir.mkdir(exist_ok=True)
    
    print(f"Fetching page {page_id} from {site}...")
    
    # Fetch parent page
    parent_page = fetcher.get_page(page_id)
    if not parent_page:
        print(f"Error: Could not fetch page {page_id}")
        sys.exit(1)
    
    print(f"✓ Found: {parent_page.get('title', 'Untitled')}")
    
    # Fetch descendants
    if max_depth is None or max_depth > 0:
        print(f"Fetching descendants (depth: {args.depth})...")
        descendants = fetcher.get_page_descendants_recursive(page_id, max_depth)
        print(f"✓ Found {len(descendants)} descendant pages")
    else:
        descendants = []
    
    # Build page list
    all_pages = [parent_page] + descendants
    
    # Add depth to parent
    parent_page["depth"] = 0
    
    # Save pages and build manifest
    manifest = {
        "source_url": args.url or f"https://{site}/wiki/pages/{page_id}",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "page_count": len(all_pages),
        "pages": []
    }
    
    for page in all_pages:
        page_id_str = page["id"]
        title = page.get("title", "Untitled")
        slug = slugify(title)
        html_filename = f"{page_id_str}_{slug}.html"
        html_path = output_dir / html_filename
        
        # Extract HTML body
        body_storage = page.get("body", {}).get("storage", {}).get("value", "")
        
        # Save HTML
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"<!-- Confluence Page: {title} -->\n")
            f.write(f"<!-- Page ID: {page_id_str} -->\n")
            f.write(f"<!-- Fetched: {manifest['fetched_at']} -->\n\n")
            f.write(body_storage)
        
        if args.verbose:
            print(f"  Saved: {html_filename}")
        
        # Fetch attachments
        attachment_files = []
        if not args.no_attachments:
            attachments = fetcher.get_page_attachments(page_id_str)
            if attachments and args.verbose:
                print(f"    {len(attachments)} attachment(s)")
            
            for attachment in attachments:
                downloaded = fetcher.download_attachment(attachment, attachments_dir)
                if downloaded:
                    attachment_files.append(downloaded)
        
        # Add to manifest
        version = page.get("version", {})
        manifest["pages"].append({
            "id": page_id_str,
            "title": title,
            "parent_id": page.get("parentId"),
            "depth": page.get("depth", 0),
            "html_file": html_filename,
            "attachments": attachment_files,
            "last_modified": version.get("createdAt", ""),
            "author": version.get("authorId", "")
        })
    
    # Save manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(all_pages)} pages to {output_dir}/")
    print(f"✓ Manifest: {manifest_path}")
    if not args.no_attachments:
        total_attachments = sum(len(p["attachments"]) for p in manifest["pages"])
        if total_attachments > 0:
            print(f"✓ Downloaded {total_attachments} attachment(s) to {attachments_dir}/")


if __name__ == "__main__":
    main()
