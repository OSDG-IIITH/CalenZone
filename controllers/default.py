# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

@auth.requires_login()
def profile():
    form = SQLFORM(db.userTag)
    #dn=db(db.auth_user.id==request.args[0]).select()
    tags = db(db.auth_user.id==db.userTag.auth_user and db.tag.id==db.userTag.tag).select(db.auth_user.email, db.tag.tagName)
    form.vars.auth_user = session.auth.user.id
    if form.process().accepted:
        response.flash = T("Tag Added!")
    return dict(form=form, tags=tags)

@auth.requires_login()
def createEvent():
    form = SQLFORM(db.events)
    form.vars.ownerOfEvent = session.auth.user.id
    if form.process().accepted:
        response.flash = T("Event Created!")
        redirect(URL('showEvent', args=[4]))
    return dict(form=form)

@auth.requires_login()
def setEventTags():
    form = SQLFORM(db.eventTag)
    if form.process().accepted:
        response.flash = T("Tag added!")
    return dict(form=form)

def showEvent():
    event = db(db.events.auth_user == request.args[0]).select()
    return locals();

@auth.requires_login()
def eventView():
    ##db(db.userTag.auth_user==session.auth.user.id).select()
    tags=db(db.userTag.auth_user==session.auth.user.id).select(db.userTag.tag)
    events = []
    blah = tags[0]
    for taga in tags:
        events = db(db.eventTag.tag == taga).select(db.events.eventName)
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
