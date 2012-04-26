##########################
### Account Controller ###
##########################

## Deal with all the following functionalities relating to accounts
## 1. account creation/registration
## 2. email confirmation
## 3. rest password
## 4. change password

#===============================================================================
# Use the Auth functions provided by Web2py
# use @auth.requires_login()
# @auth.requires_membership('group name')
# @auth.requires_permission('read','table name',record_id)
# to decorate functions that need access control
#===============================================================================


def register():
    """
    exposes:
    http://..../[app]/account/register
    """
    
    if (request.args(0) != 'prospect' and request.args(0) != 'prospector'):
        redirect(URL(c='default', f='index'))
    
    session.from_register = True
    session.register_arg = request.args(0)
    form = auth.register()
       
    return dict(form=form)

def verify_email():
    """
    exposes:
    http://..../[app]/account/verify_email
    """
    return dict(form=auth.verify_email())

def login():
    """
    exposes:
    http://..../[app]/account/login
    """
    return dict(form=auth.login())

def logout():
    """
    exposes:
    http://..../[app]/account/logout
    """
    return dict(form=auth.logout())

def retrieve_password():
    """
    exposes:
    http://..../[app]/account/retrieve_password
    """
    return dict(form=auth.retrieve_password())

def change_password():
    """
    exposes:
    http://..../[app]/account/change_password
    """
    return dict(form=auth.change_password())



#===============================================================================
# def register():
#    form = SQLFORM.factory(
#        Field('email', requires=[IS_NOT_EMPTY(), 
#                                IS_EMAIL(forced='^.*\.edu(|\..*)$', error_message='email must be .edu address')]),
#        Field('password', 'password', requires=[IS_NOT_EMPTY(), 
#                                            IS_STRONG(min=7, special=0, upper=0, number=0, error_message='minimum 7 characters'), 
#                                            CRYPT()]),
#        Field('re_password', 'password', requires=[IS_EXPR('value==%s' % repr(request.vars.get('password', None)), error_message='Passwords do not match'), 
#                                                CRYPT()]),
#        submit_button='Sign up')
#    if form.process().accepted:
#        session.email = form.vars.email
#        session.pwd = form.vars.pwd
#        redirect(URL('registered'))
#    return dict(form=form)
#===============================================================================

def registered():
    
    logger.debug('from_register: %s and session.registered: %s' % (session.from_register, session.registered))

    if not session.from_register:
        logger.debug('request NOT from registration page')
        session.from_register = False
        redirect(URL(c='default', f='index'))
    elif not session.registered_email:
        logger.debug('request from registration page but form not processed')
        session.from_register = False
        redirect(URL(f='register', args=[session.register_arg]))
                
    return dict()


@auth.requires_login()
def profile():
    participant=db(db.participant.user_id==auth.user_id).select().first()
    if(participant==None):
        db.participant.user_id.default=auth.user_id
        form=crud.create(db.participant,next=URL('education'))
    else:
        crud.settings.update_deletable = False
        form=crud.update(db.participant,participant.id,next=URL('education'))
    return dict(form=form)
    
    
    
@auth.requires_login()
def education():
    edu=crud.select(
       db.participant_edu,db.participant_edu.user_id==auth.user_id,orderby=db.participant_edu.Start_Year)
    db.participant_edu.user_id.default=auth.user_id
    form=crud.create(db.participant_edu,next=URL('education'))
    return dict(eduinfo=edu,form=form)
    
@auth.requires_login()
def skills():
    skills=crud.select(
       db.participant_skill,db.participant_skill.user_id==auth.user_id)
    db.participant_skill.user_id.default=auth.user_id
    form=crud.create(db.participant_skill,next=URL('skills'))
    return dict(skills=skills,form=form)
    
@auth.requires_login()
def experience():
    exp=crud.select(
       db.participant_exp,db.participant_exp.user_id==auth.user_id,orderby=db.participant_exp.Start_Date)
    db.participant_exp.user_id.default=auth.user_id
    form=crud.create(db.participant_exp,next=URL('experience'))
    return dict(exp=exp,form=form)