##########################
### Account Controller ###
##########################

## Deal with all the following functionalities relating to accounts
## 1. account creation/registration
## 2. account confirmation
## 3. profile creation/editing

def register():
	form = SQLFORM.factory(
		Field('email', requires=IS_NOT_EMPTY()),
		Field('pwd', requires=[IS_NOT_EMPTY(), IS_STRONG(min=6, special=0, upper=1), CRYPT()]),
		Field('re_pwd', requires=IS_MATCH(form.vars.pwd)))
	if form.process().accepted:
		session.email = form.vars.email
		session.pwd = form.vars.pwd
		redirect(URL('registered'))
	return dict(form=form)

def registered():
	if not request.function=='register' and not session.email:
		redirect(URL('register'))
	return dict()

