import sqlite3
import datetime
import os

class AnalyticsLogger:
    def __init__(self, db_path: str = "edubuddy_users.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the analytics tables."""
        conn = sqlite3.connect(self.db_path, timeout=20)
        c = conn.cursor()
        
        # Ingestion Logs
        c.execute('''
            CREATE TABLE IF NOT EXISTS ingestion_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                file_type TEXT,
                file_size_bytes INTEGER,
                timestamp TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def log_ingestion(self, filename: str, file_size: int, status: str = "success"):
        """Log a file ingestion event."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            
            file_type = os.path.splitext(filename)[1].lower().replace('.', '')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            c.execute('''
                INSERT INTO ingestion_logs (filename, file_type, file_size_bytes, timestamp, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, file_type, file_size, timestamp, status))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging ingestion: {e}")

    def get_ingestion_stats(self):
        """Get stats for analytics dashboard."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # File Type Distribution
            c.execute('''
                SELECT file_type, COUNT(*) as count 
                FROM ingestion_logs 
                WHERE status = 'success'
                GROUP BY file_type
            ''')
            type_stats = {row['file_type']: row['count'] for row in c.fetchall()}
            
            conn.close()
            return type_stats
        except Exception as e:
            print(f"Error getting stats: {e}")
    def delete_ingestion_logs(self) -> bool:
        """Delete all ingestion logs."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            c = conn.cursor()
            c.execute("DELETE FROM ingestion_logs")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting logs: {e}")
            return False
