"""Create a safe local .env file for Windows development."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent
env_file = root / ".env"

if env_file.exists():
    print("Existing .env found. It was not changed.")
else:
    setup_key = secrets.token_urlsafe(48)
    env_file.write_text(
        "APP_ENV=development\n"
        "COOKIE_SECURE=false\n"
        f"ADMIN_SETUP_KEY={setup_key}\n",
        encoding="utf-8",
    )
    print("\nA local .env file was created.")
    print("ONE-TIME OWNER SETUP KEY (keep it private):")
    print(setup_key)
    print("\nEnter this key once on the first setup screen.")
    print("After creating your owner login, delete ADMIN_SETUP_KEY from .env and restart.")
