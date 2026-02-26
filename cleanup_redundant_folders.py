"""
Cleanup Redundant Folders
Based on analysis, these folders are redundant/old versions
"""
import shutil
from pathlib import Path
import os

# Folders to DELETE (redundant/old versions)
REDUNDANT_FOLDERS = [
    # Old/duplicate app versions (we have BridgeCanvas as the winner)
    "BridgeDraw",           # React version - we're using Streamlit
    "BridgeGAD-00",         # Old version
    "BridgeGADdrafter",     # Another old version
    
    # Archive folders (old documentation)
    "docs_archive",         # Old docs - no longer needed
    
    # Cache folders (can be regenerated)
    ".pytest_cache",        # Test cache
]

# Folders to KEEP (essential)
KEEP_FOLDERS = [
    ".git",                 # Version control - CRITICAL
    ".github",              # GitHub config - CRITICAL
    ".kiro",                # Kiro config - CRITICAL
    "BridgeCanvas",         # WINNER - the working version
    "src",                  # Core source code - CRITICAL
    "docs",                 # Current documentation
    "inputs",               # Sample input files
    "outputs",              # Generated outputs
]

def get_folder_size(folder_path):
    """Calculate folder size in MB"""
    total = 0
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_folder_size(entry.path)
    except PermissionError:
        pass
    return total / (1024 * 1024)  # Convert to MB

def analyze_folders():
    """Analyze all folders"""
    print("=" * 70)
    print("FOLDER ANALYSIS")
    print("=" * 70)
    print()
    
    total_redundant_size = 0
    
    print("REDUNDANT FOLDERS (will be deleted):")
    for folder in REDUNDANT_FOLDERS:
        path = Path(folder)
        if path.exists():
            size = get_folder_size(str(path))
            total_redundant_size += size
            print(f"  ❌ {folder:30s} {size:8.1f} MB")
        else:
            print(f"  ⏭️  {folder:30s} (not found)")
    
    print()
    print(f"Total redundant space: {total_redundant_size:.1f} MB")
    print()
    
    print("FOLDERS TO KEEP:")
    for folder in KEEP_FOLDERS:
        path = Path(folder)
        if path.exists():
            size = get_folder_size(str(path))
            print(f"  ✅ {folder:30s} {size:8.1f} MB")
    
    print()
    print("=" * 70)
    return total_redundant_size

def cleanup(dry_run=True):
    """Delete redundant folders"""
    total_size = analyze_folders()
    
    if dry_run:
        print()
        print("🔍 DRY RUN MODE - No files will be deleted")
        print()
        print("To actually delete, run:")
        print("  python cleanup_redundant_folders.py --execute")
        return
    
    print()
    print("⚠️  DELETING REDUNDANT FOLDERS...")
    print()
    
    deleted_count = 0
    deleted_size = 0
    
    for folder in REDUNDANT_FOLDERS:
        path = Path(folder)
        if path.exists():
            try:
                size = get_folder_size(str(path))
                shutil.rmtree(path)
                print(f"✅ Deleted: {folder} ({size:.1f} MB)")
                deleted_count += 1
                deleted_size += size
            except Exception as e:
                print(f"❌ Failed to delete {folder}: {e}")
        else:
            print(f"⏭️  Skipped: {folder} (not found)")
    
    print()
    print("=" * 70)
    print("🎉 CLEANUP COMPLETE!")
    print("=" * 70)
    print(f"Deleted: {deleted_count} folders")
    print(f"Freed: {deleted_size:.1f} MB")
    print()
    print("Remaining folders:")
    for folder in KEEP_FOLDERS:
        if Path(folder).exists():
            print(f"  ✅ {folder}")
    print()
    print("Your repo is now LEAN and CLEAN! 🚀")

if __name__ == "__main__":
    import sys
    
    if "--execute" in sys.argv:
        response = input("⚠️  This will DELETE folders permanently. Continue? (yes/no): ")
        if response.lower() == "yes":
            cleanup(dry_run=False)
        else:
            print("❌ Cancelled")
    else:
        cleanup(dry_run=True)
