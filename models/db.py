# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
#response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.formstyle = 'bootstrap3_stacked' # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager, Crud
import datetime

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()
crud = Crud(db)


# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=True, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.actions_disabled=['register','change_password','request_reset_password','profile', 'retrieve_username']
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

db.define_table('tag',
               Field('tagName', 'string', unique=True),
               Field('isModerated', 'boolean', default = False),
               format='%(tagName)s')

db.define_table('events',
                Field('eventName', 'string', label="Event's Name (*)", requires=IS_NOT_EMPTY()),
                Field('startAt', 'datetime', label="Starts At (*)", requires=[IS_NOT_EMPTY(),IS_DATETIME_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'),error_message='Wrong Date')]),
                Field('endAt', 'datetime', label="Ends At"),
                Field('venue', 'string', label="Venue"),
                Field('contact', 'string', label="Contact"),
                Field('description', 'text', label="Description (*)", requires=IS_NOT_EMPTY()),
                Field('link', 'string', label="Webpage link"),
    
                Field('typeOfEvent', 'string', label="Event Tag (*)", requires = IS_IN_SET(['Academic', 'Cultural', 'Sports', 'Holiday', 'Other', 'Urgent'])),
                auth.signature,
                format='%(eventName)s')

db.define_table('Venue',Field('name'))
db.events.venue.widget = SQLFORM.widgets.autocomplete(
     request, db.Venue.name, limitby=(0,10), min_length=2)

db.define_table('userTag',
                Field('auth_user', db.auth_user, readable=False, writable=False),
                Field('tag', db.tag))

db.define_table('Moderators',
                Field('auth_user', db.auth_user, readable=False, writable=False),
                Field('tag', db.tag))

db.define_table('eventTag',
                Field('tag', db.tag),
                Field('isApproved', 'integer', readable=False, writable=False, default=0),
                Field('events', db.events))

from gluon.contrib.login_methods.ldap_auth import ldap_auth
auth.settings.login_methods.append(ldap_auth(mode='uid_r', server='ldap.iiit.ac.in',
    manage_user=True,
   base_dn='OU=Users,DC=iiit,DC=ac,DC=in',
   logging_level='debug',
   user_firstname_attrib='cn:1',user_lastname_attrib='cn:2',user_mail_attrib='mail',db=db))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
