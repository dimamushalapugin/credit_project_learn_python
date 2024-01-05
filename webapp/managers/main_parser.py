import openpyxl
import os

# from datetime import datetime as dt
# from typing import Optional
# from docx import Document
# from num2words import num2words
# from flask_login import current_user
# from webapp.config import DADATA_BASE
# from webapp.risk.logger import logging
# from webapp.risk.mongo_db import MongoDB
from dadata import Dadata
DADATA_TOKEN = "804d29658b186056c6cfab57f94c68695581d747"
DADATA_SECRET = "2c54bab544f947c975525ab452d014492122e52b"
DADATA_BASE = Dadata(DADATA_TOKEN, DADATA_SECRET)




def main_result_dadata(someone):
    main_result = DADATA_BASE.find_by_id("party", someone)
    return main_result
print(main_result_dadata('1655099271'))



