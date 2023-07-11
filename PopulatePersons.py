# This file reads data from linkedin urls tables and fills the persons table

# imports
from sqlite3 import IntegrityError
from Models import db, LinkedInURLs, Persons
import sys
from CustomScraper import EmailFinder, LinkedIn
from dotenv import load_dotenv
load_dotenv()
import os


# set limit to scrape in one run
Slimit = 80

# create email finder object
access_key = os.environ['SKRAPP_ACCESS_KEY']
findEmail = EmailFinder(access_key)
# create linkedin scraper object
linkedin = LinkedIn()

# step 1: Get n rows where url has not been scraped
urls = LinkedInURLs.query.filter(LinkedInURLs.scraped==False).limit(Slimit).all()
error_links = []
# now loop over each row entry
for row in urls:
    id = row.id
    url = row.linkedinURL

    # try to get scraped data from linkedin
    try:
        data = linkedin.scrape_url_data(url)
        # {'firstname':firstname, 'lastname':lastname, 'job':job_title, 'url':url, 'company':company}
    except:
            print('--------------- LINKEDIN FINDER ERROR AT url '+str(url)+' ------- id: '+str(id)+' Reason: '+str(sys.exc_info()[0]))
            print('I will log this entry and continue...')
            error_links.append(url)
            try:
                db.session.delete(row)
                db.session.commit()
            except:
                db.session.rollback()
                print('Error deleting - please update manually for last link. thanks.')
                exit()
            continue

    # if data is found proceed
    # step 2: find email
    try:
        email = findEmail.find_email(data['firstname'],data['lastname'],data['company'])
        # {'email':response['email'], 'accuracy':response['accuracy']}
    except:
        print('--------------- ERROR IN RUNNING FINDEMAIL - CHECK')
        if findEmail.get_remaining_balance() == 0:
            print('BALANCE REMAINING: '+str(findEmail.get_remaining_balance()))
            linkedin.close_driver()
            exit()
    # see if email is ok
    try: 
        email = email['email']
    except:
        print('-------- ERROR IN RESPONSE OF FINDING EMAIL - I will log this entry and continue...')
        error_links.append(url)
        print('BALANCE REMAINING: '+str(findEmail.get_remaining_balance()))
        if findEmail.get_remaining_balance() == 0:
            linkedin.close_driver()
            exit()
        try:
            db.session.delete(row)
            db.session.commit()
        except:
            db.session.rollback()
            print('Error deleting - please update manually for last link. thanks.')
            exit()
        continue
    # if email is ok write this data to the database
    try:
        db.session.add(Persons(linkedinURL=data['url'],firstname=data['firstname'],lastname=data['lastname'], email=email, company=data['company'],
        job=data['job'],contacted=False))
        db.session.commit()
        print('added to the database New person of email '+email+' working at '+data['company'])
        # update this value in linkedin urls table to scraped
        try:
            LinkedInURLs.query.filter_by(id=id).update(dict(scraped=True))
            db.session.commit()
        except:
            db.session.rollback()
            print('Error updating scraped value to true - please update manually for last scraped email. thanks.')
            exit()
    except IntegrityError:
        print('--------------- ERROR AT EMAIL '+str(email)+' Reason: Integrity Error')
        db.session.rollback()
    except:
        print('--------------- ERROR AT EMAIL '+str(email)+' Reason: '+str(sys.exc_info()[0]))
        db.session.rollback()

print('Error links:')
for link in error_links:
    print(link)
print()
print('Script Finished, remaining API call balance is '+str(findEmail.get_remaining_balance())+' credits')
linkedin.close_driver()




