"""API Router: Communication (mensagens, templates, campanhas) endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_campaign_repo,
    get_current_user,
    get_message_repo,
    get_message_template_repo,
)
from odontoflow.api.schemas.communication import (
    CampaignResponse,
    CampaignsListResponse,
    CreateCampaignRequest,
    CreateTemplateRequest,
    MessageResponse,
    MessagesListResponse,
    SendMessageRequest,
    TemplateResponse,
    TemplatesListResponse,
)
from odontoflow.communication.application.commands.create_campaign import CreateCampaignCommand
from odontoflow.communication.application.commands.create_template import CreateTemplateCommand
from odontoflow.communication.application.commands.execute_campaign import ExecuteCampaignCommand
from odontoflow.communication.application.commands.send_message import SendMessageCommand
from odontoflow.communication.application.queries.list_campaigns import ListCampaignsQuery
from odontoflow.communication.application.queries.list_messages import ListMessagesQuery
from odontoflow.communication.application.queries.list_templates import ListTemplatesQuery
from odontoflow.communication.domain.models import (
    Campaign,
    CampaignStatus,
    Message,
    MessageChannel,
    MessageTemplate,
    MessageType,
)
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError

router = APIRouter(
    prefix="/api/v1",
    tags=["communication"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _template_to_response(t: MessageTemplate) -> TemplateResponse:
    return TemplateResponse(
        id=str(t.id),
        name=t.name,
        message_type=t.message_type.value,
        channel=t.channel.value,
        content=t.content,
        active=t.active,
        created_at=t.created_at.isoformat(),
    )


def _message_to_response(m: Message) -> MessageResponse:
    return MessageResponse(
        id=str(m.id),
        patient_id=str(m.patient_id),
        channel=m.channel.value,
        message_type=m.message_type.value,
        content=m.content,
        status=m.status.value,
        sent_at=m.sent_at.isoformat() if m.sent_at else None,
        delivered_at=m.delivered_at.isoformat() if m.delivered_at else None,
        error_message=m.error_message,
        campaign_id=str(m.campaign_id) if m.campaign_id else None,
        created_at=m.created_at.isoformat(),
    )


def _campaign_to_response(c: Campaign) -> CampaignResponse:
    return CampaignResponse(
        id=str(c.id),
        name=c.name,
        message_type=c.message_type.value,
        channel=c.channel.value,
        template_id=str(c.template_id),
        target_filter=c.target_filter,
        scheduled_at=c.scheduled_at.isoformat() if c.scheduled_at else None,
        messages_total=c.messages_total,
        messages_sent=c.messages_sent,
        messages_failed=c.messages_failed,
        status=c.status.value,
        created_at=c.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Message Templates
# ---------------------------------------------------------------------------


@router.post(
    "/message-templates",
    response_model=TemplateResponse,
    status_code=201,
)
async def create_template(
    req: CreateTemplateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_message_template_repo),
):
    """Cria template de mensagem."""
    cmd = CreateTemplateCommand(
        tenant_id=current_user.tenant_id,
        name=req.name,
        message_type=MessageType(req.message_type),
        channel=MessageChannel(req.channel),
        content=req.content,
    )
    try:
        template = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)
    return _template_to_response(template)


@router.get(
    "/message-templates",
    response_model=TemplatesListResponse,
)
async def list_templates(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_message_template_repo),
):
    """Lista templates de mensagem."""
    query = ListTemplatesQuery(tenant_id=current_user.tenant_id)
    templates = await query.execute(repo)
    return TemplatesListResponse(
        templates=[_template_to_response(t) for t in templates],
        total=len(templates),
    )


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


@router.post(
    "/messages/send",
    response_model=MessageResponse,
    status_code=201,
)
async def send_message(
    req: SendMessageRequest,
    current_user: CurrentUser = Depends(get_current_user),
    message_repo=Depends(get_message_repo),
    template_repo=Depends(get_message_template_repo),
):
    """Envia mensagem para paciente."""
    cmd = SendMessageCommand(
        tenant_id=current_user.tenant_id,
        patient_id=UUID(req.patient_id),
        channel=MessageChannel(req.channel),
        message_type=MessageType(req.message_type),
        content=req.content,
        template_id=UUID(req.template_id) if req.template_id else None,
        template_variables=req.template_variables,
    )
    try:
        message = await cmd.execute(message_repo, template_repo)
    except NotFoundError:
        raise HTTPException(404, "Template nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)
    return _message_to_response(message)


@router.get(
    "/messages",
    response_model=MessagesListResponse,
)
async def list_messages(
    patient_id: Optional[UUID] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_message_repo),
):
    """Lista historico de mensagens."""
    query = ListMessagesQuery(
        tenant_id=current_user.tenant_id,
        patient_id=patient_id,
    )
    messages = await query.execute(repo)
    return MessagesListResponse(
        messages=[_message_to_response(m) for m in messages],
        total=len(messages),
    )


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------


@router.post(
    "/campaigns",
    response_model=CampaignResponse,
    status_code=201,
)
async def create_campaign(
    req: CreateCampaignRequest,
    current_user: CurrentUser = Depends(get_current_user),
    campaign_repo=Depends(get_campaign_repo),
    template_repo=Depends(get_message_template_repo),
):
    """Cria campanha de mensagens."""
    cmd = CreateCampaignCommand(
        tenant_id=current_user.tenant_id,
        name=req.name,
        message_type=MessageType(req.message_type),
        channel=MessageChannel(req.channel),
        template_id=UUID(req.template_id),
        target_filter=req.target_filter,
        scheduled_at=datetime.fromisoformat(req.scheduled_at) if req.scheduled_at else None,
    )
    try:
        campaign = await cmd.execute(campaign_repo, template_repo)
    except NotFoundError:
        raise HTTPException(404, "Template nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)
    return _campaign_to_response(campaign)


@router.get(
    "/campaigns",
    response_model=CampaignsListResponse,
)
async def list_campaigns(
    status: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_campaign_repo),
):
    """Lista campanhas."""
    campaign_status = CampaignStatus(status) if status else None
    query = ListCampaignsQuery(
        tenant_id=current_user.tenant_id,
        status=campaign_status,
    )
    campaigns = await query.execute(repo)
    return CampaignsListResponse(
        campaigns=[_campaign_to_response(c) for c in campaigns],
        total=len(campaigns),
    )


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignResponse,
)
async def get_campaign(
    campaign_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_campaign_repo),
):
    """Obtem campanha por ID."""
    campaign = await repo.get_by_id(campaign_id)
    if not campaign or campaign.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Campanha nao encontrada")
    return _campaign_to_response(campaign)


@router.patch(
    "/campaigns/{campaign_id}/execute",
    response_model=CampaignResponse,
)
async def execute_campaign(
    campaign_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_campaign_repo),
):
    """Executa campanha de mensagens."""
    cmd = ExecuteCampaignCommand(campaign_id=campaign_id)
    try:
        campaign = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Campanha nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    if campaign.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Campanha nao encontrada")
    return _campaign_to_response(campaign)
