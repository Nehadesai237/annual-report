#!/usr/bin/env python3
"""
Cross-platform Python script to create optimized ZIP file for client delivery.
This excludes large directories like node_modules, venv, __pycache__, etc.
Works on Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
import tempfile
import fnmatch

def should_exclude(path, root_dir):
    """
    Check if a path should be excluded from the ZIP.
    """
    # Convert to relative path
    try:
        rel_path = os.path.relpath(path, root_dir)
    except ValueError:
        return True
    
    # Normalize path separators
    rel_path = rel_path.replace('\\', '/')
    path_lower = rel_path.lower()
    
    # Exclude patterns
    exclude_patterns = [
        'node_modules',
        'venv',
        'env',
        '__pycache__',
        '.git',
        '.vscode',
        '.idea',
        'uploads',
        'reports',
        'build',
        'dist',
        '.pytest_cache',
        'htmlcov',
        '.coverage',
        '.DS_Store',
        'Thumbs.db',
        '*.pyc',
        '*.pyo',
        '*.log',
        '*.db',
        '*.sqlite',
        '*.egg-info',
        'ml/models/*.h5',
        'ml/models/*.pkl',
        'ml/models/*.joblib',
    ]
    
    # Check each pattern
    for pattern in exclude_patterns:
        # Simple filename match
        if fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
        
        # Path contains pattern
        if pattern in path_lower or pattern in rel_path:
            return True
        
        # Wildcard match
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path, f'**/{pattern}') or fnmatch.fnmatch(rel_path, f'{pattern}/**'):
            return True
    
    return False

def create_client_zip():
    """Create optimized ZIP file for client delivery."""
    print("Creating optimized ZIP file for client...\n")
    
    # Get project name and ZIP filename
    root_dir = Path.cwd()
    project_name = root_dir.name
    zip_filename = f"{project_name}-client.zip"
    
    # Remove old ZIP if exists
    if zip_filename in os.listdir('.'):
        print(f"Removing existing {zip_filename}...")
        os.remove(zip_filename)
    
    # Count files for progress
    total_files = 0
    excluded_files = 0
    
    print("Scanning files...")
    files_to_include = []
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), root_dir)]
        
        for file in files:
            file_path = os.path.join(root, file)
            total_files += 1
            
            if should_exclude(file_path, root_dir):
                excluded_files += 1
                continue
            
            files_to_include.append(file_path)
    
    print(f"Found {total_files} total files")
    print(f"Excluding {excluded_files} files (node_modules, venv, cache, etc.)")
    print(f"Including {len(files_to_include)} files\n")
    
    # Create ZIP file with no compression for maximum speed
    print(f"Creating {zip_filename} (no compression for speed)...")
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_STORED, compresslevel=0) as zipf:
            for file_path in files_to_include:
                # Get relative path for archive
                arcname = os.path.relpath(file_path, root_dir)
                
                # Normalize path separators to forward slashes (ZIP standard)
                arcname = arcname.replace('\\', '/')
                
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"Warning: Could not add {arcname}: {e}")
        
        # Get file size
        zip_size = os.path.getsize(zip_filename)
        size_mb = zip_size / (1024 * 1024)
        
        print(f"\n✅ ZIP file created successfully!")
        print(f"   File: {zip_filename}")
        print(f"   Size: {size_mb:.2f} MB ({zip_size:,} bytes)")
        print(f"\n✨ Done! Your client ZIP is ready.")
        
    except Exception as e:
        print(f"\n❌ Error creating ZIP file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        create_client_zip()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

