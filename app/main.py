from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import List
from app.models.trademark import Trademark
from app.services.trademark_service import load_trademarks_from_json
from app.api.trademarks import router as trademarks_router
from app.core.config import TRADEMARK_JSON_PATH
from app.services.state import trademarks_obj_list

@asynccontextmanager
async def lifespan(app: FastAPI):
    global trademarks_obj_list
    trademarks_obj_list.clear()
    trademarks_obj_list.extend(load_trademarks_from_json(TRADEMARK_JSON_PATH))
    yield

app = FastAPI(
    lifespan=lifespan,
    title="상표 검색 API",
    version="1.0.0",
    description="""
상표 정보를 검색하고 필터링하는 API입니다.\n`trademark_sample.json` 파일에서 데이터를 로드하여 사용합니다.\n**날짜 형식은 YYYY-MM-DD 를 지원합니다.**
"""
)

app.include_router(trademarks_router)