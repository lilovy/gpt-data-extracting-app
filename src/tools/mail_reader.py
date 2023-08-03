import imaplib
import email
import re
from time import sleep


class MailCriteria:
    ALL = 'ALL'
    UNSEEN = 'UNSEEN'
    SEEN = 'SEEN'
    RECENT = 'RECENT'
    FLAGGED = 'FLAGGED'
    UNFLAGGED = 'UNFLAGGED'
    ANSWERED = 'ANSWERED'
    UNANSWERED = 'UNANSWERED'
    DRAFT = 'DRAFT'
    UNDRAFT = 'UNDRAFT'


class EmailReader:
    def __init__(self, client: str, email_address: str, password: str, delay: int = 0):
        self.client = client
        self.email_address = email_address
        self.password = password
        self.mail = None
        self.delay = delay

    def __enter__(self):
        sleep(self.delay)
        # Connect to the IMAP server
        self.mail = imaplib.IMAP4_SSL(self.client)

        # Log in to the email account
        self.mail.login(self.email_address, self.password)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log out of the email account
        self.mail.logout()

    def get_latest_email_body(self, sender_email: str=None, criteria: MailCriteria = MailCriteria.ALL):
        # Select the inbox folder
        self.mail.select("inbox")

        # Search for the latest email matching the criteria from the specified sender email
        search_query = f'({criteria})'
        if sender_email:
            search_query += f' (FROM "{sender_email}")'

        status, email_ids = self.mail.search(None, search_query)

        if email_ids[0]:
            latest_email_id = email_ids[0].split()[-1]

            # Get the body of the latest email
            status, message_data = self.mail.fetch(latest_email_id, "(RFC822)")

            # Parse the email content
            for response in message_data:
                if isinstance(response, tuple):
                    # Decode the message from bytes to email.Message object
                    msg = email.message_from_bytes(response[1])

                    # Get the body of the email
                    if msg.is_multipart():
                        # If the email has multiple parts, get the body of the first part
                        body = msg.get_payload(0).get_payload(decode=True)
                    else:
                        # Otherwise, get the body of the email
                        body = msg.get_payload(decode=True)

                    # Return the body of the email
                    return body.decode()

        # No matching email found
        return None
    
    def get_code_from_email(self, sender_email: str=None, criteria: MailCriteria = MailCriteria.ALL):
        # Select the inbox folder
        self.mail.select("inbox")

        # Search for the latest email from the specified sender email
        search_query = f'({criteria})'
        if sender_email:
            search_query += f' (FROM "{sender_email}")'

        status, email_ids = self.mail.search(None, search_query)

        if email_ids[0]:
            latest_email_id = email_ids[0].split()[-1]

            # Get the body of the latest email
            status, message_data = self.mail.fetch(latest_email_id, "(RFC822)")

            # Parse the email content
            for response in message_data:
                if isinstance(response, tuple):
                    # Decode the message from bytes to email.Message object
                    msg = email.message_from_bytes(response[1])

                    # Get the body of the email
                    if msg.is_multipart():
                        # If the email has multiple parts, get the body of the first part
                        body = msg.get_payload(0).get_payload(decode=True)
                    else:
                        # Otherwise, get the body of the email
                        body = msg.get_payload(decode=True)

                    # Extract the code from the email body using regular expressions
                    code_regex = r"\d{7}"  # 6-digit code
                    code_match = re.search(code_regex, body.decode())

                    # Return the code if found
                    if code_match:
                        return code_match.group()

        # No email found or no code found in the email body
        return None


def get_code(email: str, password, delay: int = 0):
    with EmailReader(
        client="imap.rambler.ru",
        email_address=email,
        password=password,
        delay=delay,
        ) as reader:

        msg = reader.get_code_from_email(
            sender_email="account-security-noreply@accountprotection.microsoft.com",
            criteria=MailCriteria.UNSEEN,
        )

        if msg: return msg

        return


if __name__ == "__main__":
    with EmailReader(
        client="imap.rambler.ru", 
        email_address="mail@rambler.ru", 
        password="password",
        ) as reader:
        body = reader.get_code_from_email(
            sender_email="account-security-noreply@accountprotection.microsoft.com",
            )
        if body:
            print(body)
        else:
            print("No matching email found")
