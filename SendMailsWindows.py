# imports
from time import sleep
import win32com.client as win32
from sqlite3 import IntegrityError
from Models import db, LinkedInURLs, Persons
import sys
outlook = win32.Dispatch('outlook.application')

# set limit to send in one run
Slimit = 100


# step 1: Get n rows where url has not been contacted
rows = Persons.query.filter(Persons.contacted==False).limit(Slimit).all()



for row in rows:
    # set variables
    id = row.id
    currentname = row.firstname
    currentCompany = row.company
    currentEmail = row.email
    job = row.job.lower()
    # if their job title indicates they are recruiter - modify based on that
    if 'talent' in job or 'recruiter' in job or 'program manager' in job:
        mytext = 'Canada relating to DevOps or Software Engineering'
    else:
        mytext = 'your team'
    htmlEmail = '\
    Hello '+currentname+',<br>\
    I hope you had an awesome New Year and a great day so far!<br>\
    <br>\
    I wanted to inquire about any open full-time new grad positions in '+mytext+' at '+currentCompany+' starting in May. I saw your profile on LinkedIn and wanted to reach out to you. Here\'s what I bring to the table to add value to the organization.<br>\
    <br>\
    <b>Experience:</b> My program, focuses mostly on chemical systems and material science. However, I have developed in-depth knowledge of programming concepts and data structures by teaching myself and by working in the relevant industries during my co-ops because I have a passion for coding.<br>\
    <b>Leadership:</b> I have attended and won many hackathons where I have experienced teamwork and team building activities while working on a common goal and solving challenging problems which have helped me gain diverse experience over widespread fields.<br>\
    <b>Lifelong Learning:</b> I strive to continuously learn new technologies and develop skills to deliver higher performance at workplace.<br>\
    <br>\
    Thank you once again for your help. I have also attached my résumé for your reference. Have a great rest of the day and week 😊<br>\
    <br>\
    Best<br>\
    <span style="mso-fareast-language:EN-CA"><img border=0 width=221 height=63 style="width:2.302in;height:.6562in" id="_x0000_i1029" src="cid:MyId1" alt="signature"><o:p></o:p></span><br>\
        '
    # Create mail object
    mail = outlook.CreateItem(0)
    mail.To = currentEmail
    mail.Subject = 'Hi '+currentname+', I found you through LinkedIn and wanted to reach out!'
    mail.HTMLBody = htmlEmail

    # To attach 2 files
    attachment  = "C:\\Users\\name\\Desktop\\things\\Resume.pdf"
    mail.Attachments.Add(attachment)
    # For image attatchment
    attachment = mail.Attachments.Add("C:\\Users\\ragha\\Desktop\\things\\signature_image.png")
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyId1")

    #  Send the email
    mail.Send()
    # Sleep for 1 sec
    sleep(1)
    # print if sent
    print('Email sent to '+currentname+' at email '+currentEmail+' who works at '+currentCompany)
    # update this row in the table
    try:
        Persons.query.filter_by(id=id).update(dict(contacted=True))
        db.session.commit()
    except:
        db.session.rollback()
        print('Error updating contacted value to true - please update manually for last sent email. thanks.')
        exit()

