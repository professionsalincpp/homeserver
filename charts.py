import json
from typing import overload

class Chart:
    @overload
    def __init__(self, name: str, data: str) -> None: ...
    @overload
    def __init__(self, name: str, data: dict) -> None: ...
    def __init__(self, name: str, data: dict | str) -> None:
        self.name = name
        if isinstance(data, str):
            self.data = json.loads(data)
        else:
            self.data = data
    
    def __str__(self) -> str:
        return json.dumps(self.data)
    
    def __repr__(self) -> str:
        return f'{self.name}: ' + json.dumps(self.data)
    
    def __eq__(self, other) -> bool:
        return self.data == other.data
    
    def __ne__(self, other) -> bool:
        return self.data != other.data
    
    def __hash__(self) -> int:
        return hash(self.data)
    
    def __getitem__(self, key) -> any:
        return self.data[key]
    
    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __delitem__(self, key) -> None:
        del self.data[key]

    def dumps(self) -> str:
        return json.dumps(self.data)
    
    def loads(self, data: str) -> None:
        self.data = json.loads(data)

    def join(self, other: 'Chart') -> 'Chart':
        return Chart(self.name, self.data + other.data)
    
    def add_data(self, key: str, value: any) -> None:
        self.data.append([key, value])
