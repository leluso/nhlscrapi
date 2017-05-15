v0.4.5
------
- Bug fix
- Fork

v0.4.4
------

  * Close issue 15 from ``scrapr.rosterrep.parse_rosters()``
  * Calling ``max`` on empty key list, used common sense and switched to ``len``
  * Stupid indentation issue leading to inclusion of roster table header 

v0.4.3
------

  * Put some blunt checks in ``scrapr.descparser.py`` for missing info in RTSS reports.
  * See Issue 4
  * TODO: design a more robust/elegant way of defining data formats and missing data. This works for now.

v0.4.2
------

  * Let ``scrapr.rtss.PlayParser`` track game type and loosen skater count to address shootout parsing discussed in `Issue #2 <https://github.com/robhowley/nhlscrapi/issues/2>`_
  * Update constants ... will find a better way to handle checks.
  * see Issues 2, and 3

v0.4.1
------

  * Ugly hack in ``scrapr.toirep.TOIRepBase`` to account for missing data in the report discussed in `Issue #1 <https://github.com/robhowley/nhlscrapi/issues/1>`_
  * TODO: need to add a more robust way to handle broken records gracefully and continues parsing the remainder of the document.

v0.4.0
------

  * added support and associated unit test for event summary report

    - scraper in ``scrapr.eventsummary.EventSummRep``
    - report wrapper and primary access object in ``games.eventsummary.EventSummary``

  * the event summary report has abiltiy to filter and sort by player data
  * updated docs
  * updated REAMDME to reflect change

v0.3.7
------

  * messed up the prior upload. embarrassing. fixed remaining 3.x print issue.

v0.3.6
------

  * fixed a lot of python3.x compatibility issues

    - ``_tools.build_enum`` switch to ``items()`` from ``iteritems()``
    - ``print vs`` to ``print()`` in ``scrapr.descparser``
    - take out ``maketrans`` in ``scrapr.descparser`` and put in ``replace()``

  * fully qualify the ``scrapr.eventparser`` import in ``scrapr.rtss``
  * ``Game.plays`` property returns ``self.play_by_play.plays()`` but plays isn't callable

v0.3.5
------

  * dropped urllib2 dependency because it's 2015 and I'm tired of being a dinosaur
  * added ``requests`` to setup dependencies
  * fully qualified the ``scrapr.NHLCn`` import in ``scrapr.reportloader``
  * consolidated cli_opts.py into gamedata.py ... that whole thing needs a rewrite anyway (TODO)

v0.3.4
------

  * setup script reference bug.

v0.3.3
------

  * true bug fix. messed up the pypi upload setup
  * forgot cfg et c.

v0.3.2
------

  * refactored ``Plays``/``Strength`` construct

    - moved ``Plays`` and ``Strength`` from ``games.plays`` to ``games.playbyplay``
    - moved ``scrapr.rtss.playparser.PlayParser`` to ``scrapr.rtss``
    - deleted games/plays.py and scrapr/playparser.py
    - reworked data structure of ``PlayParser`` to be purely a dict
    - parsed play data isn't converted into the proper ``Play`` object until ``games.playbyplay.PlayByPlay`` gets it

  * refactored TOI/ShiftSummary construct

    - moved ``ShiftSummary`` from ``scrapr.toirep`` to ``games.toi``
    - ``scrapr.toirep.TOIRepBase`` now stores by player shift info as dict
    - parsed shift summary isn't made into a ``ShiftSummary`` object until in ``TOI``

  * Goal of both big refactors was to keep scraping/raw web data as dicts and have object wrappers only exist in the games package
  * added a ``unittest`` for the time on ice and shift summary info
  * added docstrings to major report and scraper interfaces
  * built docs using Sphinx


v0.3.1
------

  * fixed play-by-play bug created when no cum_stats provided
  * deprecated extractors
  * refactored GameKey and GameType into nhlscrapi.games.game
  * updated unittests and README to reflect the refactoring


v0.3.0
------

  * added face off comparison report, associated report loaded (scraper) and unittest

    * gave Game object basic access/loading to face off comp

  * reworked testing framework

    * can now run tests w the standard :code:`python -m unittest discover`

  * made versioning counter sane. structure is v(realease).(feature).(bug)
  * added :code:`lxml` to the install requirements in setup
  * added this change log
