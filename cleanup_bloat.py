"""
Cleanup Script: Remove bloat from root app
Following BridgeCanvas lessons: Keep only what's essential
"""
import os
import shutil
from pathlib import Path

# Files to DELETE (bloat)
DELETE_FILES = [
    # AI/ML features (premature)
    "src/bridge_gad/ai_optimizer.py",
    
    # API layer (not needed for Streamlit)
    "src/bridge_gad/api.py",
    
    # Bill generation (separate app)
    "src/bridge_gad/bill_generator.py",
    
    # CLI (use Streamlit instead)
    "src/bridge_gad/cli.py",
    
    # Auto-updater (premature)
    "src/bridge_gad/core_updater.py",
    "src/bridge_gad/updater.py",
    
    # GUI (use Streamlit)
    "src/bridge_gad/gui.py",
    
    # Experimental features
    "src/bridge_gad/living_gad.py",
    "src/bridge_gad/mesh_builder.py",
    
    # Plugin system (unused)
    "src/bridge_gad/plugin_generator.py",
    "src/bridge_gad/plugin_installer.py",
    "src/bridge_gad/plugin_manifest.json",
    "src/bridge_gad/plugin_registry.py",
    "src/bridge_gad/plugin_runner.py",
    
    # Telemetry (why?)
    "src/bridge_gad/telemetry.py",
    
    # Duplicate loggers
    "src/bridge_gad/logger_config.py",
    
    # Enhanced versions (keep simple ones)
    "src/bridge_gad/enhanced_io_utils.py",
    "src/bridge_gad/enhanced_lisp_functions.py",
    
    # LISP mirror (not needed)
    "src/bridge_gad/lisp_mirror.py",
    
    # Multi-sheet (overkill)
    "src/bridge_gad/multi_sheet_generator.py",
    
    # Ultimate exporter (too complex)
    "src/bridge_gad/ultimate_exporter.py",
    
    # Advanced features (premature)
    "src/bridge_gad/advanced_features.py",
]

# Folders to DELETE
DELETE_FOLDERS = [
    "src/bridge_gad/plugins",
]

# Files to KEEP (essential)
KEEP_FILES = [
    "src/bridge_gad/__init__.py",
    "src/bridge_gad/__main__.py",
    "src/bridge_gad/bridge_generator.py",  # Core
    "src/bridge_gad/bridge_types.py",
    "src/bridge_gad/config.py",
    "src/bridge_gad/core.py",
    "src/bridge_gad/drawing_generator.py",
    "src/bridge_gad/drawing.py",
    "src/bridge_gad/geometry.py",
    "src/bridge_gad/io_utils.py",  # Simple version
    "src/bridge_gad/logger.py",  # Simple version
    "src/bridge_gad/optimize.py",
    "src/bridge_gad/output_formats.py",
    "src/bridge_gad/parameters.py",
    "src/bridge_gad/templates.py",
    "src/bridge_gad/py.typed",
]

def cleanup():
    """Remove bloat files"""
    print("🧹 Starting cleanup...")
    print(f"📊 Target: Remove {len(DELETE_FILES)} files + {len(DELETE_FOLDERS)} folders")
    print()
    
    deleted_count = 0
    kept_count = 0
    
    # Delete files
    for file_path in DELETE_FILES:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
                print(f"✅ Deleted: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
        else:
            print(f"⏭️  Not found: {file_path}")
    
    # Delete folders
    for folder_path in DELETE_FOLDERS:
        path = Path(folder_path)
        if path.exists():
            try:
                shutil.rmtree(path)
                print(f"✅ Deleted folder: {folder_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {folder_path}: {e}")
        else:
            print(f"⏭️  Not found: {folder_path}")
    
    # Count kept files
    for file_path in KEEP_FILES:
        if Path(file_path).exists():
            kept_count += 1
    
    print()
    print("=" * 60)
    print(f"🎉 Cleanup complete!")
    print(f"📊 Deleted: {deleted_count} items")
    print(f"📊 Kept: {kept_count} essential files")
    print(f"📊 Reduction: {deleted_count / (deleted_count + kept_count) * 100:.1f}%")
    print()
    print("Next steps:")
    print("1. Test with: streamlit run app_lean.py")
    print("2. Use requirements_lean.txt (13 deps instead of 54)")
    print("3. Archive old files if needed")

def dry_run():
    """Show what would be deleted without actually deleting"""
    print("🔍 DRY RUN - No files will be deleted")
    print()
    
    print("Would DELETE:")
    for file_path in DELETE_FILES:
        exists = "✓" if Path(file_path).exists() else "✗"
        print(f"  [{exists}] {file_path}")
    
    for folder_path in DELETE_FOLDERS:
        exists = "✓" if Path(folder_path).exists() else "✗"
        print(f"  [{exists}] {folder_path}/")
    
    print()
    print("Would KEEP:")
    for file_path in KEEP_FILES:
        exists = "✓" if Path(file_path).exists() else "✗"
        print(f"  [{exists}] {file_path}")
    
    print()
    print("Run with --execute to actually delete files")

if __name__ == "__main__":
    import sys
    
    if "--execute" in sys.argv:
        response = input("⚠️  This will DELETE files. Continue? (yes/no): ")
        if response.lower() == "yes":
            cleanup()
        else:
            print("❌ Cancelled")
    else:
        dry_run()
