from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from app.api.v1.receiver.repository import ReceiverRepository


class ReceiverService(ABC):

    @abstractmethod
    def find_by_name(self, name: str):
        ...

    @abstractmethod
    def create_receiver(self):
        ...


class ReceiverServiceImpl(ReceiverService):

    def __init__(self, repo: ReceiverRepository, db: Session):
        self._db = db
        self._repo = repo


    def create_receiver(self):
        pass

    def find_by_name(self, name: str):
        pass

