"""Gateway para ViaCEP — auto-preenchimento de endereco por CEP."""
from __future__ import annotations

import httpx

from odontoflow.patient.domain.models import Address


class ViaCEPGateway:
    async def fetch_address(self, cep: str) -> Address | None:
        cep_digits = cep.replace("-", "").replace(".", "").strip()
        if len(cep_digits) != 8:
            return None
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"https://viacep.com.br/ws/{cep_digits}/json/")
                if resp.status_code != 200:
                    return None
                data = resp.json()
                if data.get("erro"):
                    return None
                return Address(
                    street=data.get("logradouro", ""),
                    neighborhood=data.get("bairro", ""),
                    city=data.get("localidade", ""),
                    state=data.get("uf", ""),
                    zip_code=cep_digits,
                )
        except Exception:
            return None
