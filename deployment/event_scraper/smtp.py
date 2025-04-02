from smtplib import SMTP as _SMTP, SMTPException
from common import fread
from config import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from logging import getLogger

logger = getLogger(__name__)

class SMTP:

    @staticmethod
    def build_multipart_msg(subj_title: str, payload: str) -> MIMEMultipart: 
        message = MIMEMultipart()
        message['From'] = Header(config['smtp']['sender'], config['encoding'])
        message['To'] = Header(', '.join(config['smtp']['recipients']).strip(), config['encoding'])
        message['Subject'] = Header(subj_title, config['encoding'])
        message.attach(MIMEText(payload, config['smtp']['mime_type'], config['encoding']))
        return message
    

    @staticmethod
    def notify_email() -> int:

        hosts = [eh for eh in config['hostlist'] if eh and not str(eh).startswith(('#', '\n'))]
        if not hosts:
            raise ValueError("No hosts found. Please check your configuration.")
    
        if len(hosts) < 1:
            logger.error(f"Error: No event hosts found in list: {config['hostlist']}")
            return 1

        payload = '\n{}\n'.format(fread(config['logger']['log_file'], encoding=config['encoding']))
        subj_title = 'Latest events fetched: {}'.format(config['logger']['log_ts'])
        contents = 'Subject: {}\n\n{}'.format(subj_title, payload)

        try:
            with _SMTP(config['smtp']['server'], config['smtp']['port']) as server:
                server.starttls()

                if config['smtp'].get('sender') and config['smtp'].get('app_passkey'):
                    server.login(config['smtp']['sender'], config['smtp']['app_passkey'])
                    logger.debug('Successfuly logged in to SMTP server.')
                else:
                    logger.debug('Not using SMTP authentication.')

                server.sendmail(
                    config['smtp']['sender'], 
                    config['smtp']['recipients'], 
                    SMTP.build_multipart_msg(subj_title, contents).as_string()
                )
                logger.info(f"Notification sent to {len(config['smtp']['recipients'])} recipients.")

        except SMTPException as e:
            logger.error(f"{e.__class__.__name__} exception raised: {e.args[::-1]}")
            return 1 
        except Exception as e:
            logger.error(f"Unknown SMTP exception raised: {e.args[::-1]}")
            return 1 
        
        return 0