# -*- coding: utf-8 -*-
from v2ex import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand 

from v2ex.models import User, Topic

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.command
def test():
    """run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)

def make_shell_context():
    return dict(app=app, db=db, User=User,Topic=Topic)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)




if __name__ == '__main__':
    manager.run()

