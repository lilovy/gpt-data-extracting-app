from .DBHelper import DBHelper
from sqlalchemy.pool import QueuePool


DB = DBHelper('results/.database/markupdata.db')

pool = QueuePool(
    creator=lambda: DB.engine.connect(),
    pool_size=10,
    max_overflow=5,
)

connection = pool.connect()