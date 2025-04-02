from common import fread, get_random_user_agent
from datetime import datetime
from io import TextIOWrapper
import logging
from os import chdir, access, W_OK
from pathlib import Path
from platform import system
from selenium.webdriver.common.by import By
from shutil import which
from sys import stdout


auth_dir = Path('/app/.auth')
smtp = fread(Path(f'{auth_dir}/.smtp.txt')).split('\n')

if len(smtp) < 2:
    raise ValueError("SMTP configuration is incomplete. Need both host and user details.")

smtp_host = smtp[0].split(':') if smtp[0] else []
smtp_user = smtp[1].split(':') if smtp[1] else []

if not smtp_host or len(smtp_host) != 2:
    raise ValueError("SMTP host must be in format 'host:port'")
if not smtp_user or len(smtp_user) != 2:
    raise ValueError("SMTP user must be in format 'username:password'")

hosts_path = Path(auth_dir) / '.hosts.txt'
if not hosts_path.exists():
    raise FileNotFoundError(f"Hosts file not found: {hosts_path}")

recipients_path = Path(auth_dir) / '.recipients.txt'
if not recipients_path.exists():
    raise FileNotFoundError(f"Recipients file not found: {recipients_path}")

# Windows/Linux platform compatibility
if system() == "Windows":
    chrome_app_path = Path('C:\\Program Files\\Google\\Chrome\\Application')
    firefox_app_path = Path('C:\\Program Files\\Mozilla Firefox')
    BINARY_NAME = Path('chrome.exe') if which('chrome.exe') else \
                  Path('firefox.exe')
    BROWSER_BINARY_PATH = which(BINARY_NAME)
    chdir(chrome_app_path) if 'chrome.exe' in BINARY_NAME else \
    chdir(firefox_app_path)
else:
    BINARY_NAME = Path('google-chrome') if which('google-chrome') else \
                  Path('chromium-browser') if which('chromium-browser') else \
                  Path('firefox')
    BROWSER_BINARY_PATH = which(BINARY_NAME)


LOG_LEVEL = logging.INFO

# Default timeout for waiting for elements and pages to load
WAIT_TIMEOUT = 5
# Maximum number of login attempts before returning exception
LOGIN_ATTEMPTS = 3
# CLASS_NUM_INDICATOR: exactly 14 classes in the class attribute list indicates an event container
CLASS_NUM_INDICATOR = 14

COMMON = {
    'host': 'facebook.com',
    'scheme': 'https',
    'url_placeholder': '<event_host_name>',
    'user_agent': get_random_user_agent(),
}

config = {
    'encoding': 'utf-8',
    'logger': {
        'format': '%(message)s',
        'level': LOG_LEVEL,
        'log_ts': datetime.now().strftime('%Y-%m-%d-%H-%M')
    },
    'smtp': {
        'server': smtp_host[0],
        'port': smtp_host[1],
        'sender': smtp_user[0],
        'app_passkey': smtp_user[1],
        'recipients': fread(recipients_path).split('\n'),
        'mime_type': 'plain',
    },
    'hostlist': fread(hosts_path).split('\n'),
    'event_url': f'https://{COMMON["host"]}/{COMMON["url_placeholder"]}/upcoming_hosted_events',
    'cookies_popup_selector': (By.XPATH, "//span[text()='Decline optional cookies']"),
    'login_popup_selector': (By.XPATH, "//div[contains(@aria-label, 'Close')]"),
    'event_container_selector': (By.XPATH, "//div[.//img and .//a and .//span]"),
    'href_selector': (By.XPATH, ".//a[@href]"),
}

log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)
if not access(log_dir, W_OK):
    raise PermissionError(f"Log directory is not writable: {log_dir}")

config['logger']['log_file'] = log_dir / f"{config['logger']['log_ts']}-events.log"

logging.basicConfig(
    level=config['logger']['level'],
    format=config['logger']['format'],
    handlers=[
        logging.FileHandler(config['logger']['log_file'], encoding=config['encoding']),
        logging.StreamHandler(TextIOWrapper(stdout.buffer, encoding=config['encoding']))
    ]
)
