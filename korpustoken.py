from app import app


# @app.before_first_request
# def create_tables():
#     db.create_all()


# try:
#     import pymysql
#     pymysql.install_as_MySQLdb()
# except ImportError:
#     pass

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
