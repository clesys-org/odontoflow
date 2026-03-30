"""Unit tests — Website Builder application commands."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError
from odontoflow.website.application.commands.create_website import (
    CreateWebsiteCommand,
    ServiceItemInput,
)
from odontoflow.website.application.commands.toggle_publish import TogglePublishCommand
from odontoflow.website.application.commands.update_website import UpdateWebsiteCommand
from odontoflow.website.application.commands.update_website import (
    ServiceItemInput as UpdateServiceItemInput,
)
from odontoflow.website.application.queries.get_public_website import GetPublicWebsiteQuery
from odontoflow.website.application.queries.get_website import GetWebsiteQuery
from odontoflow.website.infrastructure.in_memory_website_repo import InMemoryWebsiteRepository


@pytest.fixture
def repo():
    return InMemoryWebsiteRepository()


class TestCreateWebsiteCommand:
    @pytest.mark.asyncio
    async def test_create_website(self, repo):
        cmd = CreateWebsiteCommand(
            tenant_id=uuid4(),
            clinic_name="Odonto Sorriso",
            slug="odonto-sorriso",
            tagline="Seu sorriso e nossa prioridade",
            phone="(11) 3333-4444",
            services=[
                ServiceItemInput(name="Clareamento", description="Laser"),
                ServiceItemInput(name="Ortodontia"),
            ],
        )
        website = await cmd.execute(repo)

        assert website.clinic_name == "Odonto Sorriso"
        assert website.slug == "odonto-sorriso"
        assert len(website.services) == 2
        assert website.published is False

        saved = await repo.get_by_id(website.id)
        assert saved is not None
        assert saved.id == website.id

    @pytest.mark.asyncio
    async def test_create_website_empty_name_raises(self, repo):
        cmd = CreateWebsiteCommand(
            tenant_id=uuid4(),
            clinic_name="",
            slug="test-slug",
        )
        with pytest.raises(ValidationError, match="Nome da clinica"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_create_website_empty_slug_raises(self, repo):
        cmd = CreateWebsiteCommand(
            tenant_id=uuid4(),
            clinic_name="Clinica",
            slug="",
        )
        with pytest.raises(ValidationError, match="Slug e obrigatorio"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_create_website_invalid_slug_raises(self, repo):
        cmd = CreateWebsiteCommand(
            tenant_id=uuid4(),
            clinic_name="Clinica",
            slug="Invalid Slug!",
        )
        with pytest.raises(ValidationError, match="letras minusculas"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_create_website_duplicate_tenant_raises(self, repo):
        tenant_id = uuid4()
        cmd1 = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica A",
            slug="clinica-a1",
        )
        await cmd1.execute(repo)

        cmd2 = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica B",
            slug="clinica-b1",
        )
        with pytest.raises(ConflictError, match="ja possui um site"):
            await cmd2.execute(repo)


class TestUpdateWebsiteCommand:
    @pytest.mark.asyncio
    async def test_update_website(self, repo):
        # Create first
        tenant_id = uuid4()
        create_cmd = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica",
            slug="clinica-01",
        )
        await create_cmd.execute(repo)

        # Update
        update_cmd = UpdateWebsiteCommand(
            tenant_id=tenant_id,
            tagline="Novo slogan",
            phone="(11) 9999-0000",
            services=[
                UpdateServiceItemInput(name="Implante", description="Implante dentario"),
            ],
        )
        website = await update_cmd.execute(repo)

        assert website.tagline == "Novo slogan"
        assert website.phone == "(11) 9999-0000"
        assert len(website.services) == 1
        assert website.services[0].name == "Implante"

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises(self, repo):
        cmd = UpdateWebsiteCommand(
            tenant_id=uuid4(),
            tagline="Novo",
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)


class TestTogglePublishCommand:
    @pytest.mark.asyncio
    async def test_toggle_publish_on(self, repo):
        tenant_id = uuid4()
        create_cmd = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica",
            slug="clinica-02",
        )
        await create_cmd.execute(repo)

        cmd = TogglePublishCommand(tenant_id=tenant_id)
        website = await cmd.execute(repo)
        assert website.published is True

    @pytest.mark.asyncio
    async def test_toggle_publish_off(self, repo):
        tenant_id = uuid4()
        create_cmd = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica",
            slug="clinica-03",
        )
        website = await create_cmd.execute(repo)

        # Publish then unpublish
        cmd = TogglePublishCommand(tenant_id=tenant_id)
        await cmd.execute(repo)  # on
        website = await cmd.execute(repo)  # off
        assert website.published is False

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_raises(self, repo):
        cmd = TogglePublishCommand(tenant_id=uuid4())
        with pytest.raises(NotFoundError):
            await cmd.execute(repo)


class TestGetWebsiteQuery:
    @pytest.mark.asyncio
    async def test_get_website(self, repo):
        tenant_id = uuid4()
        create_cmd = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica",
            slug="clinica-04",
        )
        created = await create_cmd.execute(repo)

        query = GetWebsiteQuery(tenant_id=tenant_id)
        website = await query.execute(repo)
        assert website.id == created.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self, repo):
        query = GetWebsiteQuery(tenant_id=uuid4())
        with pytest.raises(NotFoundError):
            await query.execute(repo)


class TestGetPublicWebsiteQuery:
    @pytest.mark.asyncio
    async def test_get_public_website(self, repo):
        tenant_id = uuid4()
        create_cmd = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica Publica",
            slug="clinica-pub",
        )
        await create_cmd.execute(repo)

        # Publish it
        toggle_cmd = TogglePublishCommand(tenant_id=tenant_id)
        await toggle_cmd.execute(repo)

        query = GetPublicWebsiteQuery(slug="clinica-pub")
        website = await query.execute(repo)
        assert website.clinic_name == "Clinica Publica"
        assert website.published is True

    @pytest.mark.asyncio
    async def test_get_unpublished_raises(self, repo):
        tenant_id = uuid4()
        create_cmd = CreateWebsiteCommand(
            tenant_id=tenant_id,
            clinic_name="Clinica",
            slug="clinica-unpub",
        )
        await create_cmd.execute(repo)

        query = GetPublicWebsiteQuery(slug="clinica-unpub")
        with pytest.raises(NotFoundError):
            await query.execute(repo)

    @pytest.mark.asyncio
    async def test_get_nonexistent_slug_raises(self, repo):
        query = GetPublicWebsiteQuery(slug="nao-existe")
        with pytest.raises(NotFoundError):
            await query.execute(repo)
