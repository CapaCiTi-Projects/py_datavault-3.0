import mysql.connector
import tkinter.simpledialog as tkSimpleDialog


class DBColumn(object):
    def __init__(self, name, dtype="VARCHAR(45)", allow_nulls=True, auto_increment=False):
        self.name = name
        self.type = dtype
        self.allow_nulls = allow_nulls
        self.auto_increment = auto_increment

    def __repr__(self):
        self.__str__()

    def __str__(self):
        out = ""

        out += "`" + self.name + "`"
        out += " " + self.type
        if not self.allow_nulls:
            out += " NOT NULL"
        if self.auto_increment:
            out += " AUTO_INCREMENT"

        return out

    def get_name(self):
        return self.name


class DBManager(object):
    _config = {
        "host": "localhost",
        "user": "root",
        "passwd": "",
        "db": ""
    }

    # Store information about the tables for the database through a list of dictionaries
    # Fields Include:
    # table string The name of the table,
    # primary string The primray key of the table,
    # foreign tuple The foreign key data for the table,
    # fields tuple The fields for the table, represented using DBColumn
    _tables = [
        {
            "table": "products",  # name of the table
            "primary": "id_product",  # primary key of the table
            "foreign": (  # table foreign key
                "id_category",  # Key in current table
                "categories(id_category)"  # Reference to key in other table
            ),
            "fields": (  # the columns of the table
                DBColumn("id_product", dtype="INT",
                         allow_nulls=False, auto_increment=True),
                DBColumn("id_category", dtype="INT", allow_nulls=False),
                DBColumn("name", allow_nulls=False),
                DBColumn("stock_available", dtype="INT", allow_nulls=False),
                DBColumn("selling_price", dtype="DECIMAL(13,2)",
                         allow_nulls=False)
            )
        },
        {
            "table": "categories",
            "primary": "id_category",
            "fields": (
                DBColumn("id_category", dtype="INT",
                         allow_nulls=False, auto_increment=True),
                DBColumn("title", allow_nulls=False)
            )
        }
    ]

    # Used for storing data, accessible via `store_data` & `retrieve_data`.
    _data_store = {}

    @staticmethod
    def init(data=None, tables=None, **conf):
        """Initialise the DbManager data dictionaries, ie '_data', '_conf' & '_tables'."""
        for key in data:
            DBManager.store_data(key, data[key])

        if tables is not None:
            DBManager._tables = tables

        for key in conf:
            DBManager.updateconfig_safe(key, conf[key])

        DBManager.setup_db()

    @staticmethod
    def open_connection(ignore_db=False):
        """Open a connection to the database using the data store in DBManager._config.
        Retrieve using the static method, getconfig()."""

        connect_args = {}
        connect_args["host"] = DBManager.getconfig("host")
        connect_args["user"] = DBManager.getconfig("user")

        passwd = ""
        if DBManager.isconfigset("passwd"):
            passwd = DBManager.getconfig("passwd")
        connect_args["passwd"] = passwd

        if DBManager.isconfigset("db") and not ignore_db:
            connect_args["database"] = DBManager.getconfig("db")

        con = mysql.connector.connect(**connect_args)
        return con

    @staticmethod
    def setup_db():
        """Setup the DataBase by creating all of the tables stored in the `_tables` dict."""
        if (not DBManager.isconfigset("db")) or (not DBManager._tables):
            return

        with DBManager.open_connection() as con:
            cursor = con.cursor(prepared=True)

            # Create all of the tables.
            for table in DBManager._tables:
                sql_createtable = f"""CREATE TABLE IF NOT EXISTS `{table["table"]}` (
                    {",".join(str(field) for field in table["fields"])},
                    PRIMARY KEY ({table["primary"]})
                )"""

                cursor.execute(sql_createtable)

            # Add foreign keys to the tables.
            for table in DBManager._tables:
                if "foreign" not in table:
                    continue

                sql_alter = f"""ALTER TABLE `{table["table"]}`
                    ADD FOREIGN KEY ({table["foreign"][0]})
                    REFERENCES {table["foreign"][1]}
                """

                cursor.execute(sql_alter)

    @staticmethod
    def get_table_cols(table):
        """Get a tuple with the names of all of the columns in the specified table."""
        columns = ([tuple(map(lambda x: x.get_name(), t["fields"]))
                    for t in DBManager._tables if t["table"] == table])[0]

        assert(len(columns) > 0), f"`{table}` does not exist in known tables."
        return columns

    @staticmethod
    def get_table_cols_full(table):
        """Get the full `DBColumn` tuple at table."""
        columns = list(t["fields"]
                       for t in DBManager._tables if t["table"] == table)[0]

        assert(len(columns) > 0), f"`{table}` does not exist in known tables."
        return columns

    @staticmethod
    def updateconfig_safe(key, data):
        """This method is the same as updateconf(), but is considered safe as
        it doesn't overwrite any config data if it already has a value."""
        if key in DBManager._config:
            if not DBManager.isconfigset(key):
                DBManager._config[key] = data
        else:
            raise KeyError(f"{key} does not exists in DBManager.tables")

    @ staticmethod
    def updateconfig(key, data):
        """Update data in the `_conf` dictionary"""
        if key in DBManager._config:
            DBManager._config[key] = data
        else:
            raise KeyError(f"{key} does not exists in DBManager.tables")

    @ staticmethod
    def getconfig(key):
        """Get the data at key in the `_conf` dict"""
        return DBManager._config[key]

    @ staticmethod
    def isconfigset(key):
        """Check to see if key exists in _conf and if a value is set."""
        return (key in DBManager._config) and (DBManager._config[key])

    @ staticmethod
    def store_data(key, data, allow_overwrite=True):
        """Method to store data in the `_data` dict. Can be used for any data."""
        if allow_overwrite:
            DBManager._data_store[key] = data
        else:
            if key not in DBManager._data_store:
                DBManager._data_store[key] = data

    @ staticmethod
    def retrieve_data(key):
        """Method to retrieve data from the `_data` dict using key."""
        return DBManager._data_store[key]


if __name__ == "__main__":
    # Some basic test data
    man = DBManager
    man.updateconfig("passwd", "2ZombiesEatBrains?")
    man.updateconfig("db", "practice")

    man.setup_db()
    print("\n".join(man.get_table_cols("products")))
    print("")
    print("\n".join(map(str, man.get_table_cols_full("products"))))
