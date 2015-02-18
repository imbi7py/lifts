"""
Logging support for LIFTS.

This implements a log to a SQLITE database.
"""
import sys

if sys.version_info.major < 3:
    import sqlite 
else:
    import sqlite3 as sqlite


TABLES = {
    "post_log": """CREATE TABLE post_log (
    id INTEGER PRIMARY KEY
    ,posted_on  DATETIME DEFAULT CURRENT_TIMESTAMP
    ,posted_by  TEXT
    ,filename   TEXT
    ,recipients TEXT
    ,comments    TEXT
    ,protected  BOOLEAN
    )
    """
}


class Log(object):
    """The Log object for LIFTS

    This is an interface to a SQLite database that will store our log.
    """

    def __init__(self, filename):
        """Connect to the logging database file; create if necessary"""
        try:
            self.db = sqlite.connect(filename)
        except sqlite.OperationalError as e:
            print("Unable to open {} for logging.".format(filename))
            raise e
        self.cursor = self.db.cursor()
        # Test if the tables exists, create if not
        query = """
        SELECT :tablename IN
        (SELECT name FROM sqlite_master WHERE type='table') AS table_exists"""
        for table in TABLES.keys():
            self.cursor.execute(query, {"tablename": table})
            exists = self.cursor.fetchone()[0]
            if not exists:
                self.cursor.execute(TABLES[table])

    def log_post(self, posted_by, filename, recipients, comments, protected):
        query_data = {
            "posted_by": posted_by,
            "filename": filename,
            "recipients": ', '.join(x.strip() for x in recipients),
            "comments": comments,
            "protected": protected
        }
        query = """INSERT INTO post_log
        (posted_by, filename, recipients, comments, protected)
        VALUES (:posted_by, :filename, :recipients,
        :comments, :protected)
        """
        self.cursor.execute(query, query_data)
        self.db.commit()

