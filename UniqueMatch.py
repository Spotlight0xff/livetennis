class UniqueMatch:
    def __init__(self, year, tId, matchId):
        self.year = year
        self.tournament_id = tId
        self.match_id = matchId

    def getName(self):
        """Generate an unique name for each match record"""
        return 'Match_{}_{}_{}'.format(
                self.year,
                self.tournament_id,
                self.match_id)

    def getId(self):
        return (self.year,
                self.tournament_id,
                self.match_id)

    def __eq__(self, other):
        """Compare objects based on getId() values"""
        return self.getId() == other.getId()

    def getMatch(self):
        return self.match_id

    def getYear(self):
        return self.year

    def getTournament(self):
        return self.tournament_id
