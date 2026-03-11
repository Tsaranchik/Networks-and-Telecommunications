from dataclasses import dataclass
from fastapi import Query
from sqlalchemy import asc, desc


@dataclass(frozen=True)
class ListParams:
    limit: int
    offset: int
    sort_by: str
    sort_dir: str


def list_params(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
) -> ListParams:
    return ListParams(limit=limit, offset=offset, sort_by=sort_by, sort_dir=sort_dir)


def apply_list_params(stmt, model, params: ListParams, allowed_sort_fields: set[str]):
    sort_by = params.sort_by if params.sort_by in allowed_sort_fields else "id"
    sort_dir = params.sort_dir.lower()

    order_col = getattr(model, sort_by)
    order = asc(order_col) if sort_dir != "desc" else desc(order_col)

    return stmt.order_by(order).limit(params.limit).offset(params.offset)
