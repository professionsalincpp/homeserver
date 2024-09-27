class Channel:
    def __init__(self, name: str, owner_id: int, id: int | None = None):
        self.name = name
        self.owner_id = owner_id
        self.id = id if isinstance(id, int) else id

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'{self.name}: {self.owner_id}'