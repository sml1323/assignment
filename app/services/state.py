from typing import List
from app.models.trademark import Trademark

trademarks_obj_list: List[Trademark] = []

def get_trademarks_obj_list() -> List[Trademark]:
    return trademarks_obj_list 