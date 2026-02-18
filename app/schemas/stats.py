from pydantic import BaseModel
from typing import List, Tuple

class UserStats(BaseModel):
    user_id: int
    username: str
    count: int   # для количества достижений
    total_points: int  # для суммы баллов

class UserPair(BaseModel):
    user1_id: int
    user1_username: str
    user2_id: int
    user2_username: str
    difference: int