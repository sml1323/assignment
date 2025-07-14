from datetime import date
from typing import List, Optional
from pydantic import BaseModel, field_validator

class Trademark(BaseModel):
    """
    상표 정보를 나타내는 Pydantic 모델
    """
    productName: Optional[str] = None
    productNameEng: Optional[str] = None
    applicationNumber: str
    applicationDate: Optional[date] = None
    registerStatus: Optional[str] = None
    publicationNumber: Optional[str] = None
    publicationDate: Optional[date] = None
    registrationNumber: Optional[List[Optional[str]]] = None
    registrationDate: Optional[List[Optional[date]]] = None
    internationalRegNumbers: Optional[str] = None
    internationalRegDate: Optional[date] = None
    priorityClaimNumList: Optional[List[Optional[str]]] = None
    priorityClaimDateList: Optional[List[Optional[date]]] = None
    asignProductMainCodeList: Optional[List[Optional[str]]] = None
    asignProductSubCodeList: Optional[List[Optional[str]]] = None
    viennaCodeList: Optional[List[Optional[str]]] = None

    @field_validator('applicationDate', 'publicationDate', 'internationalRegDate', mode='before')
    @classmethod
    def parse_date_string(cls, value: Optional[str]) -> Optional[date]:
        if value and isinstance(value, str) and len(value) == 8:
            try:
                return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
            except ValueError:
                return None
        return None

    @field_validator('registrationDate', 'priorityClaimDateList', mode='before')
    @classmethod
    def parse_date_list_string(cls, value: Optional[List[Optional[str]]]) -> Optional[List[Optional[date]]]:
        if not value:
            return None
        parsed_dates: List[Optional[date]] = []
        for date_str in value:
            if date_str and isinstance(date_str, str) and len(date_str) == 8:
                try:
                    parsed_dates.append(date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8])))
                except ValueError:
                    parsed_dates.append(None)
            else:
                parsed_dates.append(None)
        return parsed_dates 