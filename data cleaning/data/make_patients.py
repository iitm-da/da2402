"""Generates patients.csv for DA2402 Data Cleaning, Lecture 6 (duplicates).

A hospital in Chennai registers a patient at the front desk on every visit, so one
person can appear several times, written differently each time. Fixed seed, so every
figure quoted on the slides reproduces exactly.

person_id is the truth: rows with the same person_id are the same person.
It exists so methods can be scored. Never use it for matching.

Planted on purpose:
  name     initial before or after the name, joined or split given names, spelling
           variants (Lakshmi / Laxmi), one-letter typos, upper case, titles (Mr., Dr.)
  phone    9840012345 / 98400 12345 / +91 98400 12345 / 09840012345, missing, changed
  dob      ISO or dd/mm/yyyy, day and month swapped, year off by one, missing
  address  St / Street, Rd / Road, area spelling (Velachery / Velacheri), moved house
  pincode  missing, one digit wrong
  exact    a few rows saved twice by the desk software
Hard non-matches (different people who look alike):
  twins            same initial, dob, address and phone; different given name
  father and son   same name, address and phone; dob 25 to 35 years apart
  common names     unrelated people with the same name in different areas
"""
import numpy as np, pandas as pd

rng = np.random.default_rng(2402)
R = lambda p: rng.random() < p
pick = lambda xs: xs[rng.integers(len(xs))]

AREAS = {  # area: (pincode, spellings)
    'Velachery': ('600042', ['Velachery', 'Velacheri']),
    'Adyar': ('600020', ['Adyar', 'Adayar']),
    'T. Nagar': ('600017', ['T. Nagar', 'T Nagar', 'Thyagaraya Nagar']),
    'Anna Nagar': ('600040', ['Anna Nagar', 'Annanagar']),
    'Mylapore': ('600004', ['Mylapore', 'Mylapur']),
    'Tambaram': ('600045', ['Tambaram']),
    'Porur': ('600116', ['Porur']),
    'Guindy': ('600032', ['Guindy', 'Gindy']),
    'Kodambakkam': ('600024', ['Kodambakkam', 'Kodambakam']),
    'Perambur': ('600011', ['Perambur']),
    'Chromepet': ('600044', ['Chromepet', 'Chrompet']),
    'Saidapet': ('600015', ['Saidapet', 'Saidapettai']),
}
STREETS = ['Gandhi Street', 'Nehru Road', 'Kamarajar Salai', '2nd Main Road', 'Bharathi Street',
           'Lake View Road', 'Church Street', 'Temple Street', '4th Cross Street', 'Market Road',
           'Big Street', 'Station Road']
ABBR = [('Street', 'St'), ('Road', 'Rd')]

TA_M = ['Senthil Kumar', 'Ramesh', 'Suresh', 'Karthik', 'Sathish', 'Ganesh', 'Murugan', 'Arun',
        'Vijay', 'Prakash', 'Balaji', 'Saravanan', 'Venkatesan', 'Gopal', 'Rajesh', 'Dinesh',
        'Manikandan', 'Selvam', 'Anand', 'Sridhar', 'Ram Kumar', 'Ravi Kumar']
TA_F = ['Lakshmi', 'Priya', 'Deepa', 'Kavitha', 'Shanthi', 'Meena', 'Revathi', 'Jayalakshmi',
        'Divya', 'Saranya', 'Gayathri', 'Anitha', 'Malathi', 'Vasanthi', 'Sangeetha', 'Nithya',
        'Bhuvana', 'Sumathi']
NO_M = ['Rahul', 'Amit', 'Rohit', 'Vikram', 'Sanjay', 'Arjun', 'Nikhil']
NO_F = ['Pooja', 'Neha', 'Anjali', 'Sneha', 'Riya']
NO_S = ['Sharma', 'Gupta', 'Singh', 'Verma', 'Agarwal', 'Jain', 'Mehta']
SO_M = ['Venkata Ramana', 'Srinivasa', 'Anil', 'Suresh', 'Joseph', 'Mohammed', 'Abdul']
SO_F = ['Lakshmi', 'Fathima', 'Ayesha', 'Mary', 'Sujatha', 'Anitha']
SO_S = {'Venkata Ramana': ['Reddy', 'Rao'], 'Srinivasa': ['Rao', 'Murthy', 'Reddy'], 'Anil': ['Nair', 'Menon', 'Kumar'],
        'Suresh': ['Pillai', 'Naidu', 'Menon'], 'Joseph': ['Xavier', 'Antony', 'Mathew'],
        'Mohammed': ['Ismail', 'Yusuf', 'Rafi', 'Irfan'], 'Abdul': ['Rahman', 'Kareem', 'Majeed'],
        'Lakshmi': ['Menon', 'Nair', 'Iyer'], 'Fathima': ['Begum', 'Beevi', 'Nasreen'],
        'Ayesha': ['Banu', 'Siddiqui', 'Parveen'], 'Mary': ['Thomas', 'George', 'Joseph', 'Mathew'],
        'Sujatha': ['Reddy', 'Rao'], 'Anitha': ['Pillai', 'Kumari', 'Nair']}
