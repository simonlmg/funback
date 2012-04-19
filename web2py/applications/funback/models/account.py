#########################################
## database model for account services ##
#########################################

## use PostgreSQL on dotcloud (staging/production)
##db = DAL("pgsql://root:kZ2AxFUntkfwlBGCEa1N@funback-Cilia.dotcloud.com:21133")

## use PostgreSQL on localhost (testing/qa)
db = DAL("postgres://cyan:opennow330@localhost/funback")

## setup logging facilities for debugging purposes
import logging
logger = logging.getLogger("web2py.app.funback")
logger.setLevel(logging.DEBUG)

#####################################
## web2py authentication utilities ##
#####################################

from gluon.tools import Auth
auth = Auth(db, hmac_key=Auth.get_or_create_key())

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'funback.message@gmail.com'
mail.settings.login = 'funback.message:opennow123'

## for the use of reCAPTCHA (with publicly visible site only)
#auth.settings.captcha = Recaptcha(request, 'PUBLIC_KEY', 'PRIVATE_KEY', option="theme:'clean', lang:'en'")

## re-name the authentication tables
auth.settings.table_user_name = "user_login"
auth.settings.table_group_name = "user_group"
auth.settings.table_membership_name = "user_membership"
auth.settings.table_permission_name = "user_permission"
auth.settings.table_event_name = "user_event"

## create all tables needed by Auth
auth.define_tables()

## disable the default group creation behavior upon each user creation
auth.settings.create_user_groups = False
## turn on email verification upon registration and password reset
auth.settings.registration_requires_verification = True
auth.settings.reset_password_requires_verification = True
## might need to change this for company users
#auth.settings.registration_requires_approval = False 

## set the content of the verification email
auth.messages.verify_email = 'Please click on the link: http://' + \
     request.env.http_host + \
     URL(r=request, c='account', f='verify_email') + \
     '/%(key)s to verify your email address'
logger.debug("verification email content: %s" % auth.messages.verify_email)

## customize the Auth tables
## abandon (but not remove) 'first_name' and 'last_name' from user_login table

db.user_login.first_name.writable = db.user_login.last_name.writable = False
db.user_login.first_name.readable = db.user_login.last_name.readable = False
## set the email requirement
db.user_login.email.requires = [IS_NOT_EMPTY(), 
                             IS_EMAIL(),
                             IS_NOT_IN_DB(db, 'user_login.email')]
#forced='^.*\.edu(|\..*)$', error_message='Email must be an .edu address' 
 
## set the password requirement
db.user_login.password.requires = [IS_NOT_EMPTY(), 
                                IS_STRONG(min=7, special=0, upper=0, number=0, error_message='Minimum 7 characters'), 
                                CRYPT()]

## setup the user group structure (should be setup one-for-all outside the app)
#auth.add_group('prospect', 'participants of events')
#auth.add_group('prospector', 'hosts of events')

######################
## Custom DB tables ##
######################

#db.define_table('login',
#    Field('email', length=96, required=True, unique=True),
#    Field('pwd', length=36, required=True, readable=False, writable=False))

#db.login.email.requires=[IS_EMAIL(), IS_NOT_IN_DB(db, 'login.email')]
#db.login.pwd.requires=[IS_NOT_EMPTY(), IS_STRONG(min=6, special=0, upper=1), CRYPT()]

db.define_table('participant',
    Field('login_id', db.user_login, readable=False, writable=False),
    Field('first_name', length=128, required=True),
    Field('last_name', length=128, required=True),
    Field('sex', required=True),
    Field('dob', 'date'),
    Field('country'),
    format='%(first_name)s %(last_name)s')

db.participant.sex.requires = IS_IN_SET(['male','female'])
db.participant.country.requires = IS_IN_SET(['United States','United Kingdom'])
db.participant.login_id.requires = IS_IN_DB(db, db.user_login.id, '%(email)s')