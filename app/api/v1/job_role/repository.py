from abc import ABC, abstractmethod
from math import ceil

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.api.v1.job_role.schemas import TotalsJobs
from app.models import JobRoleORM


class JobRoleRepository(ABC):

    @abstractmethod
    def find_by_abbreviation(self, abbreviation: str) -> JobRoleORM | None:
        ...

    @abstractmethod
    def create(self, abbreviation: str, meaning: str) -> JobRoleORM:
        ...

    @abstractmethod
    def get_by_id(self, job_id: int) -> JobRoleORM | None:
        ...

    @abstractmethod
    def update(self, job: JobRoleORM, updates: dict) -> JobRoleORM:
        ...

    @abstractmethod
    def get_jobs(
        self,
        search: str | None,
        page: int,
        limit: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsJobs, list[JobRoleORM]]:
        ...


class JobRepositoryImpl(JobRoleRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_abbreviation(self, abbreviation: str) -> JobRoleORM | None:
        return self._db.execute(
            select(JobRoleORM).where(
                JobRoleORM.abbreviation == func.upper(abbreviation)
            )
        ).scalar_one_or_none()

    def create(self, abbreviation: str, meaning: str) -> JobRoleORM:
        job_orm = JobRoleORM(abbreviation=abbreviation, meaning=meaning)
        self._db.add(job_orm)
        self._db.flush()
        return job_orm

    def get_by_id(self, job_id: int) -> JobRoleORM | None:
        return self._db.get(JobRoleORM, job_id)

    def update(self, job: JobRoleORM, updates: dict) -> JobRoleORM:
        for attr, value in updates.items():
            setattr(job, attr, value)
        return job

    def get_jobs(
        self,
        search: str | None,
        page: int,
        limit: int,
        order_by: str,
        direction: str,
    ) -> tuple[TotalsJobs, list[JobRoleORM]]:
        stmt = self._apply_filters(select(JobRoleORM), search)
        total = self._count(search)
        totals = self._calculate_totals(total, limit, page)
        offset = totals.offset

        stmt = self._apply_order(stmt, order_by, direction)
        jobs = list(
            self._db.scalars(
                stmt.offset(offset).limit(limit)
            ).all()
        )
        return totals, jobs

    def _count(self, search: str | None) -> int:
        stmt = self._apply_filters(
            select(func.count()).select_from(JobRoleORM),
            search,
        )
        return self._db.scalar(stmt) or 0

    @staticmethod
    def _apply_filters(stmt: Select, search: str | None) -> Select:
        if search:
            term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    func.upper(JobRoleORM.abbreviation).like(term),
                    func.upper(JobRoleORM.meaning).like(term),
                )
            )
        return stmt

    @staticmethod
    def _calculate_totals(total: int, page_size: int, page: int) -> TotalsJobs:
        total_pages = ceil(total / page_size) if total else 0
        current_page = 1 if total_pages == 0 else min(page, total_pages)
        offset = (current_page - 1) * page_size

        return TotalsJobs(
            total=total,
            total_pages=total_pages,
            current_page=current_page,
            offset=offset,
        )

    @staticmethod
    def _apply_order(stmt: Select, order_by: str, direction: str) -> Select:
        if order_by == "abbreviation":
            column = JobRoleORM.abbreviation
        elif order_by == "meaning":
            column = JobRoleORM.meaning
        else:
            column = JobRoleORM.id

        if direction == "asc":
            return stmt.order_by(column.asc())

        return stmt.order_by(column.desc())
