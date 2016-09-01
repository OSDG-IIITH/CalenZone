from gluon.tools import Mail
import datetime

mail = Mail()

mail.settings.server = ':'
mail.settings.sender = ''
mail.settings.login  = ':'

mailing_list = {
    "All" : ""
    "Students" : "students@lists.iiit.ac.in"
    "Research" : "research@lists.iiit.ac.in"
    "Faculty" : "faculty@lists.iiit.ac.in"
}

reminder_Template = "<INSERT MAIL TEMPLATE HERE>"

def send_mail(event, address):
    #x = mail.send(to=[mailing_list[address]], subject=("Reminder for %s" %(event.eventName)), message=reminder_template)
    pass

def generate_reminder():
    '''mail.send(self, to, subject='None', message='None', attachments=[],
    cc=[], bcc=[], reply_to=[], sender=None, encoding='utf-8',
     raw=True, headers={})'''
    curr_time = datetime.datetime.now()
    coming_time = curr_time + datetime.timedelta(minutes=5000)
    events = db((db.events.startAt < coming_time) & (db.events.startAt>curr_time)).select(orderby=db.events.startAt)
    for event in events:
        event_tags = [i.tag.tagName for i in db(db.eventTag.events == event).select()]

# from gluon.scheduler import Scheduler
# scheduler = Scheduler(db)

# scheduler.queue_task(generate_mail, period=300, repeats=0)
