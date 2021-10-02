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
    app.run(host="0.0.0.0", debug=True, use_reloader=True)
