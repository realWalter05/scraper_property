
class Config(object):
    DEBUG = True
    TESTING = False

    SCRAPER_PATH = "/home/zikavaclav05/"
    PROPERTY_PATH = "/home/zikavaclav05/taxscraper/tax_venv/bin/scraper_property"


class ProductionConfig(Config):
    ENV = "production"
    pass


class DevelopmentConfig(Config):
    ENV = "development"

    SCRAPER_PATH = "C:/Users/zikav/dev/python/scraper/"
    PROPERTY_PATH = "C:/Users/zikav/dev/python/scraper/scraper_property/"
