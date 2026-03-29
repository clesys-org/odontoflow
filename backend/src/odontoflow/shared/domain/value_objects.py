"""Self-validating Value Objects for the dental domain."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CPF:
    """CPF brasileiro — valida digitos verificadores."""

    value: str  # somente digitos (11 chars)

    def __post_init__(self) -> None:
        digits = re.sub(r"\D", "", self.value)
        if len(digits) != 11:
            raise ValueError(f"CPF deve ter 11 digitos, recebeu {len(digits)}")
        if len(set(digits)) == 1:
            raise ValueError("CPF invalido (todos digitos iguais)")

        # Digito verificador 1
        s = sum(int(digits[i]) * (10 - i) for i in range(9))
        d1 = 11 - (s % 11)
        d1 = 0 if d1 >= 10 else d1
        if int(digits[9]) != d1:
            raise ValueError("CPF invalido (digito verificador 1)")

        # Digito verificador 2
        s = sum(int(digits[i]) * (11 - i) for i in range(10))
        d2 = 11 - (s % 11)
        d2 = 0 if d2 >= 10 else d2
        if int(digits[10]) != d2:
            raise ValueError("CPF invalido (digito verificador 2)")

        object.__setattr__(self, "value", digits)

    def __str__(self) -> str:
        v = self.value
        return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"


@dataclass(frozen=True)
class Email:
    """Email validado e normalizado para lowercase."""

    value: str

    def __post_init__(self) -> None:
        v = self.value.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError(f"Email invalido: {self.value}")
        object.__setattr__(self, "value", v)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Phone:
    """Telefone brasileiro (10-11 digitos)."""

    value: str  # somente digitos

    def __post_init__(self) -> None:
        digits = re.sub(r"\D", "", self.value)
        if len(digits) < 10 or len(digits) > 11:
            raise ValueError(f"Telefone deve ter 10-11 digitos, recebeu {len(digits)}")
        object.__setattr__(self, "value", digits)

    def __str__(self) -> str:
        v = self.value
        if len(v) == 11:
            return f"({v[:2]}) {v[2:7]}-{v[7:]}"
        return f"({v[:2]}) {v[2:6]}-{v[6:]}"


@dataclass(frozen=True)
class Money:
    """Valor monetario em centavos (evita float)."""

    amount: int  # centavos

    @classmethod
    def from_reais(cls, value: float) -> Money:
        return cls(amount=round(value * 100))

    @property
    def reais(self) -> float:
        return self.amount / 100

    @property
    def formatted(self) -> str:
        return f"R$ {self.reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(amount=self.amount + other.amount)

    def __sub__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        return Money(amount=self.amount - other.amount)

    def __mul__(self, factor: int) -> Money:
        if not isinstance(factor, int):
            return NotImplemented
        return Money(amount=self.amount * factor)

    def __str__(self) -> str:
        return self.formatted


# Dentes permanentes e deciduos (notacao FDI)
_PERMANENT = set()
for q in (10, 20, 30, 40):
    _PERMANENT.update(range(q + 1, q + 9))

_DECIDUOUS = set()
for q in (50, 60, 70, 80):
    _DECIDUOUS.update(range(q + 1, q + 6))

_VALID_TEETH = _PERMANENT | _DECIDUOUS


@dataclass(frozen=True)
class ToothNumber:
    """Numero do dente na notacao FDI (11-48 permanentes, 51-85 deciduos)."""

    value: int

    def __post_init__(self) -> None:
        if self.value not in _VALID_TEETH:
            raise ValueError(
                f"Numero de dente invalido: {self.value}. "
                "Use notacao FDI (11-48 permanentes, 51-85 deciduos)."
            )

    @property
    def is_deciduous(self) -> bool:
        return self.value in _DECIDUOUS

    @property
    def quadrant(self) -> int:
        return self.value // 10

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class CEP:
    """CEP brasileiro (8 digitos)."""

    value: str

    def __post_init__(self) -> None:
        digits = re.sub(r"\D", "", self.value)
        if len(digits) != 8:
            raise ValueError(f"CEP deve ter 8 digitos, recebeu {len(digits)}")
        object.__setattr__(self, "value", digits)

    def __str__(self) -> str:
        v = self.value
        return f"{v[:5]}-{v[5:]}"
