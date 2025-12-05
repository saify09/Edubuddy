import sqlite3
import hashlib
import os
from typing import Optional, Dict, Any, List

class UserManager:
    _db_initialized = False

    def __init__(self, db_path: str = "edubuddy_users.db"):
        self.db_path = db_path
        if not UserManager._db_initialized:
            self._init_db()
            UserManager._db_initialized = True

    def _init_db(self):
        """Initialize the users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                father_name TEXT,
                roll_no TEXT,
                address TEXT,
                email TEXT,
                education TEXT,
                profile_pic_path TEXT,
                gender TEXT,
                contact_info TEXT
            )
        ''')
        conn.commit()
        conn.close()
        self._migrate_db()

    def _migrate_db(self):
        """Check for missing columns and add them if necessary."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        c = conn.cursor()
        try:
            # Check if columns exist
            c.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in c.fetchall()]
            
            if 'gender' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN gender TEXT")
            if 'contact_info' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN contact_info TEXT")
            if 'last_login' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
            if 'login_count' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0")
            if 'is_blocked' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0")
            if 'profession' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN profession TEXT")
                
            conn.commit()
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            
            # Hash password
            pwd_hash = self._hash_password(user_data['password'])
            
            # Replaced roll_no with profession, removed father_name/address from strict requirement if needed
            # We keep the schema compatible by passing None to removed fields if they exist in DB
            c.execute('''
                INSERT INTO users (
                    username, password_hash, first_name, last_name, 
                    email, education, profile_pic_path, gender, contact_info, 
                    profession, is_blocked, roll_no, father_name, address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
            ''', (
                user_data['username'], pwd_hash, user_data['first_name'], 
                user_data['last_name'], user_data.get('email'), 
                user_data.get('education'), user_data.get('profile_pic_path'), 
                user_data.get('gender'), user_data.get('contact_info'),
                user_data.get('profession'),
                # Deprecated fields passed as None/Empty
                user_data.get('roll_no', ''), user_data.get('father_name', ''), user_data.get('address', '') 
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print("Username already exists.")
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Verify credentials. Returns user dict if valid, None otherwise.
        Also updates login stats.
        """
        pwd_hash = self._hash_password(password)
        
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, pwd_hash))
        row = c.fetchone()
        
        if row:
            # Check if blocked
            if row['is_blocked']:
                conn.close()
                return {"error": "blocked"}

            # Update login stats
            try:
                import datetime
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_count = row['login_count'] if 'login_count' in row.keys() and row['login_count'] else 0
                c.execute("UPDATE users SET last_login = ?, login_count = ? WHERE username = ?", (now, current_count + 1, username))
                conn.commit()
                
                # Re-fetch to get updated data
                c.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = c.fetchone()
            except Exception as e:
                print(f"Error updating login stats: {e}")
                
            conn.close()
            return dict(row)
            
        conn.close()
        return None

    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """Update user profile details."""
        allowed_fields = [
            'first_name', 'last_name', 'father_name', 'roll_no', 
            'address', 'email', 'education', 'profile_pic_path',
            'gender', 'contact_info'
        ]
        
        fields_to_update = []
        values = []
        
        for k, v in updates.items():
            if k in allowed_fields:
                fields_to_update.append(f"{k} = ?")
                values.append(v)
        
        if not fields_to_update:
            return False
            
        values.append(username)
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE username = ?"
            c.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def block_user(self, username: str) -> bool:
        """Block a user."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            c.execute("UPDATE users SET is_blocked = 1 WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error blocking user: {e}")
            return False

    def unblock_user(self, username: str) -> bool:
        """Unblock a user."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            c.execute("UPDATE users SET is_blocked = 0 WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error unblocking user: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user details by username."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for admin dashboard."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT username, first_name, last_name, email, roll_no, gender, contact_info, education, last_login, login_count, is_blocked FROM users')
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
