###########################################
### database model for account services ###
###########################################

## use PostgreSQL on dotcloud (staging/production)
##db = DAL("pgsql://root:kZ2AxFUntkfwlBGCEa1N@funback-Cilia.dotcloud.com:21133")

## setup logging facilities for debugging purposes
import logging
logger = logging.getLogger("web2py.app.funback")
logger.setLevel(logging.DEBUG)

## use PostgreSQL on localhost (testing/qa)
db = DAL("postgres://cyan:opennow330@localhost/funback")


########################
### Custom Functions ###
########################

def grant_permissions(form):
    logger.debug("permission granting reached")
    group_id = auth.id_group(role=request.args(0))
    logger.debug("group id for registrant: " + str(group_id))
    logger.debug("user id for registrant: " + str(form.vars.id))
    auth.add_membership(group_id, form.vars.id)
    session.registered_email = form.vars.email
    logger.debug("permission granted")
    
def program_login(user):
    logger.debug("log in user programmatically")
    logger.debug("temporarily remove CRYPT validator on 'password' filed of 'user_login' table")
    ## assuming the last added validator is CRYPT
    crypt_validator = db.user_login.password.requires.pop()
    logger.debug("manual login")
    auth.login_bare(user.email, user.password)
    logger.debug("re-add CRYPT validator")
    db.user_login.password.requires.append(crypt_validator)
    

#######################################
### web2py authentication utilities ###
#######################################

from gluon.tools import Auth
auth = Auth(db, hmac_key=Auth.get_or_create_key())

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'Funback Messsage <funback.message@gmail.com>'
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

## specify the page workflow for registration process
auth.settings.register_onaccept.append(grant_permissions)
auth.settings.register_next = URL('registered')
auth.settings.verify_email_onaccept.append(program_login)
auth.settings.verify_email_onaccept.append(lambda user: mail.send(to=user.email, subject='Welcome to Funback', 
                                                                  message='Hello %s' % user.email))
auth.settings.verify_email_next = URL('profile')

## specify the page workflow after a user is logged in
auth.settings.logged_url = URL('profile') # for now

## set some registration labels
auth.messages.verify_password_comment = 'Please re-type your password'
messages.verify_email_subject = 'Email Verification'

## set the content of the verification email
auth.messages.verify_email = 'Please click on the link: http://' + \
                            request.env.http_host + \
                            URL(r=request, c='account', f='verify_email') + \
                            '/%(key)s to verify your email address'

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


########################
### Custom DB tables ###
########################

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
