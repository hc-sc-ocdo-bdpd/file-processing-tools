from file_processor_strategy import FileProcessorStrategy
from libratom.lib.pff import PffArchive
import shutil
from errors import FileProcessingFailedError

class PstFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}

    def process(self) -> None:
        try:
            pst_file = PffArchive(self.file_path)
            root_folder = pst_file.root_folder
            num_folders, num_messages, folder_names, message_subjects, sender_addresses, recipient_addresses, message_bodies, message_attachments, message_dates = self.get_metadata(root_folder)

            self.metadata.update({
                'num_folders': num_folders,
                'num_messages': num_messages,
                'folder_names': folder_names,
                'message_subjects': message_subjects,
                'sender_addresses': sender_addresses,
                'recipient_addresses': recipient_addresses,
                'message_bodies': message_bodies,
                'message_attachments': message_attachments,
                'message_dates': message_dates
            })

            pst_file.close()
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")

    def get_metadata(self, folder) -> list:
        num_folders = 1
        num_messages = len(folder.sub_messages)
        folder_names = [folder.name]
        message_subjects = [message.subject for message in folder.sub_messages]
        sender_addresses = [message.sender.email_address for message in folder.sub_messages]
        recipient_addresses = [recipient.email_address for message in folder.sub_messages for recipient in message.recipients]
        message_bodies = [message.body for message in folder.sub_messages]
        message_attachments = [attachment.long_filename for message in folder.sub_messages for attachment in message.attachments]
        message_dates = [message.client_submit_time for message in folder.sub_messages]

        for sub_folder in folder.sub_folders:
            sub_num_folders, sub_num_messages, sub_folder_names, sub_message_subjects, sub_sender_addresses, sub_recipient_addresses, sub_message_bodies, sub_message_attachments, sub_message_dates = self.get_metadata(sub_folder)
            num_folders += sub_num_folders
            num_messages += sub_num_messages
            folder_names += sub_folder_names
            message_subjects += sub_message_subjects
            sender_addresses += sub_sender_addresses
            recipient_addresses += sub_recipient_addresses
            message_bodies += sub_message_bodies
            message_attachments += sub_message_attachments
            message_dates += sub_message_dates

        return num_folders, num_messages, folder_names, message_subjects, sender_addresses, recipient_addresses, message_bodies, message_attachments, message_dates
    
    def save(self, output_path: str = None) -> None:
        try:
            save_path = output_path or self.file_path
            shutil.copyfile(self.file_path, save_path)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving file {self.file_path} to {save_path}: {e}")
