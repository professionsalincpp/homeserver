class User:
    def __init__(self, username, password, is_admin=False, id: int | None = None):
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.id = id

    def __str__(self):
        return self.username
    
    def __repr__(self):
        return self.username
    
    def __eq__(self, other):
        return self.username == other.username