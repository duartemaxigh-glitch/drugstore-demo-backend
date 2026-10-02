from typing import Protocol


class PasswordHasher(Protocol):
    def generar_hash(self, password: str) -> str:
        ...

    def verificar(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        ...
