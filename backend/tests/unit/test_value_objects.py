"""Testes dos Value Objects do shared kernel."""

import pytest

from odontoflow.shared.domain.value_objects import CEP, CPF, Email, Money, Phone, ToothNumber


class TestCPF:
    def test_valid_cpf(self):
        cpf = CPF("529.982.247-25")
        assert cpf.value == "52998224725"
        assert str(cpf) == "529.982.247-25"

    def test_valid_cpf_digits_only(self):
        cpf = CPF("52998224725")
        assert cpf.value == "52998224725"

    def test_invalid_cpf_wrong_length(self):
        with pytest.raises(ValueError, match="11 digitos"):
            CPF("123")

    def test_invalid_cpf_all_same(self):
        with pytest.raises(ValueError, match="invalido"):
            CPF("11111111111")

    def test_invalid_cpf_check_digit(self):
        with pytest.raises(ValueError, match="digito verificador"):
            CPF("52998224726")


class TestEmail:
    def test_valid_email(self):
        email = Email("User@Example.COM")
        assert email.value == "user@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValueError, match="invalido"):
            Email("not-an-email")


class TestPhone:
    def test_valid_mobile(self):
        phone = Phone("(11) 97030-2337")
        assert phone.value == "11970302337"
        assert str(phone) == "(11) 97030-2337"

    def test_valid_landline(self):
        phone = Phone("1133334444")
        assert len(phone.value) == 10

    def test_invalid_phone(self):
        with pytest.raises(ValueError, match="10-11 digitos"):
            Phone("123")


class TestMoney:
    def test_from_reais(self):
        m = Money.from_reais(125.50)
        assert m.amount == 12550
        assert m.reais == 125.50

    def test_add(self):
        a = Money(1000)
        b = Money(2500)
        assert (a + b).amount == 3500

    def test_sub(self):
        assert (Money(5000) - Money(1500)).amount == 3500

    def test_mul(self):
        assert (Money(1000) * 3).amount == 3000

    def test_formatted(self):
        m = Money(125050)
        assert "1.250,50" in m.formatted


class TestToothNumber:
    def test_valid_permanent(self):
        t = ToothNumber(11)
        assert t.value == 11
        assert not t.is_deciduous
        assert t.quadrant == 1

    def test_valid_deciduous(self):
        t = ToothNumber(51)
        assert t.is_deciduous

    def test_invalid_tooth(self):
        with pytest.raises(ValueError, match="invalido"):
            ToothNumber(99)

    def test_all_quadrants(self):
        for num in [11, 21, 31, 41, 51, 61, 71, 81]:
            ToothNumber(num)  # Should not raise


class TestCEP:
    def test_valid_cep(self):
        cep = CEP("01234-567")
        assert cep.value == "01234567"
        assert str(cep) == "01234-567"

    def test_invalid_cep(self):
        with pytest.raises(ValueError, match="8 digitos"):
            CEP("123")
