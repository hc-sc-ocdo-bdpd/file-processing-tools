import extract_msg
import re
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class MsgFileProcessor(FileProcessorStrategy):
    """
    Processor for Outlook MSG files, building a strictly linear thread:
      oldest -> next -> ... -> newest
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        if not open_file:
            logger.debug(f"MSG file '{self.file_path}' was not opened (open_file=False).")
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def split_email_thread(self, body_text: str) -> list[str]:
        pattern = r"(?m)^(?=From:\s)"
        parts = re.split(pattern, body_text or "")
        return [p.strip() for p in parts if p.strip()]

    def parse_email_block(self, block_text: str) -> dict | None:
        from_match = re.search(r"(?im)^From:\s*(.*)$", block_text)
        if not from_match:
            return None

        sender = from_match.group(1).strip()
        sent_match = re.search(r"(?im)^Sent(?: on)?:\s*(.*)$", block_text)
        timestamp = sent_match.group(1).strip() if sent_match else None
        if not timestamp:
            date_match = re.search(r"(?im)^Date:\s*(.*)$", block_text)
            timestamp = date_match.group(1).strip() if date_match else None

        to_match = re.search(r"(?im)^To:\s*(.*)$", block_text)
        recipients_raw = to_match.group(1).strip() if to_match else ""
        recipients = [r.strip() for r in re.split(r"[;,]", recipients_raw) if r.strip()] if recipients_raw else []

        subject_match = re.search(r"(?im)^Subject:\s*(.*)$", block_text)
        subject = subject_match.group(1).strip() if subject_match else None

        pattern_remove = r"(?im)^(From|Sent(?: on)?|Date|To|Subject):.*?$"
        cleaned_body = re.sub(pattern_remove, "", block_text).strip()

        return {
            "subject": subject,
            "sender": sender,
            "recipients": recipients,
            "timestamp": timestamp,
            "body": cleaned_body,
            "reply": None
        }

    def build_linear_chain(self, emails: list[dict]) -> dict | None:
        if not emails:
            return None
        head = emails[0]
        current = head
        for nxt in emails[1:]:
            current["reply"] = nxt
            current = nxt
        return head

    def parse_msg(self) -> dict:
        msg = extract_msg.Message(self.file_path)
        raw_body = msg.body or ""
        blocks = self.split_email_thread(raw_body)
        if not blocks:
            only_node = {
                "subject": msg.subject,
                "sender": msg.sender,
                "recipients": [r.strip() for r in msg.to.split(";")] if msg.to else [],
                "timestamp": msg.date.isoformat() if msg.date else None,
                "body": raw_body,
                "reply": None
            }
            msg.close()
            return only_node

        reversed_blocks = list(reversed(blocks))
        parsed_emails = []
        leftover_chunks = []

        for blk in reversed_blocks:
            parsed = self.parse_email_block(blk)
            if parsed:
                parsed_emails.append(parsed)
            else:
                leftover_chunks.append(blk)

        chain_head = self.build_linear_chain(parsed_emails)
        leftover_body = "\n\n".join(leftover_chunks).strip()
        main_node = {
            "subject": msg.subject,
            "sender": msg.sender,
            "recipients": [r.strip() for r in msg.to.split(";")] if msg.to else [],
            "timestamp": msg.date.isoformat() if msg.date else None,
            "body": leftover_body or "",
            "reply": None
        }

        if chain_head:
            current = chain_head
            while current["reply"] is not None:
                current = current["reply"]
            current["reply"] = main_node
            final_thread = chain_head
        else:
            final_thread = main_node

        msg.close()
        return final_thread

    def process(self) -> None:
        logger.info(f"Starting processing of MSG file '{self.file_path}'.")
        if not self.open_file:
            logger.debug(f"MSG file '{self.file_path}' was not opened (open_file=False).")
            return

        try:
            msg = extract_msg.Message(self.file_path)
            logger.debug(f"Detected encoding 'utf-8' for MSG file '{self.file_path}'.")
            self.metadata["text"] = msg.body
            self.metadata["subject"] = msg.subject
            self.metadata["date"] = msg.date
            self.metadata["sender"] = msg.sender
            self.metadata["recipients"] = [r.email for r in msg.recipients if r.email]
            msg.close()
            self.metadata["thread"] = self.parse_msg()
            logger.info(f"Successfully processed MSG file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process MSG file '{self.file_path}': {e}")
            raise FileProcessingFailedError(f"Error encountered while processing: {e}")

    def save(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        logger.info(f"Saving MSG file '{self.file_path}' to '{save_path}'.")
        try:
            msg_file = extract_msg.Message(self.file_path)
            msg_file.export(path=save_path)
            msg_file.close()
            logger.info(f"MSG file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save MSG file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(f"Error encountered while saving: {e}")
