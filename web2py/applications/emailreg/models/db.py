##############################
## database model (funback) ##
##############################

## use PostgreSQL database
db = DAL("pgsql://root:kZ2AxFUntkfwlBGCEa1N@funback-Cilia.dotcloud.com:21133")

############################ table definitions #############################
db.define_table('login',
	Field('email', length=96, required=true, unique=true),
	Field('pwd', length=36, required=true, readable=False, writable=False))

db.define_table('participant',
	Field('login_id', db.login, readable=False, writable=False),
	Field('first_name', length=128, required=true),
	Field('last_name', length=128, required=true),
	Field('sex', required=true),
	Field('dob', 'date'),
	Field('country'),
	Field('verified', 'boolean', default=False),
	format='%(first_name)s %(last_name)s')

db.login.email.requires=[IS_EMAIL(), IS_NOT_IN_DB(db, 'login.email')]
db.login.pwd.requires=[IS_NOT_EMPTY(), IS_STRONG(min=6, special=0, upper=1), CRYPT()]

db.participant.sex=IS_IN_SET(('male','female'))
db.participant.country=IS_IN_SET(('United States','United Kingdom'))
db.participant.login_id=IS_IN_DB(db, db.login.id, '%(email)s')

############################ table definitions #############################

############################ utilities #############################

from gluon.tools import Auth
auth = Auth(db, hmac_key=Auth.get_or_create_key())

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'funback.message@gmail.com'
mail.settings.login = 'funback.message:opennow123'


############################ utilities #############################