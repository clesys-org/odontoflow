"""Unit tests — Communication application commands."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.communication.application.commands.create_campaign import CreateCampaignCommand
from odontoflow.communication.application.commands.create_template import CreateTemplateCommand
from odontoflow.communication.application.commands.execute_campaign import ExecuteCampaignCommand
from odontoflow.communication.application.commands.send_message import SendMessageCommand
from odontoflow.communication.domain.models import (
    CampaignStatus,
    MessageChannel,
    MessageStatus,
    MessageType,
)
from odontoflow.communication.infrastructure.in_memory_communication_repo import (
    InMemoryCampaignRepository,
    InMemoryMessageRepository,
    InMemoryMessageTemplateRepository,
)


@pytest.fixture
def template_repo():
    return InMemoryMessageTemplateRepository()


@pytest.fixture
def message_repo():
    return InMemoryMessageRepository()


@pytest.fixture
def campaign_repo():
    return InMemoryCampaignRepository()


class TestCreateTemplateCommand:
    @pytest.mark.asyncio
    async def test_create_template(self, template_repo):
        cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="Lembrete Consulta",
            message_type=MessageType.APPOINTMENT_REMINDER,
            channel=MessageChannel.WHATSAPP,
            content="Ola {{patient_name}}, consulta dia {{date}}.",
        )
        template = await cmd.execute(template_repo)

        assert template.name == "Lembrete Consulta"
        assert template.message_type == MessageType.APPOINTMENT_REMINDER

        saved = await template_repo.get_by_id(template.id)
        assert saved is not None
        assert saved.id == template.id

    @pytest.mark.asyncio
    async def test_create_template_empty_name_raises(self, template_repo):
        cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="",
            content="Conteudo",
        )
        with pytest.raises(ValidationError, match="Nome do template"):
            await cmd.execute(template_repo)

    @pytest.mark.asyncio
    async def test_create_template_empty_content_raises(self, template_repo):
        cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="Lembrete",
            content="",
        )
        with pytest.raises(ValidationError, match="Conteudo do template"):
            await cmd.execute(template_repo)


class TestSendMessageCommand:
    @pytest.mark.asyncio
    async def test_send_direct_content(self, message_repo):
        cmd = SendMessageCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            channel=MessageChannel.WHATSAPP,
            message_type=MessageType.CUSTOM,
            content="Mensagem direta para paciente",
        )
        message = await cmd.execute(message_repo)

        assert message.status == MessageStatus.SENT
        assert message.content == "Mensagem direta para paciente"
        assert message.sent_at is not None

        saved = await message_repo.get_by_id(message.id)
        assert saved is not None

    @pytest.mark.asyncio
    async def test_send_from_template(self, message_repo, template_repo):
        # Create template first
        create_cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="Lembrete",
            message_type=MessageType.APPOINTMENT_REMINDER,
            channel=MessageChannel.WHATSAPP,
            content="Ola {{patient_name}}, consulta dia {{date}}.",
        )
        template = await create_cmd.execute(template_repo)

        # Send message using template
        send_cmd = SendMessageCommand(
            tenant_id=template.tenant_id,
            patient_id=uuid4(),
            channel=MessageChannel.WHATSAPP,
            message_type=MessageType.APPOINTMENT_REMINDER,
            template_id=template.id,
            template_variables={"patient_name": "Maria", "date": "15/03"},
        )
        message = await send_cmd.execute(message_repo, template_repo)

        assert message.status == MessageStatus.SENT
        assert "Maria" in message.content
        assert "15/03" in message.content

    @pytest.mark.asyncio
    async def test_send_template_not_found_raises(self, message_repo, template_repo):
        cmd = SendMessageCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            template_id=uuid4(),
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(message_repo, template_repo)

    @pytest.mark.asyncio
    async def test_send_empty_content_raises(self, message_repo):
        cmd = SendMessageCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            content="",
        )
        with pytest.raises(ValidationError, match="Conteudo da mensagem"):
            await cmd.execute(message_repo)


class TestCreateCampaignCommand:
    @pytest.mark.asyncio
    async def test_create_campaign(self, campaign_repo, template_repo):
        # Create template first
        template_cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="Recall",
            content="Hora do retorno, {{patient_name}}!",
        )
        template = await template_cmd.execute(template_repo)

        cmd = CreateCampaignCommand(
            tenant_id=template.tenant_id,
            name="Recall Semestral",
            message_type=MessageType.RECALL_CHECKUP,
            channel=MessageChannel.WHATSAPP,
            template_id=template.id,
            target_filter={"status": "active"},
        )
        campaign = await cmd.execute(campaign_repo, template_repo)

        assert campaign.name == "Recall Semestral"
        assert campaign.status == CampaignStatus.DRAFT

        saved = await campaign_repo.get_by_id(campaign.id)
        assert saved is not None

    @pytest.mark.asyncio
    async def test_create_campaign_template_not_found_raises(self, campaign_repo, template_repo):
        cmd = CreateCampaignCommand(
            tenant_id=uuid4(),
            name="Campanha",
            template_id=uuid4(),
        )
        with pytest.raises(NotFoundError):
            await cmd.execute(campaign_repo, template_repo)

    @pytest.mark.asyncio
    async def test_create_campaign_empty_name_raises(self, campaign_repo, template_repo):
        template_cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="T",
            content="C",
        )
        template = await template_cmd.execute(template_repo)

        cmd = CreateCampaignCommand(
            tenant_id=template.tenant_id,
            name="",
            template_id=template.id,
        )
        with pytest.raises(ValidationError, match="Nome da campanha"):
            await cmd.execute(campaign_repo, template_repo)


class TestExecuteCampaignCommand:
    @pytest.mark.asyncio
    async def test_execute_campaign(self, campaign_repo, template_repo):
        # Create template + campaign
        template_cmd = CreateTemplateCommand(
            tenant_id=uuid4(),
            name="T",
            content="C",
        )
        template = await template_cmd.execute(template_repo)

        campaign_cmd = CreateCampaignCommand(
            tenant_id=template.tenant_id,
            name="Campanha",
            template_id=template.id,
        )
        campaign = await campaign_cmd.execute(campaign_repo, template_repo)

        # Execute
        exec_cmd = ExecuteCampaignCommand(campaign_id=campaign.id)
        result = await exec_cmd.execute(campaign_repo)

        assert result.status == CampaignStatus.RUNNING

    @pytest.mark.asyncio
    async def test_execute_nonexistent_raises(self, campaign_repo):
        cmd = ExecuteCampaignCommand(campaign_id=uuid4())
        with pytest.raises(NotFoundError):
            await cmd.execute(campaign_repo)
