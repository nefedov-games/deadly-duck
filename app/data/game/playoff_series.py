
from sqlalchemy import and_, text

from app import db
from config_game import DdLeagueConfig
from app.custom_queries import MAX_PLAYOFF_ROUND_SQL
from app.custom_queries import SERIES_IN_ONE_ROUND_IN_ONE_DIVISION_SQL

class DdPlayoffSeriesStatuses:
    PLANNED = 0
    IN_PROGRESS = 1
    FINISHED = 2


class DdPlayoffSeries( db.Model ):
    __tablename__ = "playoff_series"
    pk = db.Column( db.Integer, primary_key=True, index=True ) # @UndefinedVariable
    top_seed_pk = db.Column( db.ForeignKey( "clubs.club_id_n" ), index=True ) # @UndefinedVariable
    low_seed_pk = db.Column( db.ForeignKey( "clubs.club_id_n" ), index=True ) # @UndefinedVariable
    user_pk = db.Column( db.ForeignKey( "users.pk" ), index=True ) # @UndefinedVariable

    top_seed_victories_n = db.Column( db.Integer, default=0, nullable=False ) # @UndefinedVariable
    low_seed_victories_n = db.Column( db.Integer, default=0, nullable=False ) # @UndefinedVariable

    season_n = db.Column( db.Integer, default=0, nullable=False, index=True ) # @UndefinedVariable
    round_n = db.Column( db.Integer, default=0, nullable=False, index=True ) # @UndefinedVariable
    is_finished = db.Column( db.Boolean, default=False, nullable=False ) # @UndefinedVariable

    matches = db.relationship( "DdMatch", backref="playoff_series" ) # @UndefinedVariable

    top_seed = db.relationship( "DdClub", foreign_keys=[top_seed_pk] ) # @UndefinedVariable
    low_seed = db.relationship( "DdClub", foreign_keys=[low_seed_pk] ) # @UndefinedVariable

    def GetLowSeedMatchesWon( self, sets_to_win=0 ):
        return sum( self._GetSetsLowSpeedWon( m ) == sets_to_win for m in self.matches )

    def GetLooserPk( self, sets_to_win=0, matches_to_win=0 ):
        top = self.GetTopSeedMatchesWon( sets_to_win=sets_to_win )
        low = self.GetLowSeedMatchesWon( sets_to_win=sets_to_win )

        if top >= matches_to_win:
            return self.low_seed_pk
        elif low >= matches_to_win:
            return self.top_seed_pk
        else:
            return None

    def GetTopSeedMatchesWon( self, sets_to_win=0 ):
        return sum( self._GetSetsTopSpeedWon( m ) == sets_to_win for m in self.matches )

    def GetWinnerPk( self, sets_to_win=0, matches_to_win=0 ):
        top = self.GetTopSeedMatchesWon( sets_to_win=sets_to_win )
        low = self.GetLowSeedMatchesWon( sets_to_win=sets_to_win )

        if top == matches_to_win:
            return self.top_seed_pk
        elif low == matches_to_win:
            return self.low_seed_pk
        else:
            return None

    def IsFinished( self, matches_to_win=0 ):
        condition1 = self.top_seed_victories_n == matches_to_win
        condition2 = self.low_seed_victories_n == matches_to_win
        if condition1 or condition2:
            return True
        else:
            return False

    def _GetSetsLowSpeedWon( self, match ):
        if match.home_team_pk == self.low_seed_pk:
            return match.home_sets_n
        elif match.away_team_pk == self.low_seed_pk:
            return match.away_sets_n
        else:
            raise ValueError( "Low seed had not played this match." )

    def _GetSetsTopSpeedWon( self, match ):
        if match.home_team_pk == self.top_seed_pk:
            return match.home_sets_n
        elif match.away_team_pk == self.top_seed_pk:
            return match.away_sets_n
        else:
            raise ValueError( "Top seed had not played this match." )

    def __repr__( self ):
        return "<DdPlayoffSeries #{0:d} {1:d} vs {2:d} season #{3:d}>".format( 
            self.pk,
            self.top_seed_pk,
            self.low_seed_pk,
            self.season_n
        )

class DdDaoPlayoffSeries( object ):
    def CreatePlayoffSeries( self, top_seed_pk=0, low_seed_pk=0, round_n=0, user=None ):
        """
        Creates new playoff series.
        Does not save it in the db.
        Returns created series.
        """
        series = DdPlayoffSeries()
        series.user_pk = user.pk
        series.season_n = user.current_season_n
        series.top_seed_pk = top_seed_pk
        series.low_seed_pk = low_seed_pk
        series.round_n = round_n
        # self.SavePlayoffSeries(series)
        return series

    def GetAllPlayoffSeries( self, user=None ):
        return DdPlayoffSeries.query.filter( 
            and_( 
                DdPlayoffSeries.season_n == user.current_season_n,
                DdPlayoffSeries.user_pk == user.pk
            )
        ).all()

    def GetPlayoffSeriesByRoundAndDivision( self, user=None, rnd=0 ):
        div1 = DdPlayoffSeries.query.from_statement( 
            text( SERIES_IN_ONE_ROUND_IN_ONE_DIVISION_SQL ).params( 
                user=user.pk,
                season=user.current_season_n,
                division=1,
                rnd=rnd
            )
        ).all()
        div2 = DdPlayoffSeries.query.from_statement( 
            text( SERIES_IN_ONE_ROUND_IN_ONE_DIVISION_SQL ).params( 
                user=user.pk,
                season=user.current_season_n,
                division=2,
                rnd=rnd
            )
        ).all()
        return div1, div2

    def GetMaxPlayoffRound( self, user=None ):
        res = db.engine.execute( # @UndefinedVariable
            MAX_PLAYOFF_ROUND_SQL.format( 
                user_pk=user.pk,
                season=user.current_season_n
            )
        ).first() # @UndefinedVariable
        return res["max_round"]

    def SavePlayoffSeries( self, pos=None ):
        pos.is_finished = pos.IsFinished( 
            matches_to_win=DdLeagueConfig.MATCHES_TO_WIN,
        )
        db.session.add( pos ) # @UndefinedVariable
        db.session.commit() # @UndefinedVariable

    def SavePlayoffSeriesList( self, series_list=[] ):
        for srs in series_list:
            srs.is_finished = srs.IsFinished( 
                matches_to_win=DdLeagueConfig.MATCHES_TO_WIN,
            )
        db.session.add_all( series_list ) # @UndefinedVariable
        db.session.commit() # @UndefinedVariable
