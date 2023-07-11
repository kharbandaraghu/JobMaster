from CustomScraper import URLScrapper, EmailFinder
import sys
# 'scotiabank','BMO','Accenture','KMPG','EY','CIBC', 'Open Text','Capital One', 'Netflix', 'Manulife', 'Twitch'
companies = []
pages = 1

def run():
    # create scraper object
    a = URLScrapper()
    for company in companies:
        try:
            a.get_urls_for_company(company,pages)
        except:
            print('--------------- ERROR GETTING URL FOR '+str(company)+' Reason: '+str(sys.exc_info()[0]))
            exit()
        a.print_urls()
        print('adding these to database')
        a.add_urls_to_database()
        print(company+' fully added to database')
        # empty url list after adding to database
        a.empty_url_list()

    a.close_driver()

# run()