from __future__ import annotations

import uuid

class Entity:
    def __init__(self): 
        self.id = uuid.uuid4()