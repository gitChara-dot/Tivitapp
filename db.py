
import sqlite3
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_name="tivitapp.db"):
        self.db_name = db_name
        self.create_table()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn # Allow functions to use conn
            conn.commit() # Save when finished
        except Exception as e:
            conn.rollback() # If an error occurs, rollback changes
            raise e 
        finally:
            conn.close() 

    def create_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    deadline TEXT,
                    priority TEXT,
                    state TEXT
                )
            """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS timers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    length INTEGER NOT NULL
                    )
                    """
                )
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    length INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    uuid TEXT NOT NULL
                    )
                    """
                )

    def add_task(self, name, deadline, priority, state):
        with self._connect() as conn:
            cursor = conn.cursor()
            
            insert = "INSERT INTO tasks (name, deadline, priority, state) VALUES (?,?,?,?)"
            data = (name, deadline, priority, state)
            cursor.execute(insert, data)
            
            unique_id = cursor.lastrowid
            return unique_id

    def get_tasks(self):
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tasks")

            tasks = cursor.fetchall()
            
            return tasks
    def delete_task(self, task_id):
        with self._connect() as conn:
            cursor = conn.cursor()

            deletion = "DELETE FROM tasks WHERE id = ?"
            cursor.execute(deletion, (task_id,))

      

    def update(self,name: str, deadline: str, priority : str, state : str, task_id: int ):
        with self._connect() as conn:
            cursor = conn.cursor()
            
            update_query = """
            UPDATE tasks
            SET name = ?,
            deadline = ?,
            priority = ?,
            state = ?
            WHERE id = ?
            
            """
            data = (name, deadline, priority, state, task_id)
            cursor.execute(update_query, data)

    def get_alive_tasks_number(self):
    
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
            SELECT COUNT(*) FROM tasks
            """)

            number = cursor.fetchone()[0]

            return number

    def add_timer(self, type: str,  length: int):
        with self._connect() as conn:
            cursor = conn.cursor()

            insert = "INSERT INTO timers (type, length) VALUES (?, ?)"
            data = (type, length)

            cursor.execute(insert, data)
            timer_uuid = cursor.lastrowid

            return timer_uuid
    
    def delete_timer(self, timer_uuid: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            
            deletion = "DELETE FROM timers WHERE id = ?"
            cursor.execute(deletion, (timer_uuid, ))

    def get_timers(self):
        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM timers")

            data = cursor.fetchall() 

            return data

    def log_activity(self, type: str, length: int,  uuid : str):
        timestamp = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.cursor()

            query = "INSERT INTO activity (type, length, timestamp, uuid) VALUES (?,?,?,?)"
            data = (type,length, timestamp, uuid)
            cursor.execute(query, data)
    
    def delete_activity_id(self, id : int):
        with self._connect() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM activity WHERE id = ?"
            cursor.execute(query, (id, ))
    def delete_activity_from_session(self, uuid : str):
        with self._connect() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM activity WHERE uuid = ?"
            cursor.execute(query, (uuid, ))
    
    def get_activity_from_id(self, id : int):
        with self._connect() as conn:

            cursor = conn.cursor()
            query = "SELECT * FROM activity WHERE id = ?"
            cursor.execute(query, (id,))

            data = cursor.fetchall()

            return data
    def get_all_activity_from_uuid(self, uuid : int):
        with self._connect() as conn:

            cursor = conn.cursor()
            query = "SELECT * FROM activity WHERE uuid = ?"
            cursor.execute(query, (uuid,))

            data = cursor.fetchall()

            return data
    def get_activity_from_day(self, timestamp : str): # Asumes date in YYYY-MM-DD
        with self._connect() as conn:
            cursor = conn.cursor()
            search_param = f"{timestamp}%"
            query = "SELECT * FROM activity WHERE timestamp LIKE ? ORDER BY timestamp DESC"
            cursor.execute(query, (search_param,))

            data = cursor.fetchall()

            return data

    def get_activity_since_date(self, timestamp:str): # # Asumes date in ISO 8601 Ex. 2026-02-03T19:00:00
        with self._connect() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM activity WHERE timestamp >= ? ORDER BY timestamp DESC;"

            cursor.execute(query, (timestamp,))

            data = cursor.fetchall()

            return data
        
    def get_activity_between_dates(self, timestamp_begin :str, timestamp_end : str):
        with self._connect() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM activity WHERE timestamp >= ? AND timestamp<= ? ORDER BY timestamp DESC;"

            cursor.execute(query, (timestamp_begin, timestamp_end))

            data = cursor.fetchall()

            return data


        