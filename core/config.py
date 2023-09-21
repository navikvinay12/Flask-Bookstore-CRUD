from settings import setting


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Development(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = setting.DATABASE_URL


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = None


config_dict = {
    "development": Development,
    "testing": Testing
}
