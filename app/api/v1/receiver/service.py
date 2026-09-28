from sqlalchemy.orm import Session

from app.api.v1.receiver.repository import ReceiverRepository


class ReceiverService:
    def __init__(self, repo: ReceiverRepository, db: Session):
        self._db = db
        self._repo = repo

    def find_by_name(self, name: str):
        pass

    def create_receiver(self):
        pass

