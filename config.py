
class Config(object):
    DEBUG = True
    TESTING = False

    SCRAPER_PATH = "/home/zikavaclav05/"
    PROPERTY_PATH = "/home/zikavaclav05/taxscraper/tax_venv/bin/scraper_property/"


class ProductionConfig(Config):
    ENV = "production"
    pass


class DevelopmentConfig(Config):
    ENV = "development"

    SCRAPER_PATH = "/home/walter/Dev/scraper_property"
    PROPERTY_PATH = "/home/walter/Dev/scraper_property/properties/"
