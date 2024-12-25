import os


class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload'
    FILE_PATH = ROOT + UPLOAD_PATH

    USER = os.environ.get('MYSQL_USER', 'proxima')
    PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Sap_4778147781')
    HOST = os.environ.get('MYSQL_HOST', 'localhost')
    PORT = os.environ.get('MYSQL_PORT', 3306)
    DB = os.environ.get('MYSQL_DB', 'project_001')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = 'soefkseifs47y3920rwfga8fl391ur32uf'
    SQLALCHEMY_TRACK_MODIFICATIONS = True