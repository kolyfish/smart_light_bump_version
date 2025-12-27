import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

# Define separator based on OS (though this script is for Mac)
sep = ":" 

# Run PyInstaller
PyInstaller.__main__.run([
    'app.py',
    '--name=MarketTradeAlertLight',
    '--onefile',
    '--console',  # Keep console to show QR code and logs
    f'--add-data=templates{sep}templates', # Add templates folder
    # '--icon=docs/icon.icns', # If we had an icon
    '--clean',
])

print("\n✅ Build complete. Check the 'dist' folder.")
print("To run: ./dist/MarketTradeAlertLight")
