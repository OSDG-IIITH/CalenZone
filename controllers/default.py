# -*- coding: utf-8 -*-

#########################################################################
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

import time
import datetime
import csv

UNREMOVABLE_GROUPS = ["All", "Students", "Reasearch", "Faculty"]

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to IIIT Calendar Portal")
    redirect(URL('calendar'))
    return dict(title='Please Log in')


@auth.requires_login()
def search():
    query = db.userTag.tag == db.eventTag.tag
    query &= (db.userTag.auth_user == session.auth.user.id)
    query &= (db.events.id == db.eventTag.events)
    res = db(query).select(db.events.ALL)
    return dict(res=res)


def iCal():
    useremail = request.args[0]
    userid = db(db.auth_user.email==useremail).select(db.auth_user.id)[0]
    
    q1 = db.userTag.tag == db.eventTag.tag
    q2 = db.userTag.auth_user == userid
    q3 = db.events.id == db.eventTag.events
    events = db((q1 & q2 & q3)).select(db.events.ALL,distinct=True)
    
    title = "IIIT CALENDAR"
    exported_data = \
    """BEGIN:VCALENDAR
    VERSION:2.0
    X-WR-CALNAME:%s
    SUMMARY:%s
    PRODID:-//Generated by RSScal//web2py 2011
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    """ % (title, title)

    date_format = '%Y%m%dT%H%M%SZ'

    for item in events:
        exported_data += \
        """BEGIN:VEVENT
        UID:%s
        URL:%s
        DTSTART:%s
        DTEND:%s
        SUMMARY:%s
        END:VEVENT
        """ % (item.id, item['link'], item['startAt'].strftime(date_format), item['endAt'].strftime(date_format), item['eventName'])
    exported_data += "END:VCALENDAR"
    return exported_data


@auth.requires_login()
def profile():
    form = SQLFORM(db.userTag)
    # Get tag names for display in view
    temp = db(db.userTag.auth_user == session.auth.user.id).select()
    mytags = []
    mytags += [(db.tag[i.tag].tagName, i.id) for i in temp]
    # Get tag ids to check for duplicates
    mtags = []
    mtags += [db.tag[i.tag].id for i in temp]
    form.vars.auth_user = session.auth.user.id
    grid = SQLFORM.grid(db.events.created_by == session.auth.user.id)
    if form.process().accepted:
        # If the tag already exits, delete the new duplicate entry
        if form.vars.tag in mtags:
            session.flash = T("Tag already added!")
            db(db.userTag.id == form.vars.id).delete()
        else:
            session.flash = T("Tag Added!")
        redirect(URL())
    return locals()


@auth.requires_login()
def importEvents():
    groups = db(db.tag.id>0).select()
    grp_dict = {}
    for a in groups:
        grp_dict[a.tagName]=a.id

    if request.vars.csvfile != None:
        file = request.vars.csvfile.file
        csvdata = csv.reader(file)
        for arr in csvdata:
            id = db.events.insert(**db.events._filter_fields({
                "eventName":arr[0],
                "startAt":arr[1],
                "endAt":arr[2],
                "venue":arr[3],
                "contact":arr[4],
                "description":arr[5],
                "link":arr[6],
                "typeOfEvent":arr[7],
                "created_by":session.auth.user.id,
                "created_at":datetime.datetime.utcnow()
                }))
            grps = arr[8].split(";")
            for grp in grps:
                db.eventTag.insert(**db.eventTag._filter_fields({
                    "tag":grp_dict[grp.strip()],
                    "events":id
                    }))

    return dict()


def checkMail():
    "Place holder function to test scheduler. To be removed in deployment."
    generate_reminder()


@auth.requires_login()
def deleteGroup():
    try:
        group = request.args[0]
    except IndexError:
        session.flash = "Incorrect Url: No parameters"
        redirect(URL('profile'))
    if group in UNREMOVABLE_GROUPS:
        session.flash = "You cannot remove yourself from this group!"
        redirect(URL('profile'))
    group = db(db.tag.tagName == group)
    if group.count() == 0:
        session.flash = "Non existant group!"
        redirect(URL('profile'))
    tag_id = group.select()[0].id
    userTagRow = db((db.userTag.tag == tag_id) & (db.userTag.auth_user == session.auth.user))
    if userTagRow.count() == 0:
        session.flash = "You are already not in this group!"
    else:
        crud.delete(db.userTag, userTagRow.select()[0].id)
    redirect(URL('profile'))
    return


