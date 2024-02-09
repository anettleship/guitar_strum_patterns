from application.app_factory import create_app
from application.config import Config


app = create_app(Config())


def main(app):
    app.run()


if __name__ == "__main__":
    main(app)
