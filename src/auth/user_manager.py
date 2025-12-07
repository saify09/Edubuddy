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
            if 'bio' not in columns:
                c.execute("ALTER TABLE users ADD COLUMN bio TEXT")
                
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
        conn = sqlite3.connect(self.db_path, timeout=20)
        c = conn.cursor()
        try:
            # Check if username exists
            c.execute("SELECT username FROM users WHERE username = ?", (user_data['username'],))
            if c.fetchone():
                return False

            c.execute('''
                INSERT INTO users (
                    username, password_hash, first_name, last_name, 
                    email, contact_info, gender, profession, bio, profile_pic_path, 
                    login_count, is_blocked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            ''', (
                user_data['username'],
                self._hash_password(user_data['password']),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('email'),
                user_data.get('contact_info'),
                user_data.get('gender'),
                user_data.get('profession'),
                user_data.get('bio'),
                user_data.get('profile_pic_path')
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """Update user details."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        c = conn.cursor()
        try:
            # Filter allowed fields
            allowed_fields = [
                'first_name', 'last_name', 'father_name', 'address', 'email', 
                'education', 'profile_pic_path', 'gender', 'contact_info', 
                'profession', 'bio'
            ]
            
            valid_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not valid_updates:
                return False
                
            query_parts = [f"{k} = ?" for k in valid_updates.keys()]
            values = list(valid_updates.values())
            values.append(username)
            
            query = f"UPDATE users SET {', '.join(query_parts)} WHERE username = ?"
            c.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            conn.close()

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user details by username."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = c.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None
        finally:
            conn.close()



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



    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for admin dashboard."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT username, first_name, last_name, email, roll_no, gender, contact_info, education, last_login, login_count, is_blocked FROM users')
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