def groupNameFormatter(x):
    y = ""
    for i in x:
        y = y + "\'" + str(i.tagName) + "\'"
        y = y + ","
    if y != "":
        y = y[:-1]
    return y


@auth.requires_login()
def createEvent():
    form = SQLFORM(db.events)
    form.vars.created_by = session.auth.user.id

    ##adding group names
    x = db(db.tag).select(db.tag.tagName)
    y = groupNameFormatter(x)

    ##Processing Form
    ##auto setting end date
    if request.post_vars.startAt:
        if request.post_vars.endAt == "":
            try:
                form.vars.endAt = datetime.datetime.strptime(request.vars.startAt,
                                                         '%Y-%m-%d %H:%M:%S') + datetime.timedelta(0, 3600)
                request.post_vars.endAt = str(datetime.datetime.strptime(request.vars.startAt, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(0, 3600))
            except:
                response.flash += "Invalid Date Format: Start At"
                form.errors = True
                ##if request.vars["startAt"]
        else:
            try:
                datetime.datetime.strptime(request.vars.startAt, '%Y-%m-%d %H:%M:%S') > datetime.datetime.strptime(
                request.vars.endAt, '%Y-%m-%d %H:%M:%S')
                form.errors = True
                response.flash += "End before start!"
            except:
                response.flash += "Invalid Date Format: End At"
                form.errors = True

    ##Checking if groups are in db

    if request.vars.groups:
        groups = request.vars.groups.split(", ")
        # testcase1
        for group in groups:
            if len(db(db.tag.tagName == group).select(db.tag.id)) == 0:
                response.flash += "Invalid Group Name!"
                form.errors = True
        # testcase2
        if len(groups) != len(set(groups)):
            response.flash += "Multiple groups of same name!"
            form.errors = True

    if not form.errors:
        if form.process().accepted:
            response.flash = "Event created successfully"
            groups = request.vars.groups.split(", ")
            for group in groups:
                gr_id = db(db.tag.tagName == group).select(db.tag.id)[0].id
                response.flash += ":" + str(gr_id)
                db.eventTag.insert(tag=gr_id, events=form.vars.id)
            redirect(URL('calendar'))
    return dict(form=form, grouplist=T(y))


@auth.requires_login()
def changeTags():
    try:
        request.args[0]
    except IndexError:
        redirect(URL('myEvents'))
    form_id = request.args[0]

    ##adding group names
    x = db(db.tag).select(db.tag.tagName)
    y = groupNameFormatter(x)
    q1 = db.eventTag.events == form_id
    q2 = db.tag.id == db.eventTag.tag
    # currentTags = groupNameFormatter(db(q1 & q2).select(db.tag.tagName))
    z = db(q1 & q2).select(db.tag.tagName)
    currentTags = ""
    for i in z:
        currentTags=currentTags+i.tagName + ","
    if request.vars.groups:
        db(db.eventTag.events == form_id).delete()
        groups = request.vars.groups.split(", ")
        for group in groups:
            gr_id = db(db.tag.tagName == group).select(db.tag.id)[0].id
            db.eventTag.insert(tag=gr_id, events=form_id)
        redirect(URL('myEvents'))
    return dict(grouplist=T(y), currentTags=currentTags)


@auth.requires_login()
def setEventTags():
    myevents = db(db.events.created_by == session.auth.user.id).select(db.events.id)
    temp = [i for i in myevents]
    form = SQLFORM.grid(db.eventTag.events.belongs(temp))
    # if form.process().accepted:
    #    response.flash = T("Tag added!")
    return locals()


def showEvent():
    event = db(db.events.auth_user == request.args[0]).select()[0]
    return locals();


def showDes():
    des = db(db.events.id == request.args[0]).select(db.events.description, db.events.startAt, db.events.endAt,
                                                     db.events.link, db.events.contact, db.events.eventName,
                                                     db.events.venue)[0]
    return dict(des=des)


@auth.requires_login()
def myEvents():
    events = db(db.events.created_by == session.auth.user.id).select()
    tagarr = []
    for event in events:
        x = db(db.tag).select(db.tag.tagName)
        y = groupNameFormatter(x)
        q1 = db.eventTag.events == event.id
        q2 = db.tag.id == db.eventTag.tag
        currentTags = groupNameFormatter(db(q1 & q2).select(db.tag.tagName))
        tagarr.append(currentTags)
    return locals()


@auth.requires_login()
def editEvent():
    try:
        request.args[0]
    except IndexError:
        redirect(URL('myEvents'))
    eventId = request.args[0]
    try:
        created_by = db(db.events.id == eventId).select(db.events.created_by)[0].created_by
    except IndexError:
        redirect(URL('myEvents'))
    if created_by != session.auth.user.id:
        redirect(URL('myEvents'))
    # form1=crud.update(db.events,eventId)
    # crud.settings.update_next = URL('myEvents')
    record = db.events(eventId)
    form = SQLFORM(db.events, record)
    if form.process().accepted:
        redirect(URL('myEvents'))
    return dict(form=form)


def gen_mail():
    response.view = 'default/index.html'
    return locals()


def calendar():
    if session.auth != None:
        useremail = db(db.auth_user.id==session.auth.user.id).select(db.auth_user.email)[0].email
        check = db((db.userTag.auth_user == session.auth.user.id) & (db.userTag.tag == db.tag.id) & (db.tag.tagName == "All")).count()
        if check == 0:
            db.userTag.insert(auth_user=session.auth.user.id, tag=1)
    else:
        useremail = "Not Logged in"
    return locals()


@auth.requires_login()
def deleteEvent():
    event_id = request.args[0]
    event = db.events[event_id]
    if event == None:
        session.flash = "Event does not exist!"
        redirect(URL('myEvents'))
    if event.created_by == session.auth.user.id:
        session.flash = "Event deleted!"
        db(db.events.id == event_id).delete()
    else:
        session.flash = "You do no have permission to delete this event!"
    redirect(URL('myEvents'))


def eventView():
    if session.auth != None:
        q1 = db.userTag.tag == db.eventTag.tag
        q2 = db.userTag.auth_user == session.auth.user.id
        q3 = db.events.id == db.eventTag.events
        events = db((q1 & q2 & q3)).select(db.events.eventName, db.events.id, db.events.startAt,
                                       db.events.endAt, db.events.typeOfEvent,
                                       distinct=True)
    else:
        q1 = db.eventTag.tag == db.tag.id
        q2 = db.tag.tagName == "Public"
        q3 = db.events.id == db.eventTag.events
        events = db((q1 & q2 & q3)).select(db.events.eventName, db.events.id, db.events.startAt,
                                       db.events.endAt, db.events.typeOfEvent,
                                       distinct=True)

    json_response = []
    for event in events:
        temp = {}
        temp["id"] = event["id"]
        temp["eventName"] = event["eventName"]
        temp["events"] = {}
        temp["events"]["startAt"] = event["startAt"]

        ## default endtime to start time if there is none
        if event["endAt"]:
            temp["events"]["endAt"] = event["endAt"]
        else:
            temp["events"]["endAt"] = event.startAt
            event["endAt"] = event.startAt

        temp["typeOfEvent"] = event["typeOfEvent"]
        temp["title"] = event["eventName"]
        if event.typeOfEvent == 'Academic':
            temp["class"] = "event-info"
        if event.typeOfEvent == 'Cultural':
            temp["class"] = "event-success"
        if event.typeOfEvent == 'Sports':
            temp["class"] = "event-special"
        if event.typeOfEvent == 'Holiday':
            temp["class"] = "event-warning"
        if event.typeOfEvent == 'Other':
            temp["class"] = "event-inverse"
        if event.typeOfEvent == 'Urgent':
            temp["class"] = "event-important"
        temp["url"] = URL('showDes.html', args=[event.id])
        temp["start"] = (event["startAt"] - datetime.datetime(1970, 1, 1)).total_seconds() * 1000 - 19800 * 1000
        temp["end"] = (event.endAt - datetime.datetime(1970, 1, 1)).total_seconds() * 1000 - 19800 * 1000
        json_response.append(temp)

    return dict(success=1, result=json_response)


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
