"""Unit tests for the ingestion layer (LocalNewsletterLoader & SafeImapClient)."""

from unittest.mock import MagicMock, patch
import pytest

from app.config import Settings
from app.ingest.local_loader import LocalNewsletterLoader
from app.ingest.imap_client import SafeImapClient, decode_mime_header


def test_local_loader_loads_four_fixtures():
    loader = LocalNewsletterLoader()
    emails = loader.load_demo_newsletters()

    assert len(emails) == 4
    sources = {e.source for e in emails}
    assert "TLDR Tech" in sources
    assert "ByteByteGo" in sources
    assert "PyCoder's Weekly" in sources
    assert "Hacker Newsletter" in sources

    for email in emails:
        assert email.raw_word_count > 0
        assert len(email.raw_html) > 50
        assert email.subject != ""


def test_decode_mime_header():
    assert decode_mime_header("Simple Subject") == "Simple Subject"
    assert decode_mime_header(None) == ""


def test_safe_imap_client_requires_credentials():
    config = Settings(imap_username=None, imap_password=None)
    client = SafeImapClient(config)
    with pytest.raises(ValueError, match="IMAP credentials missing"):
        client.fetch_unread_newsletters()


@patch("imaplib.IMAP4_SSL")
def test_safe_imap_client_uses_body_peek(mock_imap_ssl):
    mock_mail = MagicMock()
    mock_imap_ssl.return_value = mock_mail
    mock_mail.select.return_value = ("OK", [b"1"])
    mock_mail.search.return_value = ("OK", [b"101"])
    
    # Mock single email payload with sample HTML
    raw_email_bytes = b"Subject: Test Newsletter\r\nFrom: test@example.com\r\nContent-Type: text/html\r\n\r\n<html><body><p>Hello World</p></body></html>"
    mock_mail.fetch.return_value = ("OK", [(b"101", raw_email_bytes)])

    config = Settings(imap_username="user@example.com", imap_password="secret-password")
    client = SafeImapClient(config)
    emails = client.fetch_unread_newsletters()

    assert len(emails) == 1
    assert emails[0].subject == "Test Newsletter"
    # CRITICAL: Verify BODY.PEEK[] was called to avoid altering \Seen flag
    mock_mail.fetch.assert_called_with(b"101", "(BODY.PEEK[])")
