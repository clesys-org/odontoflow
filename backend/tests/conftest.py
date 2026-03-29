"""Fixtures compartilhadas para testes do OdontoFlow."""

from __future__ import annotations

import os

# Garante que nao usa credenciais reais em testes
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-tests-only")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
