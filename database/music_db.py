import mysql.connector
from datetime import datetime
from config.settings import MYSQL_CONFIG

class MusicDatabase:
    def __init__(self):
        self.db_config = MYSQL_CONFIG
        self.init_db()

    def get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                artist VARCHAR(255),
                url VARCHAR(512),
                source VARCHAR(50),
                file_path VARCHAR(512),
                download_date DATETIME,
                INDEX idx_title (title),
                INDEX idx_url (url)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()

    def add_song(self, title, artist, url, source, file_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            INSERT INTO songs (title, artist, url, source, file_path, download_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (title, artist, url, source, file_path, datetime.now())
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

    def find_song(self, title):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM songs WHERE title LIKE %s', (f'%{title}%',))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return result

    def get_song_by_url(self, url):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM songs WHERE url = %s', (url,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return result

    def get_recent_songs(self, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM songs ORDER BY download_date DESC LIMIT %s', (limit,))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return results
