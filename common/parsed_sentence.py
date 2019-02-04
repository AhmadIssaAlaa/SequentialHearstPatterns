class parsed_sentence:
    def __init__(self):
        self.words = []
        self.NPs = []

    def add_word(self, w, l, pos, i, par, parent_index, rel , ty):
        word = parsed_word(w, l, pos, i, par, parent_index, rel, ty)
        self.words.append(word)

    def add_NP(self, np, root, ri, start, end):
        np2 = noun_phrase(np, root, ri, start, end)
        self.NPs.append(np2)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return " ".join([word.word for word in self.words])

class parsed_word:
    def __init__(self, w, l, pos, i, par, parent_index, rel, ty):
        self.word = w
        self.lemma = l
        self.pos = pos
        self.index = i
        self.dep_rel = rel
        self.parent = par
        self.parent_index = parent_index
        self.type = ty

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(" + self.word + ", " + self.lemma + ", " + self.pos + ", " + str(self.index) + ", " + self.parent + ", " + str(self.parent_index) + ", " + self.dep_rel+ ", " + self.type + ")"

class noun_phrase:
    def __init__(self, np, root, ri, start, end):
        self.text = np
        self.root = root
        self.root_index = ri
        self.start = start
        self.end = end

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(" + self.text + ", " + self.root + ", " + str(self.root_index) + ", " + str(self.start) + ", " + str(self.end) + ")"