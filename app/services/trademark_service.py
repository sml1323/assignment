import json
from datetime import date
from typing import List, Optional
from app.models.trademark import Trademark
from app.core.config import TRADEMARK_JSON_PATH

def load_trademarks_from_json(filepath: str = TRADEMARK_JSON_PATH) -> List[Trademark]:
    """
    JSON 파일에서 상표 데이터를 로드하여 Pydantic 객체 리스트로 반환
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    processed_objects: List[Trademark] = []
    for item_dict in raw_data_list:
        if not item_dict.get("applicationNumber"):
            continue
        try:
            processed_objects.append(Trademark(**item_dict))
        except Exception:
            continue
    return processed_objects

def filter_trademarks(
    data: List[Trademark],
    status: Optional[str] = None,
    product_name: Optional[str] = None,
    application_number: Optional[str] = None,
    app_date_from: Optional[date] = None,
    app_date_to: Optional[date] = None
) -> List[Trademark]:
    """
    상표 데이터 리스트를 다양한 조건에 따라 필터링
    """
    results = data
    if status:
        results = [tm for tm in results if tm.registerStatus and tm.registerStatus.lower() == status.lower()]
    if product_name:
        results = [tm for tm in results if tm.productName and product_name.lower() in tm.productName.lower()]
    if application_number:
        results = [tm for tm in results if tm.applicationNumber == application_number]
    if app_date_from:
        results = [tm for tm in results if tm.applicationDate and tm.applicationDate >= app_date_from]
    if app_date_to:
        results = [tm for tm in results if tm.applicationDate and tm.applicationDate <= app_date_to]
    return results 