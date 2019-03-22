
import os

from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from app import CreateApp
from app import db
from app import cache
from app.data.models import DdPost
from app.data.game.career import DdCareer
from app.data.game.club import DdClub
from app.data.game.game_service import DdGameService
from app.data.game.match import DdMatch
from app.data.game.player import DdPlayer
from app.data.game.playoff_series import DdPlayoffSeries
from app.data.main.role import DdRole
from app.data.main.role import DdPermission
from app.data.main.user import DdUser


app = CreateApp(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


def MakeShellContext():
    return dict(
        app=app,
        db=db,
        cache=cache,
        DdClub=DdClub,
        DdMatch=DdMatch,
        DdPermission=DdPermission,
        DdPlayer=DdPlayer,
        DdPlayoffSeries=DdPlayoffSeries,
        DdPost=DdPost,
        DdRole=DdRole,
        DdUser=DdUser,
    )


app.shell_context_processor(MakeShellContext)


@app.cli.command()
def test():
    """Performs all tests."""
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def initapp():
    """Inserts roles and clubs into database."""
    service = DdGameService()
    DdRole.InsertRoles()
    service.InsertClubs()