SPELL = {'Lakshmi': 'Laxmi', 'Mohammed': 'Mohamed', 'Karthik': 'Karthick', 'Sathish': 'Satish',
         'Deepa': 'Dheepa', 'Shanthi': 'Santhi', 'Jayalakshmi': 'Jaya Lakshmi', 'Gayathri': 'Gayatri',
         'Kavitha': 'Kavita', 'Anitha': 'Anita', 'Fathima': 'Fatima', 'Saravanan': 'Sharavanan',
         'Srinivasa': 'Sreenivasa', 'Sangeetha': 'Sangita', 'Nithya': 'Nitya', 'Sumathi': 'Sumati',
         'Revathi': 'Revati', 'Vasanthi': 'Vasanti', 'Senthil Kumar': 'Senthilkumar',
         'Venkata Ramana': 'Venkataramana', 'Reddy': 'Reddi', 'Ram Kumar': 'Ramkumar',
         'Ravi Kumar': 'Ravikumar', 'Ismail': 'Ismayil'}
LETTERS = 'ABDGJKMNPRSTV'


def new_person(style=None):
    style = style or pick(['ta'] * 6 + ['no'] * 2 + ['so'] * 2)
    sex = 'M' if R(.5) else 'F'
    if style == 'ta':
        given = pick(TA_M if sex == 'M' else TA_F)
        p = dict(style='ta', given=given, initial=pick(LETTERS), surname=None)
    elif style == 'no':
        p = dict(style='no', given=pick(NO_M if sex == 'M' else NO_F), initial=None, surname=pick(NO_S))
    else:
        given = pick(SO_M if sex == 'M' else SO_F)
        p = dict(style='so', given=given, initial=None, surname=pick(SO_S[given]))
    area = pick(list(AREAS))
    p.update(sex=sex,
             dob=pd.Timestamp('1950-01-01') + pd.Timedelta(days=int(rng.integers(0, 365 * 55))),
             phone=pick(['9', '8', '7', '6']) + ''.join(str(d) for d in rng.integers(0, 10, 9)),
             door=int(rng.integers(1, 120)), street=pick(STREETS), area=area)
    return p


def canon_name(p):
    if p['style'] == 'ta':
        return f"{p['initial']}. {p['given']}"
    return f"{p['given']} {p['surname']}"


def typo(s):
    i = int(rng.integers(1, len(s) - 1))
    if not s[i].isalpha() or not s[i - 1].isalpha():
        return s
    k = rng.integers(3)
    if k == 0:   # swap two neighbours
        return s[:i - 1] + s[i] + s[i - 1] + s[i + 1:]
    if k == 1:   # drop one letter
        return s[:i] + s[i + 1:]
    return s[:i] + s[i] + s[i:]   # double one letter


def vary_name(p):
    g, sn, ini = p['given'], p['surname'], p['initial']
    if R(.35):
        g = SPELL.get(g, g)
        if sn:
            sn = SPELL.get(sn, sn)
    if p['style'] == 'ta':
        form = pick(['{i}. {g}', '{i} {g}', '{g} {i}', '{g} {i}.', '{g}'] + ['{i}. {g}'] * 2)
        n = form.format(i=ini, g=g)
    else:
        form = pick(['{g} {s}'] * 4 + ['{s} {g}', '{s}, {g}', '{g0}. {s}'])
        n = form.format(g=g, s=sn, g0=g[0])
    if R(.15):
        n = typo(n)
    if R(.08):
        n = pick(['Mr. ', 'Dr. '] if p['sex'] == 'M' else ['Mrs. ', 'Ms. ', 'Dr. ']) + n
    if R(.25):
        n = n.upper()
    return n


