from core import UnitOfWork


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
