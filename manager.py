from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app
from src.haokan.models import db

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)

if __name__ == '__main__':
    manager.run()