def fmt_phone(ph):
    return pick([ph, ph, f'{ph[:5]} {ph[5:]}', f'+91 {ph[:5]} {ph[5:]}', f'+91-{ph}', f'0{ph}'])


def fmt_dob(d):
    return d.strftime('%Y-%m-%d') if R(.7) else d.strftime('%d/%m/%Y')


def fmt_addr(p, vary):
    st, area = p['street'], p['area']
    a_txt = AREAS[area][1][0]
    door = f"{p['door']}"
    if vary:
        for full, ab in ABBR:
            if full in st and R(.5):
                st = st.replace(full, ab + pick(['', '.']))
        a_txt = pick(AREAS[area][1])
        door = pick([door, f'No.{door}', f'No. {door}'])
    return f'{door}, {st}, {a_txt}'


def record(p, first):
    pin = AREAS[p['area']][0]
    r = dict(name=canon_name(p) if first else vary_name(p),
             sex=p['sex'], dob=p['dob'].strftime('%Y-%m-%d'),
             phone=p['phone'], address=fmt_addr(p, not first), pincode=pin)
    if not first:
        if R(.15): r['sex'] = pick({'M': ['Male', 'm', ''], 'F': ['Female', 'f', '']}[p['sex']])
        if R(.05) and p['dob'].day <= 12:
            r['dob'] = p['dob'].strftime('%Y-%d-%m')               # day and month swapped
        elif R(.10):
            r['dob'] = ''
        elif R(.04):
            r['dob'] = fmt_dob(p['dob'] + pd.DateOffset(years=pick([-1, 1])))   # year typed wrong
        else:
            r['dob'] = fmt_dob(p['dob'])
        if R(.10): r['phone'] = ''
        elif R(.07): r['phone'] = pick(['9', '8', '7']) + ''.join(str(d) for d in rng.integers(0, 10, 9))
        else: r['phone'] = fmt_phone(p['phone'])
        if R(.08): r['pincode'] = ''
        elif R(.04): r['pincode'] = pin[:-1] + str((int(pin[-1]) + 1) % 10)
    return r


people = [new_person() for _ in range(330)]

# hard non-matches
twins = []
for _ in range(3):
    a = new_person('ta'); b = dict(a)
    b['given'] = pick([x for x in (TA_M if b['sex'] == 'M' else TA_F) if x != a['given']])
    twins += [a, b]
fathers = []
for _ in range(2):
    s = new_person('ta'); s['sex'] = 'M'; s['given'] = pick(TA_M)
    f = dict(s); f['dob'] = s['dob'] - pd.Timedelta(days=int(rng.integers(25 * 365, 35 * 365)))
    fathers += [f, s]
commons = []
for _ in range(4):                      # four unrelated S. Priya
    c = new_person('ta'); c.update(sex='F', given='Priya', initial='S'); commons.append(c)
for _ in range(3):                      # three unrelated Mohammed Ismail
    c = new_person('so'); c.update(sex='M', given='Mohammed', surname='Ismail'); commons.append(c)
people += twins + fathers + commons

# moves: some people change house or number between visits
rows = []
for pid, p in enumerate(people, 1):
    k = 1 + (R(.32)) + (R(.12)) + (R(.04))
    for v in range(k):
        q = p
        if v > 0 and R(.07):
            q = dict(p); q['area'] = pick(list(AREAS)); q['street'] = pick(STREETS)
            q['door'] = int(rng.integers(1, 120))
        r = record(q, v == 0)
        r['person_id'] = pid
        r['registered_on'] = (pd.Timestamp('2021-01-01') + pd.Timedelta(days=int(rng.integers(0, 1700))))
        rows.append(r)

# the desk software saved some registrations twice
for i in rng.choice(len(rows), 12, replace=False):
    rows.append(dict(rows[i]))

df = pd.DataFrame(rows).sample(frac=1, random_state=2402).reset_index(drop=True)
df = df.sort_values('registered_on', kind='stable').reset_index(drop=True)
df['registered_on'] = df.registered_on.dt.strftime('%Y-%m-%d')
df.insert(0, 'rec_id', np.arange(1001, 1001 + len(df)))
df = df[['rec_id', 'registered_on', 'name', 'sex', 'dob', 'phone', 'address', 'pincode', 'person_id']]
df.to_csv('patients.csv', index=False)
print(len(df), 'records,', df.person_id.nunique(), 'people')
