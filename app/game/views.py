
"""As restful as possible game-related views.

Created on Feb 02, 2019

@author: montreal91
"""
from flask import current_app
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.views import MethodView
from flask_login import current_user
from flask_login import login_required

from app import db
from app.data.game.match import MatchChronologicalComparator
from app.data.game.player import DdPlayer
from app.data.game.player import PlayerModelComparator
from app.data.models import DdUser
from app.game import game
from configuration.config_game import club_names


@game.route("/api/clubs/", methods=["POST"])
@login_required
def Clubs():
    return jsonify(clubs=[
        {"pk": 1, "club_name": "Auckland Aces"},
        {"pk": 2, "club_name": "Brisbane Broncos"},
        {"pk": 9, "club_name": "Adelaide Falcons"},
        {"pk": 10, "club_name": "Bunbury Ravens"},
    ])


@game.route("/main/")
@login_required
def MainScreen():
    """Renders main screen."""
    if current_user.managed_club_pk is None:
        return redirect(url_for("main.Index"))

    club = game.service.GetClub(current_user.managed_club_pk)

    return render_template(
        "game/main_screen.html",
        club=club,
    )


@game.route("/api/main_screen_context/", methods=["POST"])
@login_required
def MainScreenContext():
    """Ajax view that responses with context data for main screen."""
    players = game.service.GetClubPlayers(
        user_pk=current_user.pk,
        club_pk=current_user.managed_club_pk,
    )
    players.sort(key=PlayerModelComparator, reverse=True)

    match = game.service.GetCurrentMatch(current_user)
    if match is not None and match.home_team_pk == current_user.managed_club_pk:
        ai_players = game.service.GetClubPlayers(
            user_pk=current_user.pk,
            club_pk=match.away_team_pk
        )
        away_player = max(ai_players, key=PlayerModelComparator)
        away_player = away_player.json
    else:
        away_player = None

    if match is not None:
        match = match.json

    return jsonify(
        away_player=away_player,
        players=[player.json for player in players],
        match=match,
    )

@game.route("/title_screen/")
@login_required
def TitleScreen():
    """Renders title string."""
    return render_template("game/title_screen.html")
