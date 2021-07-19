from flask import Flask
from application.config import Config





app = Flask(__name__)
app.config.from_object(Config)






def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from application.main.routes import main 
    app.register_blueprint(main)

    return app 

