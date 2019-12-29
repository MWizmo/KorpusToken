from app import app, db


@app.before_first_request
def create_tables():
    db.create_all()


try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass


