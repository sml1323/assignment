from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from typing import List, Optional
import json
from contextlib import asynccontextmanager
from datetime import date

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 애플리케이션의 시작과 종료 시점에 실행되는 lifespan 이벤트 핸들러입니다.

    애플리케이션 시작 시:
    - `trademark_sample.json` 파일에서 상표 데이터를 로드합니다.
    - 각 데이터 항목을 `Trademark` Pydantic 모델 객체로 변환합니다.
    - 변환된 객체 리스트를 전역 변수 `trademarks_obj_list`에 할당합니다.
    - 데이터 로딩 중 발생하는 오류(파일 없음, JSON 디코딩 오류 등)를 처리합니다.

    애플리케이션 종료 시:
    - 간단한 종료 메시지를 출력합니다.

    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스.
    """
    global trademarks_obj_list 
    print("애플리케이션 시작: 데이터 로딩 및 Pydantic 객체로 변환 시도...")
    try:
        with open("trademark_sample.json", "r", encoding="utf-8") as f:
            raw_data_list = json.load(f) 
        
        processed_objects: List[Trademark] = [] 
        skipped_count = 0
        for item_dict in raw_data_list:
            try:
                if "applicationNumber" not in item_dict or item_dict["applicationNumber"] is None:
                    print(f"데이터 로딩 중 필수 필드 'applicationNumber' 누락 (항목 건너뜀): {item_dict}")
                    skipped_count += 1
                    continue 
                
                trademark_object = Trademark(**item_dict)
                processed_objects.append(trademark_object) 
                
            except Exception as e: 
                print(f"데이터 로딩 중 변환 오류 (항목 건너뜀): {item_dict}, 오류: {e}")
                skipped_count += 1
        
        trademarks_obj_list = processed_objects
        print(f"애플리케이션 시작: 총 {len(raw_data_list)}개 중 {len(trademarks_obj_list)}개의 상표 객체 로드 완료 ({skipped_count}개 건너뜀).")
    
    except FileNotFoundError:
        trademarks_obj_list = []
        print("trademark_sample.json 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        trademarks_obj_list = []
        print("trademark_sample.json 파일을 읽는 중 오류 발생.")
    except Exception as e: 
        trademarks_obj_list = [] 
        print(f"lifespan 데이터 로딩 중 예상치 못한 오류 발생: {e}")
    
    yield
    print("애플리케이션 종료.")

class Trademark(BaseModel):
    """
    상표 정보를 나타내는 Pydantic 모델입니다.

    JSON 데이터의 각 필드를 파싱하고 유효성을 검사합니다.
    날짜 관련 필드는 'YYYYMMDD' 형식의 문자열을 Python `date` 객체로 변환합니다.
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
        """
        'YYYYMMDD' 형식의 문자열을 `date` 객체로 변환합니다.

        Args:
            value (Optional[str]): 변환할 날짜 문자열.

        Returns:
            Optional[date]: 변환된 `date` 객체 또는 변환 실패 시 None.
        """
        if value and isinstance(value, str) and len(value) == 8:
            try:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8]) 
                return date(year, month, day)
            except ValueError:
                return None
        return None 

    @field_validator('registrationDate', 'priorityClaimDateList', mode='before')
    @classmethod
    def parse_date_list_string(cls, value: Optional[List[Optional[str]]]) -> Optional[List[Optional[date]]]:
        """
        'YYYYMMDD' 형식의 문자열 리스트를 `date` 객체 리스트로 변환합니다.
        리스트 내의 각 항목에 대해 변환을 시도합니다.

        Args:
            value (Optional[List[Optional[str]]]): 변환할 날짜 문자열 리스트.

        Returns:
            Optional[List[Optional[date]]]: 변환된 `date` 객체 리스트 또는 원본 값이 없을 경우 None.
                                         리스트 내 변환 실패 항목은 None으로 유지됩니다.
        """
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
                    parsed_dates.append(None) 
            else:
                parsed_dates.append(None) 
        return parsed_dates
