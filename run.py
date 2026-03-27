"""
Quick start script to run the chatbot server
"""
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Check for .env file
env_file = project_root / '.env'
if not env_file.exists():
    print("❌ Error: .env file not found!")
    print("📝 Please copy .env.example to .env and configure it:")
    print("   cp .env.example .env")
    sys.exit(1)

# Import settings and run uvicorn
try:
    from config import settings

    print("Starting Bizwy Chatbot AI Server...")
    print(f"Server: http://{settings.app_host}:{settings.app_port}")
    print(f"Environment: {settings.app_env}")
    print("Session Store: in-memory")
    print(f"AI Model: {settings.openai_model}")
    print("-" * 60)

    cmd = [
        sys.executable,
        "app.py",
    ]

    subprocess.run(cmd, check=True)

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📦 Please install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"❌ Server exited with code: {e.returncode}")
    sys.exit(e.returncode)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
