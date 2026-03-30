"""Unit tests — Website Builder domain models."""
from __future__ import annotations

import pytest
from uuid import uuid4

from odontoflow.shared.domain.errors import ValidationError
from odontoflow.website.domain.models import (
    BookingWidget,
    ClinicWebsite,
    ServiceItem,
)


class TestServiceItem:
    def test_create_frozen_vo(self):
        item = ServiceItem(
            name="Clareamento",
            description="Clareamento dental a laser",
            icon="sparkles",
        )
        assert item.name == "Clareamento"
        assert item.description == "Clareamento dental a laser"
        assert item.icon == "sparkles"

    def test_frozen_immutability(self):
        item = ServiceItem(name="Ortodontia")
        with pytest.raises(AttributeError):
            item.name = "changed"


class TestClinicWebsite:
    def _make_website(self, **kwargs) -> ClinicWebsite:
        defaults = dict(
            tenant_id=uuid4(),
            clinic_name="Odonto Sorriso",
            slug="odonto-sorriso",
        )
        defaults.update(kwargs)
        return ClinicWebsite(**defaults)

    # --- Publish ---

    def test_publish(self):
        website = self._make_website()
        website.publish()
        assert website.published is True

    def test_publish_no_name_raises(self):
        website = self._make_website(clinic_name="")
        with pytest.raises(ValidationError, match="Nome da clinica"):
            website.publish()

    def test_publish_no_slug_raises(self):
        website = self._make_website(slug="")
        with pytest.raises(ValidationError, match="Slug e obrigatorio"):
            website.publish()

    # --- Unpublish ---

    def test_unpublish(self):
        website = self._make_website(published=True)
        website.unpublish()
        assert website.published is False

    # --- Toggle publish ---

    def test_toggle_publish_on(self):
        website = self._make_website()
        assert website.published is False
        website.toggle_publish()
        assert website.published is True

    def test_toggle_publish_off(self):
        website = self._make_website(published=True)
        website.toggle_publish()
        assert website.published is False

    # --- Update info ---

    def test_update_info(self):
        website = self._make_website()
        old_updated = website.updated_at

        website.update_info(
            tagline="Seu sorriso e nossa prioridade",
            phone="(11) 3333-4444",
            primary_color="#1e40af",
        )
        assert website.tagline == "Seu sorriso e nossa prioridade"
        assert website.phone == "(11) 3333-4444"
        assert website.primary_color == "#1e40af"
        assert website.updated_at >= old_updated

    def test_update_info_empty_name_raises(self):
        website = self._make_website()
        with pytest.raises(ValidationError, match="Nome da clinica nao pode ser vazio"):
            website.update_info(clinic_name="  ")

    def test_update_info_partial(self):
        website = self._make_website()
        original_name = website.clinic_name
        website.update_info(phone="(11) 9999-0000")
        assert website.clinic_name == original_name
        assert website.phone == "(11) 9999-0000"

    # --- Services ---

    def test_set_services(self):
        website = self._make_website()
        services = [
            ServiceItem(name="Clareamento", description="Laser", icon="sparkles"),
            ServiceItem(name="Ortodontia", description="Aparelho", icon="braces"),
        ]
        website.set_services(services)
        assert len(website.services) == 2
        assert website.services[0].name == "Clareamento"
        assert website.services[1].name == "Ortodontia"

    def test_set_services_empty(self):
        website = self._make_website(
            services=[ServiceItem(name="Limpeza")]
        )
        website.set_services([])
        assert len(website.services) == 0

    # --- Default values ---

    def test_default_values(self):
        website = self._make_website()
        assert website.primary_color == "#0d9488"
        assert website.booking_enabled is True
        assert website.published is False
        assert website.services == []
        assert website.social_links == {}


class TestBookingWidget:
    def test_create_widget(self):
        widget = BookingWidget(
            tenant_id=uuid4(),
            website_id=uuid4(),
        )
        assert widget.available_types == ["consulta", "avaliacao"]
        assert widget.max_days_ahead == 30
        assert widget.require_phone is True
        assert widget.active is True

    def test_deactivate(self):
        widget = BookingWidget(tenant_id=uuid4(), website_id=uuid4())
        widget.deactivate()
        assert widget.active is False

    def test_activate(self):
        widget = BookingWidget(
            tenant_id=uuid4(),
            website_id=uuid4(),
            active=False,
        )
        widget.activate()
        assert widget.active is True