trademarks_obj_list: List[Trademark] = []
app = FastAPI(lifespan=lifespan, title="상표 검색 API", version="1.0.0",
              description="""
상표 정보를 검색하고 필터링하는 API입니다.
`trademark_sample.json` 파일에서 데이터를 로드하여 사용합니다.
**날짜 형식은 YYYY-MM-DD 를 지원합니다.**
""")

                
def filter_trademarks_data(
    data_to_filter: List[Trademark],
    status: Optional[str] = None,
    product_name: Optional[str] = None,
    application_number: Optional[str] = None,
    app_date_from: Optional[date] = None,
    app_date_to: Optional[date] = None    
) -> List[Trademark]:
    """
    주어진 상표 데이터 리스트를 다양한 조건에 따라 필터링합니다.

    Args:
        data_to_filter (List[Trademark]): 필터링할 원본 Trademark 객체 리스트.
        status (Optional[str]): 필터링할 상표 등록 상태 (예: "등록", "실효").
        product_name (Optional[str]): 필터링할 상품명 (부분 일치 검색).
        application_number (Optional[str]): 필터링할 출원 번호 (정확히 일치).
        app_date_from (Optional[date]): 필터링할 출원일 시작 날짜.
        app_date_to (Optional[date]): 필터링할 출원일 종료 날짜.

    Returns:
        List[Trademark]: 필터링된 Trademark 객체 리스트.
    """
    
    current_results = list(data_to_filter)

    if status:
        current_results = [
            tm for tm in current_results 
            if tm.registerStatus and tm.registerStatus.lower() == status.lower()
        ]
    
    if product_name:
        current_results = [
            tm for tm in current_results
            if tm.productName and product_name.lower() in tm.productName.lower()
        ]

    if application_number:
        current_results = [
            tm for tm in current_results if tm.applicationNumber == application_number
        ]
        
    if app_date_from:
        current_results = [
            tm for tm in current_results
            if tm.applicationDate and tm.applicationDate >= app_date_from
        ]

    if app_date_to:
        current_results = [
            tm for tm in current_results
            if tm.applicationDate and tm.applicationDate <= app_date_to
        ]
    # -------------------------------------------------
    
    return current_results


@app.get("/trademarks",
         response_model=List[Trademark],
         summary="상표 정보 검색",
         description="""
다양한 조건으로 상표 정보를 검색하고, 페이지네이션된 결과를 반환합니다.

**필터 조건:**
- `status`: 상표 등록 상태 (예: "등록", "출원", "실효", "거절")
- `product_name`: 상품명 
- `application_number`: 출원 번호 
- `application_date_from`: 출원일 검색 시작일 (YYYY-MM-DD 형식)
- `application_date_to`: 출원일 검색 종료일 (YYYY-MM-DD 형식)

**페이지네이션:**
- `skip`: 건너뛸 항목 수 (기본값: 0)
- `limit`: 한 페이지에 표시할 항목 수 (기본값: 10)
""")
async def search_trademarks(
    status: Optional[str] = None, 
    product_name: Optional[str] = None, 
    application_number: Optional[str] = None,
    application_date_from: Optional[date] = None, 
    application_date_to: Optional[date] = None,
    # ---------------------------------
    skip: int = 0, 
    limit: int = 10
) -> List[Trademark]:
    """
    상표 정보를 검색하는 API 엔드포인트입니다.

    전역에 로드된 `trademarks_obj_list`를 기준으로 `filter_trademarks_data` 함수를 호출하여
    조건에 맞는 상표들을 필터링하고, `skip`과 `limit`을 사용하여 페이지네이션된 결과를 반환합니다.

    Args:
        status (Optional[str]): 상표 등록 상태 필터.
        product_name (Optional[str]): 상품명 필터.
        application_number (Optional[str]): 출원 번호 필터.
        application_date_from (Optional[date]): 출원일 시작 날짜 필터. FastAPI에 의해 date 객체로 변환됩니다.
        application_date_to (Optional[date]): 출원일 종료 날짜 필터. FastAPI에 의해 date 객체로 변환됩니다.
        skip (int): 페이지네이션을 위해 건너뛸 항목 수. 기본값은 0입니다.
        limit (int): 페이지네이션을 위해 한 페이지에 반환할 최대 항목 수. 기본값은 10입니다.

    Returns:
        List[Trademark]: 필터링 및 페이지네이션된 Trademark 객체 리스트.
    """
    
    filtered_trademark_objects = filter_trademarks_data(
        data_to_filter=trademarks_obj_list,
        status=status,
        product_name=product_name,
        application_number=application_number,
        app_date_from=application_date_from,
        app_date_to=application_date_to
    )
    paginated_trademark_objects = filtered_trademark_objects[skip : skip + limit]
    
    print(f"--- 최종 반환될 결과의 길이: {len(paginated_trademark_objects)} (skip: {skip}, limit: {limit}) ---")

    return paginated_trademark_objects