class HHCouple:
    def __init__(self, hypo, hyper):
        self.hypernym = hyper
        self.hyponym = hypo

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(" + self.hyponym + ", " + self.hypernym + ")"

    def __eq__(self, other):
        return self.hypernym == other.hypernym and self.hyponym == other.hyponym

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        return self.hypernym != other.hypernym or self.hyponym != other.hyponym