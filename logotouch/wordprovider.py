import csv

class AbstractWordProvider(object):

    def __init__(self):
        #TODO:  nedd type..like verb, adjective, noun etc?!
        self.data = {}
        self.word = 'walk'
        self.tense = 1 # 0=past, 1=present, 2=future
        self.person = 1
        self.pronouns = [u'Je', u'Tu', u'Il', u'Nous', u'Vous', u'Ils']
        self.zoom = 0
        self.maxzoom = 0
        self.minzoom = 0
        self.maxsynonym = 0
        self.synonym = 0
        self.antonym = False

    def __str__(self):
        return self.pronouns[self.person] + self.conjugate() + ' ' + str(self.tense)

    def conjugate(self):
        #TODO: return right word form root with time and person
        return self.word

    def get_synonym(self):
        return 'wander'

    def get_antonym(self):
        return 'stand'

    def do_zoomin(self):
        zoom = min(self.zoom + 1, self.maxzoom)
        if self.zoom == zoom:
            return
        self.zoom = zoom
        return True

    def do_zoomout(self):
        zoom = max(self.zoom - 1, self.minzoom)
        if self.zoom == zoom:
            return
        self.zoom = zoom
        return True

    def do_synonym(self):
        synonym = (self.synonym + 1) % self.maxsynonym
        if self.synonym == synonym:
            return
        self.synonym = synonym
        return True

    def do_antonym(self):
        self.antonym = not self.antonym
        return True

    def do_time_next(self):
        tense = min(2, self.tense + 1)
        if tense == self.tense:
            return
        self.tense = tense
        return True

    def do_time_previous(self):
        tense = max(0, self.tense - 1)
        if tense == self.tense:
            return
        self.tense = tense
        return True

    def do_person_next(self):
        person = min(len(self.pronouns) - 1, self.person + 1)
        if person == self.person:
            return
        self.person = person
        return True

    def do_person_previous(self):
        person = max(0, self.person - 1)
        if person == self.person:
            return
        self.person = person
        return True


class CSVWordProvider(AbstractWordProvider):
    def __init__(self, filename):
        super(CSVWordProvider, self).__init__()
        self.filename = filename
        self.load()

    def load(self):
        def norm(title):
            c = title.split()
            if len(c) != 2:
                return title
            a, b = c
            a = a.replace('Pr\xc3\xa9sent', 'present')
            a = a.replace('Futur', 'future')
            a = a.replace('Imparfait', 'past')
            a = a.replace('Imparfai', 'past')
            d = {'je': 0, 'tu': 1, 'il': 2, 'nous': 3, 'vous': 4, 'ils': 5}
            return '%s_%s' % (a, d[b.lower()])
        rows = []
        titles = None
        with open(self.filename, 'rb') as fd:
            data = csv.reader(fd)
            for row in data:
                if titles is None:
                    titles = row
                else:
                    rows.append(row)

        for i in xrange(len(titles)):
            titles[i] = titles[i].lower().replace('-', '')

        self.titles = titles
        for row in rows:
            self.data[norm(row[0])] = row[1:]


        # count zoomin
        for t in titles:
            if t.startswith('zoomin'):
                self.maxzoom += 1
            if t.startswith('zoomout'):
                self.minzoom -= 1
            if t.startswith('secouer'):
                self.maxsynonym += 1

    def get(self):
        title = 'mot'
        if self.antonym:
            title = 'contraire'
        else:
            # zoom in
            if self.zoom > 0:
                z = self.zoom - 1
                if z == 0:
                    title = 'zoomin'
                else:
                    title = 'zoomin%d' % z
            # zoom out
            elif self.zoom < 0:
                z = abs(self.zoom) - 1
                if z == 0:
                    title = 'zoomout'
                else:
                    title = 'zoomout%d' % z
            # synonym
            elif self.synonym != 0:
                title = 'secouer%d' % self.synonym

        # tense ?
        a = {0: 'past', 1: 'present', 2: 'future'}
        tense = '%s_%d' % (a[self.tense], self.person)

        tidx = self.titles.index(title) - 1
        word = self.data[tense][tidx]
        word = word.decode('utf8')
        return self.pronouns[self.person] + u' ' + word
