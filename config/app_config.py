
from application import GlobalApplicationConfig, TwilioConfig


class Sephora(object):
    Config = None
    DbConfig = None
    TwilioConfig = None

    @staticmethod
    def init_config():
        Sephora.DbConfig = DbConfig
        Sephora.Config = GlobalApplicationConfig
        Sephora.TwilioConfig = TwilioConfig


class DbConfig(object):
    NAME = '<YOUR DB NAME>'
    USER = '<YOU DB USER>'
