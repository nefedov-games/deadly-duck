
"""
Created May 20, 2019

@author montreal91
"""

from random import shuffle
from typing import Generator
from typing import List
from typing import NamedTuple
from typing import Optional

from simplified.club import DdClub
from simplified.competition import DdAbstractCompetition
from simplified.competition import ScheduleDay
from simplified.match import DdMatchParams
from simplified.match import DdMatchProcessor
from simplified.match import DdMatchResult
from simplified.match import DdScheduledMatchStruct
from simplified.match import DdStandingsRowStruct


class DdChampionshipParams(NamedTuple):
    """A passive class to store regular championship parameters."""

    match_params: DdMatchParams
    recovery_day: int
    rounds: int


class DdRegularChampionship(DdAbstractCompetition):
    """A class to incapsulate logic of a regular championship."""

    _params: DdChampionshipParams
    _results: List[List[DdMatchResult]]

    def __init__(self, clubs: List[DdClub], params: DdChampionshipParams):
        super().__init__(clubs, params)
        self._results = []

    @property
    def is_over(self) -> bool:
        return self._day >= len(self._schedule)

    @property
    def standings(self) -> List[DdStandingsRowStruct]:
        results = [DdStandingsRowStruct(i) for i in range(len(self._clubs))]

        for day in self._results:
            for match in day:
                results[match.home_pk].sets_won += match.home_sets
                results[match.home_pk].games_won += match.home_games

                results[match.away_pk].sets_won += match.away_sets
                results[match.away_pk].games_won += match.away_games

        return results

    def Update(self) -> Optional[List[DdMatchResult]]:
        if self.current_matches is None:
            self._day += 1
            return None
        day_results = []
        for match in self.current_matches:
            processor = self._match_processor
            processor.SetMatchSurface(self._clubs[match.home_pk].surface)
            res = processor.ProcessMatch(
                self._clubs[match.home_pk].selected_player,
                self._clubs[match.away_pk].selected_player,
            )
            match.is_played = True

            res.home_pk = match.home_pk
            res.away_pk = match.away_pk
            day_results.append(res)
        self._day += 1
        self._results.append(day_results)
        return day_results

    @property
    def _match_processor(self) -> DdMatchProcessor:
        return DdMatchProcessor(self._params.match_params)

    def _MakeFullSchedule(self, pk_list: List[int]):
        def MirrorDay(matches: List[DdScheduledMatchStruct]):
            return [
                DdScheduledMatchStruct(m.away_pk, m.home_pk) for m in matches
            ]

        def CopyDay(matches):
            return [
                DdScheduledMatchStruct(m.home_pk, m.away_pk) for m in matches
            ]

        def ComposeDays(matches: List[DdScheduledMatchStruct], n: int):
            res = []
            for _ in range(n // 2):
                res.append(CopyDay(matches))
            for _ in range(n // 2):
                res.append(MirrorDay(matches))
            return res

        basic_schedule = _MakeBasicSchedule(pk_list)

        res: List[ScheduleDay] = []
        in_div = self._params.rounds
        ex_div = self._params.rounds

        for i, match in enumerate(basic_schedule):
            if i % 2 == 0:
                res.extend(ComposeDays(match, ex_div))
            else:
                res.extend(ComposeDays(match, in_div))
        return res

    def _MakeSchedule(self):
        pk_list = list(range(len(self._clubs)))
        shuffle(pk_list)
        days = self._MakeFullSchedule(pk_list)
        shuffle(days)

        day = -1
        done = 0
        while done < len(days):
            day += 1
            if day % self._params.recovery_day == 0:
                self._schedule.append(None)
                continue

            self._schedule.append(days[done])
            done += 1

        self._schedule.append(None)


def _MakeBasicSchedule(pk_list: List[int]):
    def MakePairs(lst: List[int]) -> ScheduleDay:
        n = len(lst) - 1
        mid = len(lst) // 2
        return [DdScheduledMatchStruct(lst[i], lst[n-i]) for i in range(mid)]

    def Shift(lst: List[int], n: int) -> List[int]:
        if n == 0:
            return list(lst)
        return [lst[0]] + lst[-n:] + lst[1:-n]

    def ShiftGen(lst: List[int]) -> Generator[List[int], None, None]:
        for i in range(len(lst) - 1):
            yield Shift(lst, i)

    return [MakePairs(l) for l in ShiftGen(pk_list)]
