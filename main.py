from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from typing import List, Optional, List, Dict, Any
import json
from contextlib import asynccontextmanager
from datetime import date

trademarks_data: List[Dict[str, Any]] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global trademarks_data
    print("애플리케이션 시작: 데이터 로딩을 시도합니다...")
    try:
        with open("trademark_sample.json", "r", encoding="utf-8") as f:
            raw_data_list = json.load(f) 
        
        processed_data = []
        for item_dict in raw_data_list:
            try:
                # applicationNumber가 없는 경우를 대비 
                if "applicationNumber" not in item_dict or item_dict["applicationNumber"] is None:
                    print(f"데이터 로딩 중 필수 필드 'applicationNumber' 누락 (항목 건너뜀): {item_dict}")
                    skipped_count += 1
                    continue 
                trademark_obj = Trademark(**item_dict)
                processed_data.append(trademark_obj.model_dump())
            except Exception as e: 
                print(f"데이터 로딩 중 변환 오류 (항목 건너뜀): {item_dict}, 오류: {e}")
        
        trademarks_data = processed_data
        print(f"애플리케이션 시작: {len(trademarks_data)}개의 상표 데이터를 성공적으로 로드 및 변환했습니다.")
    except Exception as e: 
        trademarks_data = [] 
        print(f"lifespan 데이터 로딩 중 예상치 못한 오류 발생: {e}")
    
    yield
    print("애플리케이션 종료.")

app = FastAPI(lifespan=lifespan)


class Trademark(BaseModel):
    productName: Optional[str] = None
    productNameEng: Optional[str] = None
    applicationNumber: str
    applicationDate: Optional[date] = None
    registerStatus: Optional[str] = None
    publicationNumber: Optional[str] = None
    publicationDate: Optional[date] = None
    registrationDate: Optional[List[Optional[date]]] = None
    internationalRegNumbers: Optional[str] = None
    internationalRegDate: Optional[date] = None
    priorityClaimNumList: Optional[List[str]] = None
    priorityClaimDateList: Optional[List[Optional[date]]] = None
    asignProductMainCodeList: Optional[List[str]] = None
    asignProductSubCodeList: Optional[List[str]] = None
    viennaCodeList: Optional[List[str]] = None
    @field_validator('applicationDate', 'publicationDate', 'internationalRegDate', mode='before')
    @classmethod
    def parse_date_string(cls, value: Optional[str]) -> Optional[date]:
        if value and isinstance(value, str) and len(value) == 8:
            try:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8]) 
                return date(year, month, day)
            except ValueError:
                print(f"날짜 변환 오류 (parse_date_string): '{value}'") 
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
                    year = int(date_str[:4])
                    month = int(date_str[4:6])
                    day = int(date_str[6:8])
                    parsed_dates.append(date(year, month, day))
                except ValueError:
                    print(f"날짜 리스트 내 항목 변환 오류 (parse_date_list_string): '{date_str}'")
                    parsed_dates.append(None) 
            else:
                
                parsed_dates.append(None) 
        return parsed_dates
                

@app.get("/trademarks", response_model=List[Trademark])
async def search_trademarks(
    status: Optional[str] = None, 
    product_name: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 10
):
    results = trademarks_data

    if status:
        results = [
            tm for tm in results if tm.get("registerStatus") and tm.get("registerStatus").lower() == status.lower()
        ]
    
    if product_name:
        results = [
            tm for tm in results
            if tm.get("productName") and product_name.lower() in tm.get("productName").lower()
        ]
    
    final_results = []
    for tm_dict in results[skip : skip + limit]:
        try:
            trademark_obj = Trademark(**tm_dict)
            final_results.append(trademark_obj)
        except Exception as e: 
            print(f"Error converting item: {tm_dict}, Error: {e}")
    print(f"--- 'status=등록' 필터링 후 current_results의 길이: {len(final_results)} ---") 
    print(f"--- skip: {skip}, limit: {limit} ---") 

    return final_results 




    


