import os

BASE_PATH = os.path.split(__file__)[0]

DATABASE_URL = 'sqlite:///{}'.format(os.path.join(BASE_PATH, 'nissan_operator_DB.sqlite'))

