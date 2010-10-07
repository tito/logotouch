import csv
import sys
import re
from pprint import pprint

# import csv
c = csv.reader(open(sys.argv[1]), delimiter=',')

#-----------------------------------------------------
# fields & relation
#-----------------------------------------------------
fields_map = {
    'futur je': 'futur_je',
    'futur il': 'futur_il',
    'futur ils': 'futur_ils',
    'futur nous': 'futur_nous',
    'futur tu': 'futur_tu',
    'futur vous': 'futur_vous',
    'imparfai il': 'imparfait_il',
    'imparfait ils': 'imparfait_ils',
    'imparfait je': 'imparfait_je',
    'imparfait tu': 'imparfait_tu',
    'imparfait vous': 'imparfait_vous',
    'imparfait nous': 'imparfait_nous',
    'infinitif': 'name',
    'pr\xc3\xa9sent il': 'present_il',
    'pr\xc3\xa9sent ils': 'present_ils',
    'pr\xc3\xa9sent je': 'present_je',
    'pr\xc3\xa9sent nous': 'present_nous',
    'pr\xc3\xa9sent vous': 'present_vous',
    'pr\xc3\xa9sent tu': 'present_tu',
    'root': 'is_root',
    'verb': 'is_verb'
}

def relation_map(relation):
    name, level = relation.split('-')
    return {'type': name.lower(), 'level': level}

#-----------------------------------------------------
# relation order
#-----------------------------------------------------
relation_order = c.next()[1:]

# fix some relation (empty and number)
# case Mot -> Mot-0
# case Zoomin -> Zoomin-0
# case <empty> -> take the last and increment number
# case Secouer0 -> Secouer-0
for idx in xrange(len(relation_order)):
    relation = relation_order[idx]
    if relation == '':
        rrelation = relation_order[idx - 1]
        s = re.split('^(\w+)-(\d+)$', rrelation)
        if len(s) == 4:
            s[2] = int(s[2]) + 1
            rrelation = '%s-%d' % (s[1], s[2])
        relation_order[idx] = rrelation
    else:
        s = re.split('^(\w+)(\d+)$', relation)
        if len(s) == 4:
            relation = '%s-%s' % (s[1], s[2])
        else:
            s = re.split('^(\w+)-(\d+)$', relation)
            if len(s) == 1:
                relation = '%s-0' % relation
        relation_order[idx] = relation

#-----------------------------------------------------
# values
#-----------------------------------------------------
values = {}
for row in c:
    for idx in xrange(1, len(row)):
        if not idx in values:
            values[idx] = {'is_root':'0', 'is_verb': '1'}
            if idx == 1:
                values[idx]['is_root'] = '1'
        field = fields_map[row[0].lower()]
        values[idx][field] = row[idx]

'''
pprint('RELATIONS')
pprint(relation_order)
pprint('VALUES')
pprint(values)
'''

#-----------------------------------------------------
# output SQL
#-----------------------------------------------------

# values
for idx, item in values.items():
    sql_fields = ','.join(map(lambda x: '`%s`' % x, fields_map.values()))
    sql_values = ','.join(map(lambda x: '"%s"' % item[x], fields_map.values()))
    print 'INSERT IGNORE INTO lt_mot (%s) VALUES (%s);' % (sql_fields, sql_values)

# relations
for relation in relation_order:
    idx = relation_order.index(relation) + 1
    if idx == 1: # Mot
        continue
    sql_values = relation_map(relation)
    sql_values['mot_orig'] = values[1]['name']
    sql_values['mot_rel'] = values[idx]['name']

    sql_fields = ','.join(map(lambda x: '`%s`' % x, sql_values.keys()))
    sql_values = ','.join(map(lambda x: '"%s"' % x, sql_values.values()))
    print 'INSERT IGNORE INTO lt_relation (%s) VALUES (%s);' % (sql_fields, sql_values)
