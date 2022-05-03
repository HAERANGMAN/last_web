import os

BASE_DIR = os.path.dirname(__file__)
SQLAlCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))    # 데이터 베이스 접속주소
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 이벤트를 처리하는 옵션 >> 안필요해서 False