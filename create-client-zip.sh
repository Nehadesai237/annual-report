#!/bin/bash
# Bash script to create optimized ZIP file for client delivery
# This excludes large directories like node_modules, venv, __pycache__, etc.

set -e

echo "Creating optimized ZIP file for client..."

# Get the current directory name
PROJECT_NAME=$(basename "$PWD")
ZIP_FILE="${PROJECT_NAME}-client.zip"
TEMP_DIR="temp-zip-$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)"

# Cleanup function
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        echo "Cleaned up temporary files."
    fi
}

trap cleanup EXIT

# Create temporary directory
mkdir -p "$TEMP_DIR"
echo "Created temporary directory: $TEMP_DIR"

# Directories and files to exclude (rsync patterns)
EXCLUDE_PATTERNS=(
    --exclude='node_modules'
    --exclude='venv'
    --exclude='env'
    --exclude='__pycache__'
    --exclude='*.pyc'
    --exclude='*.pyo'
    --exclude='build'
    --exclude='dist'
    --exclude='.git'
    --exclude='.vscode'
    --exclude='.idea'
    --exclude='uploads'
    --exclude='reports'
    --exclude='*.log'
    --exclude='.DS_Store'
    --exclude='Thumbs.db'
    --exclude='*.db'
    --exclude='*.sqlite*'
    --exclude='.pytest_cache'
    --exclude='htmlcov'
    --exclude='.coverage'
    --exclude='*.egg-info'
    --exclude='ml/models/*.h5'
    --exclude='ml/models/*.pkl'
    --exclude='ml/models/*.joblib'
    --exclude='frontend/build'
    --exclude="$TEMP_DIR"
    --exclude="$ZIP_FILE"
)

echo ""
echo "Copying files (excluding large directories)..."

# Copy files using rsync (if available) or find
if command -v rsync &> /dev/null; then
    rsync -a "${EXCLUDE_PATTERNS[@]}" ./ "$TEMP_DIR/"
else
    echo "rsync not found, using find (slower)..."
    find . -type f ! -path "*/node_modules/*" \
                  ! -path "*/venv/*" \
                  ! -path "*/env/*" \
                  ! -path "*/__pycache__/*" \
                  ! -path "*/.git/*" \
                  ! -path "*/uploads/*" \
                  ! -path "*/reports/*" \
                  ! -path "*/build/*" \
                  ! -path "*/.vscode/*" \
                  ! -path "*/.idea/*" \
                  ! -name "*.pyc" \
                  ! -name "*.pyo" \
                  ! -name "*.log" \
                  ! -name ".DS_Store" \
                  ! -name "Thumbs.db" \
                  ! -path "$TEMP_DIR/*" \
                  ! -name "$ZIP_FILE" \
        | while read -r file; do
            dest="$TEMP_DIR/${file#./}"
            mkdir -p "$(dirname "$dest")"
            cp "$file" "$dest"
        done
fi

echo "Files copied successfully!"
echo ""
echo "Creating ZIP file (stored/no compression for speed)..."

# Remove old ZIP if exists
[ -f "$ZIP_FILE" ] && rm "$ZIP_FILE"

# Create ZIP with stored method (no compression) for maximum speed
cd "$TEMP_DIR"
zip -r -q -0 "../$ZIP_FILE" . 2>/dev/null || zip -r -q -0 "../$ZIP_FILE" .
cd ..

# Get file size
if [[ "$OSTYPE" == "darwin"* ]]; then
    SIZE=$(du -h "$ZIP_FILE" | cut -f1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    SIZE=$(du -h "$ZIP_FILE" | cut -f1)
else
    SIZE=$(stat -f%z "$ZIP_FILE" 2>/dev/null || stat -c%s "$ZIP_FILE")
fi

echo ""
echo "✅ ZIP file created successfully!"
echo "   File: $ZIP_FILE"
echo "   Size: $SIZE"
echo ""
echo "✨ Done! Your client ZIP is ready."

