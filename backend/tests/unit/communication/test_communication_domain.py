"""Unit tests — Communication domain models."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import ValidationError
from odontoflow.communication.domain.models import (
    Campaign,
    CampaignStatus,
    Message,
    MessageChannel,
    MessageStatus,
    MessageTemplate,
    MessageType,
)


class TestMessageTemplate:
    def test_create_template(self):
        template = MessageTemplate(
            tenant_id=uuid4(),
            name="Lembrete Consulta",
            message_type=MessageType.APPOINTMENT_REMINDER,
            channel=MessageChannel.WHATSAPP,
            content="Ola {{patient_name}}, sua consulta e dia {{date}} as {{time}}.",
        )
        assert template.name == "Lembrete Consulta"
        assert template.message_type == MessageType.APPOINTMENT_REMINDER
        assert template.channel == MessageChannel.WHATSAPP
        assert template.active is True

    def test_render_template(self):
        template = MessageTemplate(
            tenant_id=uuid4(),
            name="Lembrete",
            content="Ola {{patient_name}}, consulta dia {{date}} as {{time}}.",
        )
        rendered = template.render({
            "patient_name": "Maria",
            "date": "15/03/2026",
            "time": "14:00",
        })
        assert rendered == "Ola Maria, consulta dia 15/03/2026 as 14:00."

    def test_render_template_missing_variable(self):
        template = MessageTemplate(
            tenant_id=uuid4(),
            name="Lembrete",
            content="Ola {{patient_name}}, consulta dia {{date}}.",
        )
        rendered = template.render({"patient_name": "Joao"})
        assert "{{date}}" in rendered
        assert "Joao" in rendered

    def test_deactivate(self):
        template = MessageTemplate(tenant_id=uuid4(), name="T")
        template.deactivate()
        assert template.active is False

    def test_activate(self):
        template = MessageTemplate(tenant_id=uuid4(), name="T", active=False)
        template.activate()
        assert template.active is True


class TestMessage:
    def _make_message(self, **kwargs) -> Message:
        defaults = dict(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            channel=MessageChannel.WHATSAPP,
            message_type=MessageType.APPOINTMENT_REMINDER,
            content="Ola, lembrete de consulta amanha.",
        )
        defaults.update(kwargs)
        return Message(**defaults)

    # --- Send ---

    def test_send(self):
        msg = self._make_message()
        msg.send()
        assert msg.status == MessageStatus.SENT
        assert msg.sent_at is not None

    def test_send_empty_content_raises(self):
        msg = self._make_message(content="")
        with pytest.raises(ValidationError, match="Conteudo da mensagem"):
            msg.send()

    def test_send_not_pending_raises(self):
        msg = self._make_message(status=MessageStatus.SENT)
        with pytest.raises(ValidationError, match="nao pode ser enviada"):
            msg.send()

    # --- Mark delivered ---

    def test_mark_delivered(self):
        msg = self._make_message()
        msg.send()
        msg.mark_delivered()
        assert msg.status == MessageStatus.DELIVERED
        assert msg.delivered_at is not None

    def test_mark_delivered_not_sent_raises(self):
        msg = self._make_message()
        with pytest.raises(ValidationError, match="precisa estar SENT"):
            msg.mark_delivered()

    # --- Mark failed ---

    def test_mark_failed(self):
        msg = self._make_message()
        msg.mark_failed("Numero invalido")
        assert msg.status == MessageStatus.FAILED
        assert msg.error_message == "Numero invalido"

    def test_mark_failed_empty_error_raises(self):
        msg = self._make_message()
        with pytest.raises(ValidationError, match="Mensagem de erro"):
            msg.mark_failed("")

    # --- Full lifecycle ---

    def test_full_lifecycle_pending_to_delivered(self):
        msg = self._make_message()
        assert msg.status == MessageStatus.PENDING
        msg.send()
        assert msg.status == MessageStatus.SENT
        msg.mark_delivered()
        assert msg.status == MessageStatus.DELIVERED

    def test_full_lifecycle_pending_to_failed(self):
        msg = self._make_message()
        msg.mark_failed("Timeout na API")
        assert msg.status == MessageStatus.FAILED


class TestCampaign:
    def _make_campaign(self, **kwargs) -> Campaign:
        defaults = dict(
            tenant_id=uuid4(),
            name="Recall Semestral",
            message_type=MessageType.RECALL_CHECKUP,
            channel=MessageChannel.WHATSAPP,
            template_id=uuid4(),
            target_filter={"status": "active"},
        )
        defaults.update(kwargs)
        return Campaign(**defaults)

    # --- Schedule ---

    def test_schedule(self):
        from datetime import datetime, timezone

        campaign = self._make_campaign()
        dt = datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)
        campaign.schedule(dt)
        assert campaign.status == CampaignStatus.SCHEDULED
        assert campaign.scheduled_at == dt

    def test_schedule_not_draft_raises(self):
        from datetime import datetime, timezone

        campaign = self._make_campaign(status=CampaignStatus.RUNNING)
        with pytest.raises(ValidationError, match="precisa estar DRAFT"):
            campaign.schedule(datetime(2026, 4, 1, tzinfo=timezone.utc))

    # --- Execute ---

    def test_execute_from_draft(self):
        campaign = self._make_campaign()
        campaign.execute()
        assert campaign.status == CampaignStatus.RUNNING

    def test_execute_from_scheduled(self):
        campaign = self._make_campaign(status=CampaignStatus.SCHEDULED)
        campaign.execute()
        assert campaign.status == CampaignStatus.RUNNING

    def test_execute_completed_raises(self):
        campaign = self._make_campaign(status=CampaignStatus.COMPLETED)
        with pytest.raises(ValidationError, match="nao pode ser executada"):
            campaign.execute()

    # --- Record sent/failed ---

    def test_record_sent(self):
        campaign = self._make_campaign()
        campaign.record_sent()
        campaign.record_sent()
        assert campaign.messages_sent == 2

    def test_record_failed(self):
        campaign = self._make_campaign()
        campaign.record_failed()
        assert campaign.messages_failed == 1

    # --- Complete ---

    def test_complete(self):
        campaign = self._make_campaign(status=CampaignStatus.RUNNING)
        campaign.complete()
        assert campaign.status == CampaignStatus.COMPLETED

    def test_complete_not_running_raises(self):
        campaign = self._make_campaign()
        with pytest.raises(ValidationError, match="precisa estar RUNNING"):
            campaign.complete()

    # --- Cancel ---

    def test_cancel(self):
        campaign = self._make_campaign()
        campaign.cancel()
        assert campaign.status == CampaignStatus.CANCELLED

    def test_cancel_completed_raises(self):
        campaign = self._make_campaign(status=CampaignStatus.COMPLETED)
        with pytest.raises(ValidationError, match="nao pode ser cancelada"):
            campaign.cancel()

    def test_cancel_already_cancelled_raises(self):
        campaign = self._make_campaign(status=CampaignStatus.CANCELLED)
        with pytest.raises(ValidationError, match="nao pode ser cancelada"):
            campaign.cancel()

    # --- Full flow ---

    def test_full_flow_draft_to_completed(self):
        campaign = self._make_campaign()
        campaign.execute()
        campaign.record_sent()
        campaign.record_sent()
        campaign.record_failed()
        campaign.complete()
        assert campaign.status == CampaignStatus.COMPLETED
        assert campaign.messages_sent == 2
        assert campaign.messages_failed == 1
