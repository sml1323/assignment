from fastapi import APIRouter
from typing import List, Optional
from datetime import date
from app.models.trademark import Trademark
from app.services.trademark_service import filter_trademarks
from app.services.state import get_trademarks_obj_list
from app.core.config import DEFAULT_SKIP, DEFAULT_LIMIT

router = APIRouter()

@router.get(
    "/trademarks",
    response_model=List[Trademark],
    summary="상표 정보 검색",
    description="""
다양한 조건으로 상표 정보를 검색하고, 페이지네이션된 결과를 반환합니다.\n\n**필터 조건:**\n- `status`: 상표 등록 상태 (예: "등록", "출원", "실효", "거절")\n- `product_name`: 상품명 \n- `application_number`: 출원 번호 \n- `application_date_from`: 출원일 검색 시작일 (YYYY-MM-DD 형식)\n- `application_date_to`: 출원일 검색 종료일 (YYYY-MM-DD 형식)\n\n**페이지네이션:**\n- `skip`: 건너뛸 항목 수 (기본값: 0)\n- `limit`: 한 페이지에 표시할 항목 수 (기본값: 10)
"""
)
async def search_trademarks(
    status: Optional[str] = None,
    product_name: Optional[str] = None,
    application_number: Optional[str] = None,
    application_date_from: Optional[date] = None,
    application_date_to: Optional[date] = None,
    skip: int = DEFAULT_SKIP,
    limit: int = DEFAULT_LIMIT
) -> List[Trademark]:
    filtered = filter_trademarks(
        data=get_trademarks_obj_list(),
        status=status,
        product_name=product_name,
        application_number=application_number,
        app_date_from=application_date_from,
        app_date_to=application_date_to
    )
    return filtered[skip: skip + limit] 