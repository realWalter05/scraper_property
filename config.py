
class Config(object):
    DEBUG = True
    TESTING = False

    SCRAPER_PATH = "~/"
    PROPERTY_PATH = "~/scraper_property/"


class ProductionConfig(Config):
    ENV = "production"
    pass


class DevelopmentConfig(Config):
    ENV = "development"

    SCRAPER_PATH = "C:/Users/zikav/dev/python/scraper/"
    PROPERTY_PATH = "C:/Users/zikav/dev/python/scraper/scraper_property/"
