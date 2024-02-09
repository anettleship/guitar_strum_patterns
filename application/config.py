import os
import sys
from application.config_stages import Stage
from dotenv import load_dotenv


class Config:
    def __init__(self, stage=None):
        load_dotenv()

        self.SECRET_KEY = os.environ.get("SECRET_KEY")

        if len(self.SECRET_KEY) == 0:
            print("No secret key set, exiting... please create file .env in project root and set 'SECRET_KEY' value, according to readme")
            sys.exit()

        if not stage:
            stage = Stage[os.environ.get("STAGE")]
        self.FLASK_ENV = stage.name

        if stage == Stage.testing:
            self.DEBUG = False
            self.TESTING = True
            return

        if stage == Stage.development:
            self.DEBUG = True
            self.TESTING = True
            return

        if stage == Stage.production:
            self.DEBUG = False
            self.TESTING = False
            return
