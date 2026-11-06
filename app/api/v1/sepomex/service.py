from fastapi import HTTPException, status

from app.api.v1.sepomex.repository import SepomexRepository
from app.api.v1.sepomex.schemas import SepomexDto


class SepomexService:

    def __init__(self, repo: SepomexRepository):
        self._repo = repo

    def get_by_postal_code(self, postal_code: str) -> list[SepomexDto]:
        settlements = self._repo.find_by_postal_code(postal_code)
        if not settlements:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Código postal {postal_code} no existe en el catálogo",
            )
        return [
            SepomexDto.model_validate(settlement, from_attributes=True)
            for settlement in settlements
        ]
