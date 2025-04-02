from common import convert_time
from logging import getLogger
from time import time
from scraper import Scraper
from subprocess import run as subprocess_run, SubprocessError
from platform import system

logger = getLogger(__name__)

def is_behind_vpn() -> bool:
    """
    Check if the user is behind a VPN by checking if gateway IP address is assigned. 
    If the gateway IP address is assigned, the user is behind a VPN. 
    Otherwise, the user is not behind a VPN. Supported on Windows OS only.
    """
    try:
        if system() == "Windows":
            result = subprocess_run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            vpn_info = next((lines[i:i+7] for i, line in enumerate(lines) if "NordLynx" in line), None)
            return True if vpn_info and vpn_info[-1].strip().split(':')[-1].strip() != "" else False
        else:
            logger.debug("Linux OS VPN check not supported - skipping")
            return True

    except SubprocessError as e:
        logger.error(f"Error checking VPN status: {e}")
        return False

def main():
    if not is_behind_vpn():
        logger.error("Error: Not behind a VPN. Please connect to a VPN and try again.")
        return 1
    
    start = time()
    s = Scraper()
    
    try:
        s.print_and_notify_on_events(s.run_program())
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt.")
        return 1

    logger.info(f"Time: {convert_time(time() - start)}")
    return 0

if __name__ == '__main__':
    exit(main())
