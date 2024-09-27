import json
import typing
from user import User
from charts import Chart
import sqlite3
from channel import Channel

class UserDatabase:
    def __init__(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT,
            password TEXT,
            is_admin INTEGER
        )""")

    def delete_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.connection.commit()

    def add_user(self, user: User):
        if self.check_username_exists(user.username):
            return
        self.cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (user.username, user.password, user.is_admin))
        self.connection.commit()

    def get_user(self, username) -> typing.Optional[User]:
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        fetched = self.cursor.fetchone()
        if fetched:
            usr = User(fetched[1], fetched[2], fetched[3], fetched[0])
            return usr
        else:
            return None
        
    def get_user_id(self, username) -> typing.Optional[int]:
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        fetched = self.cursor.fetchone()
        if fetched:
            return fetched[0]
        else:
            return None
        
    def delete_user(self, username):
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.connection.commit()

    def close(self):
        self.connection.close()

    def get_all_users(self) -> list[User]:
        self.cursor.execute("SELECT * FROM users")
        fetched = self.cursor.fetchall()
        users = []
        for user in fetched:
            users.append(User(user[1], user[2], user[3]))
        return users
    
    def update_user(self, user: User):
        if not self.check_username_exists(user.username):
            print("User doesn't exist")
            return
        self.cursor.execute("UPDATE users SET password = ?, is_admin = ? WHERE username = ?", (user.password, user.is_admin, user.username))
        self.connection.commit()

    def authenticate_user(self, username, password) -> bool:
        user = self.get_user(username)
        if user:
            if user.password == password:
                return True
            return False
        else:
            return False
        
    def register_user(self, username, password):
        if self.check_username_exists(username):
            print("Username already exists")
            return
        user = User(username, password)
        self.add_user(user)
        print("User registered")
        
    def check_username_exists(self, username):
        user = self.get_user(username)
        print(f"Checking if {username} exists: {user}")
        if user:
            return True
        else:
            return False
        
    def check_password(self, username, password):
        user = self.get_user(username)
        if user and user[1] == password:
            return True
        else:
            return False
        
    def check_admin(self, username):
        user = self.get_user(username)
        if user and user[2] == 1:
            return True
        else:
            return False
        

class ChannelDatabase:
    def __init__(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.create_table()

    def delete_table(self):
        self.cursor.execute("DROP TABLE channels")
        self.connection.commit()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner_id INTEGER
        )""")
        self.connection.commit()

    def get_channel(self, name, owner_id: typing.Optional[int] = None) -> typing.Optional[Channel]:
        if owner_id:
            self.cursor.execute("SELECT * FROM channels WHERE name = ? AND owner_id = ?", (name, owner_id))
        else:
            self.cursor.execute("SELECT * FROM channels WHERE name = ?", (name,))
        fetched = self.cursor.fetchone()
        if fetched:
            channel = Channel(fetched[1], fetched[2], fetched[0])
            return channel
        else:
            return None
        
    def get_channel_by_id(self, channel_id: int) -> typing.Optional[Channel]:
        self.cursor.execute("SELECT * FROM channels WHERE id = ?", (channel_id,))
        fetched = self.cursor.fetchone()
        if fetched:
            channel = Channel(fetched[1], fetched[2], fetched[0])
            return channel
        else:
            return None
        
    def get_channel_id(self, name) -> typing.Optional[int]:
        self.cursor.execute("SELECT * FROM channels WHERE name = ?", (name,))
        fetched = self.cursor.fetchone()
        if fetched:
            channel = fetched[0]
            return channel
        else:
            return None
        
    def get_channel_name(self, id: int) -> typing.Optional[str]:
        self.cursor.execute("SELECT name FROM channels WHERE id = ?", (id,))
        fetched = self.cursor.fetchone()
        if fetched:
            return fetched[1]
        else:
            return None

    def add_channel(self, channel: Channel) -> int:
        if self.get_channel(channel.name) is not None:
            return
        self.cursor.execute("INSERT INTO channels (name, owner_id) VALUES (?, ?)", (channel.name, channel.owner_id))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_channels(self):
        self.cursor.execute("SELECT * FROM channels")
        fetched = self.cursor.fetchall()
        channels = []
        for channel in fetched:
            print(channel)
            channels.append(Channel(channel[1], channel[2], channel[0]))
        return channels
    
    def get_owner_channels(self, owner_id: int) -> list[Channel]:
        self.cursor.execute("SELECT * FROM channels WHERE owner_id = ?", (owner_id,))
        fetched = self.cursor.fetchall()
        channels = []
        for channel in fetched:
            channels.append(Channel(channel[1], channel[2], channel[0]))
        return channels

class ChartsDatabase:
    def __init__(self, filename):    
        self.filename = filename
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.create_table()

    def get_all_charts(self) -> dict[str, Chart]:
        self.cursor.execute("SELECT * FROM charts")
        fetched = self.cursor.fetchall()
        charts = {}
        for chart in fetched:
            charts[chart[0]] = Chart(chart[0], json.loads(chart[1]))
        return charts
    
    def get_channel_charts(self, channel_id: int) -> dict[str, Chart]:
        self.cursor.execute("SELECT * FROM charts WHERE channel_id = ?", (channel_id,))
        fetched = self.cursor.fetchall()
        charts = {}
        for chart in fetched:
            charts[chart[0]] = Chart(chart[0], json.loads(chart[1]))
        return charts
    
    def delete_table(self):
        self.cursor.execute("DROP TABLE charts")
        self.connection.commit()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS charts (
            name TEXT,
            data TEXT,
            channel_id INTEGER,
            FOREIGN KEY(channel_id) REFERENCES channels(id)
        )""")

    def add_chart(self, channel_id: int, chart: Chart) -> None:
        if self.get_chart(channel_id, chart.name):
            return
        self.cursor.execute("INSERT INTO charts VALUES (?, ?, ?)", (chart.name, str(chart), channel_id))
        self.connection.commit()

    def get_chart(self, channel_id: int, name) -> typing.Optional[Chart]:
        self.cursor.execute("SELECT * FROM charts WHERE name = ? AND channel_id = ?", (name, channel_id))
        fetched = self.cursor.fetchone()
        if fetched:
            chart = Chart(fetched[0], json.loads(fetched[1]))
            return chart
        else:
            return None

    def close(self) -> None:
        self.connection.close()

    def update_chart(self, channel_id: int, chart: Chart) -> None:
        self.cursor.execute("UPDATE charts SET data = ? WHERE name = ? AND channel_id = ?", (str(chart), chart.name, channel_id))
        self.connection.commit()
        