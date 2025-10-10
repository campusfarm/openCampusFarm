from winreg import REG_CREATED_NEW_KEY

from PIL.ImagePalette import load
from numpy import real
from EMS import real_time_ems
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    real_time_ems.main()
