from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from extentions import db, migrate

# Initialize the Flask app
app = Flask(__name__)

# Configure async support
app.config['FLASK_ASYNC'] = True  # Enable async support

# Configure the database URI (SQLite in this case)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "test_db.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and migration objects
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import your models after initializing db and migrate
from src.models.user import User
from src.models.competition import Competition
from src.models.registration import Registration
from src.models.competition_metadata import DanceStyle, DanceGroup

# routers
from src.routes.whatsapp import whatsapp_bp

# Register the blueprints
app.register_blueprint(whatsapp_bp)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
