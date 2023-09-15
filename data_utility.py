class DataUtility:
    def __init__(self ):
        self.team_name_list = [
            'ב. ירושלים',
            'מ. אשדוד',
            'ה. ב. שבע',
            'ב. סכנין',
            'מ. חיפה',
            'ה. ירושלים',
            'ה. פ. תקווה',
            'ה. חיפה',
            'ה. ת. אביב',
            'מ. פ. תקווה',
            'מ. ת. אביב',
            'מ. ב. ריינה',
            'מ. נתניה',
            'ה. חדרה'
        ]
        self.full_team_name_list = ['מכבי פתח תקווה', 'הפועל חיפה', 'מכבי נתניה', 'הפועל ירושלים', 'בני סכנין', 'מכבי חיפה', 'מכבי בני ריינה', 'מכבי תל אביב', 'בית"ר ירושלים', 'מ.ס. אשדוד', 'הפועל חדרה', 'הפועל תל אביב', 'הפועל פתח תקווה', 'הפועל באר שבע']
        self.stats_hebrew_english = {
            'בישולים': 'Assists',
            'פנדלים שגרם': 'Penalties Caused',
            'לא ספג שערים': 'Clean Sheets',
            'פנדלים שנסחטו': 'Penalties Saved',
            'שערים': 'Goals Scored',
            'שערים שספג': 'Goals Conceded',
            'דקות משחק': 'Minutes Played',
            'הרכב פותח': 'Starting Lineup',
            'שערים עצמיים': 'Own Goals',
            'פנדלים שהחמיץ': 'Penalties Missed',
            'פנדלים שנעצרו': 'Penalties Stopped',
            'כרטיסים אדומים': 'Red Cards',
            'נכנס בחילוף': 'Substituted In',
            'יצא בחילוף': 'Substituted Out',
            'כרטיסים צהובים': 'Yellow Cards'
        }
        self.position_mapping = {
            'שוער': 'GK',
            'מגן/בלם': 'CB',
            'קשר': 'MD',
            'חלוץ': 'FW'
        }