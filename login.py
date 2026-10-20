import os
import json
import hashlib
from os import path
import secrets
import getpass
import shutil
import re

USER_DIR = "users"
ACCOUNTS_FILE = "accounts.json"
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

class LoginManager:
    def __init__(self):
        os.makedirs(USER_DIR, exist_ok=True)
        self.current_user = None

    def _load_accounts(self):
        if not os.path.exists(ACCOUNTS_FILE):
            return {}

        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading account database: {e}")
            return {}
        
    def _save_accounts(self, accounts):
        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as file:
                json.dump(accounts, file, indent=4)
        except OSError as e:
            print(f"Error saving account database: {e}")

    def _hash_password(self, password, salt=None):
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), 200_000
        ).hex()
        return {"salt": salt, "hash": digest}

    def _validate_username(self, username: str) -> bool:
        return bool(USERNAME_PATTERN.match(username))

    def register_user(self):
        accounts = self._load_accounts()
        username = input("Create username: ").strip()

        if not username or any(c not in
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                for c in username):
            print("Use letters, numbers, underscores or hyphens.")
            return

        if username in accounts:
            print("Username already exists.")
            return

        password = getpass.getpass("Create password: ")
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            return

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            return

        # Save credentials
        accounts[username] = self._hash_password(password)
        self._save_accounts(accounts)
        
        # Create user directory for their personal files
        os.makedirs(os.path.join(USER_DIR, username), exist_ok=True)
        print(f"Account '{username}' created successfully!")

    def authenticate_user(self) -> bool:
        accounts = self._load_accounts()
        
        if not accounts:
            print("No accounts registered yet. Please register an account first.")
            return False

        username = input("Enter your username: ").strip()
        password = getpass.getpass("Enter your password: ")

        account = accounts.get(username)
        if not account:
            print("Access denied: Username not found.")
            return False

        candidate = self._hash_password(password, account["salt"])
        if secrets.compare_digest(candidate["hash"], account["hash"]):
            self.current_user = username
            print("Access granted!")
            return True

        print("Access denied: Incorrect password.")
        return False

    def create_user_file(self) -> None:
        if not self.current_user:
            print("Please log in first.")
            return 
        filename = input("Enter a file name (e.g. notes.txt): ").strip()

        if(
            not filename
            or filename in {".",". ."}
            or os.path.basename(filename) != filename
            or any(c in filename for c in '<>:"/\\|?*')
        ):
            print("Invalid file name.")
            return

        folder = os.path.join(USER_DIR, self.current_user)
        path - os.path.join(folder, filename)

        if os.path.exists(path):
            print("That file already exist.")
            return

        try:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            fd = os.open(path, flags=0o600)
            with open(fd, "w", encoding="utf-8") as file:
                file.write("")
            print(f"Create: {path}")
        except OSError as error:
            print(f"Could not create file: {error}")

    def delete_account(self) -> None:
        if not self.current_user:
            print("Please log in first.")
            return

        username = self.current_user
        confirm = input(
            f"Delete account '{username}' and all its filees? (yes/no): "
        ).strip().lower()

        if confirm != {"yes","y"}:
            print("Delete cancelled.")
            return

        account = self._load_account()
        account.pop(username, None)
        self._save_account(account)

        shutil.rmtree(os.path.join(USER_DIR, username), ignore_error = True)
        self.current_user = None
        print("Account and its files deleted.")

    def check_status(self) -> None:
        while True:
            status_str = f"Logged in as: {self.current_user}" if self.current_user else "Not logged in"
            print(f"\n--- Personal Finance Book [{status_str}] ---")
            
            if not self.current_user:
                print("1. Login to Account")
                print("2. Register New Account")
                print("5. Exit")
            else:
                print("3. Create Personal File")
                print("4. Delete Current Account")
                print("6. Logout")
                print("5. Exit")

            try:
                choice = int(input("Enter choice: "))
            except ValueError:
                print("Enter a valid number.")
                continue

            if choice == 1 and not self.current_user:
                self.authenticate_user()
            elif choice == 2 and not self.current_user:
                self.register_user()
            elif choice == 3 and self.current_user:
                self.create_user_file()
            elif choice == 4 and self.current_user:
                self.delete_account()
            elif choice == 6 and self.current_user:
                self.current_user = None
                print("Logged out successfully.")
            elif choice == 5:
                print("Exiting application...")
                break
            else:
                print("Invalid choice for current login state.")


if __name__ == "__main__":
    LoginManager().check_status()