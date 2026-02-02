"""
Electron-based Live Overlay Launcher
Transparent overlay dengan TRUE transparency support di Windows
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def check_nodejs_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=False)
        if result.returncode == 0:
            version = result.stdout.strip()
            logging.info(f"✅ Node.js installed: {version}")
            return True
    except FileNotFoundError:
        pass
    
    logging.error("❌ Node.js not found!")
    logging.error("   Install Node.js from: https://nodejs.org/")
    return False

def check_electron_installed(overlay_dir):
    """Check if Electron is installed in overlay directory"""
    node_modules = overlay_dir / "node_modules"
    if node_modules.exists() and (node_modules / "electron").exists():
        logging.info("✅ Electron installed")
        return True
    else:
        logging.warning("⚠️  Electron not installed yet")
        return False

def install_electron(overlay_dir):
    """Install Electron via npm"""
    logging.info("📦 Installing Electron...")
    logging.info("   This may take a few minutes on first run...")
    
    try:
        result = subprocess.run(
            ['npm.cmd', 'install'],
            cwd=overlay_dir,
            check=False,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            logging.info("✅ Electron installed successfully!")
            return True
        else:
            logging.error(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Installation error: {e}")
        return False

def launch_overlay():
    """Launch Electron overlay"""
    try:
        # Get overlay directory path
        current_dir = Path(__file__).parent
        overlay_dir = current_dir / "overlay_electron"
        
        if not overlay_dir.exists():
            logging.error(f"❌ Overlay directory not found: {overlay_dir}")
            return False
        
        # Check Node.js
        if not check_nodejs_installed():
            return False
        
        # Check and install Electron if needed
        if not check_electron_installed(overlay_dir):
            logging.info("🔧 First time setup - installing Electron...")
            if not install_electron(overlay_dir):
                return False
        
        # Launch Electron
        logging.info("🚀 Starting Electron overlay...")
        logging.info("   • Window akan muncul dengan transparent background")
        logging.info("   • Tekan Ctrl+W untuk close")
        logging.info("   • Tekan Ctrl+Shift+I untuk DevTools")
        logging.info("")
        
        process = subprocess.Popen(
            ['npm.cmd', 'start'],
            cwd=overlay_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        logging.info("✅ Overlay started! (Electron)")
        logging.info("   Close this terminal to stop overlay")
        
        # Wait for process
        process.wait()
        
        return True
        
    except FileNotFoundError as e:
        logging.error(f"❌ Command not found: {e}")
        logging.error("   Make sure Node.js and npm are installed")
        return False
    except Exception as e:
        logging.error(f"❌ Error starting overlay: {e}")
        return False

if __name__ == "__main__":
    try:
        success = launch_overlay()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logging.info("\n⚠️  Overlay stopped by user")
        sys.exit(0)
