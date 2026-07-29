"""
Tests para validar a lógica de autenticação com whitelist de e-mails
"""

import pytest


def test_email_normalization():
    """Testa se e-mails são normalizados corretamente (minúsculas + strip)"""
    admin_emails = ["Admin@Example.com", " user@example.com "]
    allowed_emails = ["User2@EXAMPLE.COM"]

    authorized_users = [
        email.strip().lower()
        for email in admin_emails + allowed_emails
        if email.strip()
    ]

    assert "admin@example.com" in authorized_users
    assert "user@example.com" in authorized_users
    assert "user2@example.com" in authorized_users
    assert len(authorized_users) == 3


def test_empty_emails_filtered():
    """Testa se e-mails vazios são filtrados"""
    admin_emails = ["admin@example.com", ""]
    allowed_emails = ["", "user@example.com", "   "]

    authorized_users = [
        email.strip().lower()
        for email in admin_emails + allowed_emails
        if email.strip()
    ]

    assert len(authorized_users) == 2
    assert "" not in authorized_users
    assert "   " not in list(authorized_users)


def test_email_parsing_from_string():
    """Testa parseamento de e-mails separados por vírgula"""
    admin_emails_str = "admin1@example.com,admin2@example.com"
    allowed_emails_str = "user1@example.com, user2@example.com"

    admin_list = admin_emails_str.split(",")
    allowed_list = allowed_emails_str.split(",")

    authorized_users = [
        email.strip().lower() for email in admin_list + allowed_list if email.strip()
    ]

    assert len(authorized_users) == 4
    assert "admin1@example.com" in authorized_users
    assert "user2@example.com" in authorized_users


def test_duplicate_emails():
    """Testa se e-mails duplicados são mantidos na lista (pode-se converter para set depois)"""
    admin_emails = ["admin@example.com"]
    allowed_emails = ["admin@example.com"]

    authorized_users = [
        email.strip().lower()
        for email in admin_emails + allowed_emails
        if email.strip()
    ]

    # Lista com duplicatas
    assert len(authorized_users) == 2
    assert authorized_users.count("admin@example.com") == 2

    # Set sem duplicatas
    authorized_users_set = set(authorized_users)
    assert len(authorized_users_set) == 1


def test_email_validation():
    """Testa lógica de validação de e-mail na whitelist"""
    authorized_users = ["admin@example.com", "user@example.com"]

    # Caso 1: E-mail válido
    test_email = "admin@example.com"
    assert test_email.strip().lower() in authorized_users

    # Caso 2: E-mail com espaços (deve ser normalizado)
    test_email = " ADMIN@EXAMPLE.COM "
    assert test_email.strip().lower() in authorized_users

    # Caso 3: E-mail não autorizado
    test_email = "unauthorized@example.com"
    assert test_email.strip().lower() not in authorized_users


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
