"""Secure, read-only IMAP client using BODY.PEEK[] to preserve unread status."""

import email
from email.header import decode_header
import imaplib
from typing import List, Optional

from app.config import Settings
from app.parser.schemas import RawEmail


def decode_mime_header(header_value: Optional[str]) -> str:
    """Safely decodes an encoded MIME header string into unicode text."""
    if not header_value:
        return ""
    decoded_fragments = decode_header(header_value)
    result = []
    for fragment, charset in decoded_fragments:
        if isinstance(fragment, bytes):
            result.append(fragment.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(str(fragment))
    return "".join(result)


class SafeImapClient:
    """Read-only IMAP connector ensuring zero state modifications to user inboxes."""

    def __init__(self, config: Settings):
        self.config = config

    def fetch_unread_newsletters(self) -> List[RawEmail]:
        """Connects over TLS, fetches unread newsletters with BODY.PEEK[], and preserves message flags."""
        if not self.config.imap_username or not self.config.imap_password:
            raise ValueError(
                "IMAP credentials missing. Provide IMAP_USERNAME and IMAP_PASSWORD in .env or run with --demo."
            )

        emails: List[RawEmail] = []
        mail = imaplib.IMAP4_SSL(self.config.imap_server, self.config.imap_port)

        try:
            mail.login(self.config.imap_username, self.config.imap_password)
            status, _ = mail.select(self.config.imap_folder, readonly=True)
            if status != "OK":
                raise ValueError(f"Could not open IMAP folder '{self.config.imap_folder}'")

            # Search unread messages
            status, search_data = mail.search(None, "UNSEEN")
            if status != "OK" or not search_data[0]:
                return emails

            message_ids = search_data[0].split()
            # Cap at max configured emails to prevent memory bloat
            fetch_ids = message_ids[-self.config.imap_max_emails:]

            for msg_id in fetch_ids:
                # CRITICAL: Use BODY.PEEK[] so \Seen flag is NEVER added to the email
                status, data = mail.fetch(msg_id, "(BODY.PEEK[])")
                if status != "OK" or not data:
                    continue

                raw_bytes = data[0][1]
                msg = email.message_from_bytes(raw_bytes)

                subject = decode_mime_header(msg.get("Subject", "(No Subject)"))
                sender = decode_mime_header(msg.get("From", "Unknown Sender"))
                date_str = msg.get("Date", "")

                # Extract HTML body
                html_body = ""
                text_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        payload = part.get_payload(decode=True)
                        if not payload:
                            continue
                        charset = part.get_content_charset() or "utf-8"
                        decoded_text = payload.decode(charset, errors="replace")
                        if content_type == "text/html" and not html_body:
                            html_body = decoded_text
                        elif content_type == "text/plain" and not text_body:
                            text_body = decoded_text
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        charset = msg.get_content_charset() or "utf-8"
                        decoded_text = payload.decode(charset, errors="replace")
                        if msg.get_content_type() == "text/html":
                            html_body = decoded_text
                        else:
                            text_body = decoded_text

                content = html_body if html_body else f"<html><body><pre>{text_body}</pre></body></html>"
                word_count = len((text_body or html_body).split())

                emails.append(
                    RawEmail(
                        id=f"imap-{msg_id.decode('ascii', errors='ignore')}",
                        source=sender,
                        subject=subject,
                        date=date_str,
                        raw_html=content,
                        raw_text=text_body or None,
                        raw_word_count=word_count,
                    )
                )

        finally:
            try:
                mail.close()
                mail.logout()
            except Exception:
                pass

        return emails
