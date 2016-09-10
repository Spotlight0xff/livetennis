

class MatchModel(object):
    data = {}

    def fromCsv(self, csv):
        parsed = csv.split(',')
        print(len(parsed))
        print("\n".join(parsed))
        print('Build model from csv?!?!')

