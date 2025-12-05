# EduBuddy Authentication Guide

This guide explains how to manage user accounts and verify logins in the EduBuddy application.

## 1. User Signup & Login

### Signup Rules
*   **Username**: Must be unique and at least 4 characters long.
*   **Password**: Must be at least 6 characters long.
*   **Required Fields**: Username and Password are marked with red stars (*).

### Login
*   Use your registered username and password.
*   If you forget your password, an admin must reset it directly in the database (see below).

## 2. Checking Accounts (Admin)

The user data is stored in a SQLite database file: `userdata/users.db`.

### Option A: Using a SQLite Viewer
1.  Download a tool like **DB Browser for SQLite**.
2.  Open `userdata/users.db`.
3.  Browse the `users` table to see all registered accounts.
    *   **Note**: Passwords are hashed (encrypted), so you cannot read them directly.

### Option B: Using Python Script
You can run the following script to list all users:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('userdata/users.db')
df = pd.read_sql_query("SELECT username, first_name, last_name, email FROM users", conn)
print(df)
conn.close()
```

## 3. Resetting Passwords

Since there is no "Forgot Password" feature in the UI yet, an admin must reset it manually:

1.  Open `userdata/users.db` in DB Browser for SQLite.
2.  Find the user in the `users` table.
3.  You cannot type a plain password. You must generate a SHA-256 hash for the new password.
    *   Example Hash for `password123`: `ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f`
4.  Replace the `password_hash` value with the new hash.
5.  Save changes.
