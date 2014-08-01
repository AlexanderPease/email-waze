''' 

OLD uses politiciandb (w/out MongoEngine)
Inits or updates politiciandb with Sunlight database info and other fields

'''
import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/ftv/followthevote')
    import settings
except:
    pass

from sunlight import congress
from db.old import politiciandb

### Pull data from sunlight
politicians = congress.all_legislators_in_office()

for politician in politicians:
    p = {'first_name': politician['first_name'], 
        'last_name': politician['last_name'],
        'state': politician['state'],
        'party': politician['party'],
        'title': politician['title'],
        'bioguide_id': politician['bioguide_id'],
    }
    # Sens don't have district
    if 'district' in politician.keys() and p['title'] == 'Rep':
        p['district'] = politician['district']
    else:
        p['district'] = ""
    if 'twitter_id' in politician.keys():
        p['twitter_id'] = politician['twitter_id']
    else:
        p['twitter_id'] = ""

    politiciandb.save(p)
    print 'Added sunlight data for %s' % p['bioguide_id']

### Add in Twitter handles I found myself
TWITTER_EXTRA = [
    ('Grayson', 'AlanGrayson'),
    ('Hastings', 'alceehastings'),
    ('Franken', 'alfranken'),
    ('Long', 'auctnr1'),
    ('Cassidy', 'BillCassidy'),
    ('Schatz', 'brianschatz'),
    ('Murphy', 'ChrisMurphyCT'),
    ('Rohrabacher', 'DanaRohrabacher'),
    ('Davis', 'DannyKDavis'),
    ('Vitter', 'DavidVitter'),
    ('Cummings', 'ElijahECummings'),
    ('Lucas', 'FrankDLucas'),
    ('Garcia', 'JoeGarcia'),
    ('Tester', 'jontester'),
    ('Beatty', 'JoyceBeatty'),
    ('Brownley', 'JuliaBrownley'),
    ('Ayotte', 'KellyAyotte'),
    ('Capuano', 'MikeCapuano'),
    ('Hall', 'RalphHallPress'),
    ('Andrews', 'RepAndrews'),
    ('Cardenas', 'RepCardenas'), #should be an with accent
    ('Guthrie', 'RepGuthrie'),
    ('Sarbanes', 'RepJohnSarbanes'),
    ('Lance', 'RepLanceNJ7'),
    ('Lipinski', 'RepLipinski'),
    ('Pocan', 'repmarkpocan'),
    ('Welch', 'RepPeterWelch'),
    ('Davis', 'RepSusanDavis'),
    ('Baldwin', 'RepTammyBaldwin'),
    ('Thompson', 'RepThompson'),
    ('Holt', 'RushHolt'),
    ('Isakson', 'SenatorIsakson'),
    ('Risch', 'SenatorRisch'),
    ('Gillibrand', 'SenGillibrand'),
    ('Cowan', 'SenMoCowan'),
    ('Scalise', 'SteveScalise'),
    ('Massie', 'ThomasMassieKY'),
    ('Walz', 'Tim_Walz'),
    ('Kaine', 'timkaine'),
    ('Radel', 'treyradel'),
    ]
    
for p in politiciandb.find_all():
    for pair in TWITTER_EXTRA:
        if p['last_name'] == pair[0]:
            p['twitter_id'] = pair[1]
            politiciandb.save(p)
            print "Added twitter handle %s" % p['twitter_id']

### Create some derivative fields
states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

for p in politiciandb.find_all():
    p['name'] = p['title'] + ". " + p['first_name'] + " " + p['last_name']
    p['brief_name'] = p['title'] + ". " + p['last_name']
    p['full_state_name'] = states[p['state']]
    if p['title'] == 'Sen':
        p['chamber'] = 'Senate'
    else:
        p['chamber'] = 'House'
    
    # Determine if image exists or not, save path in document
    image_root = os.path.join(settings.get('project_root'),'static/img/200x250/')
    image_path = image_root +  p['bioguide_id'] + '.jpg'
    file_exists = os.path.isfile(image_path)
    if file_exists:
        p['portrait_path'] = 'img/200x250/' + p['bioguide_id'] + '.jpg'
    else: 
        p['portrait_path'] = 'img/200x250/DEFAULT.jpg'

    politiciandb.save(p)

print 'All politicians added to database'


