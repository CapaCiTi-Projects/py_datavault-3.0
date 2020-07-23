from main import Application
from dbmanager import DBManager

import pandas as pd

data = {
    "db_data": pd.DataFrame()
}

DBManager.init(data=data, passwd="2ZombiesEatBrains?",
               db="practice", table="products")
app = Application()

app.set_tab(0)
cur_tab = app.tabs[app.visible_idx]

cur_tab.import_csv(r"C:\Users\jesse\Dropbox\My PC (LAPTOP-Q8UG53KR)\Documents\CapaCiTi\Activities\Sprints\py_datavault-3.0\import-products.csv")
cur_tab.save_to_db()