# coding=utf-8
# TODO
# - reformat GoodReads export without needing manual adjustment
# - make a list of books under $5?
import requests
import csv
import os
import time
from datetime import datetime
from lxml import html
from colorama import Fore, Back, Style

def printwreset(text):
    print(text, Style.RESET_ALL)

newfolder="bookinfo"+str(datetime.now())
os.mkdir(os.path.join("./", newfolder))
os.mkdir(os.path.join("./"+newfolder+"/", "reports"))
os.mkdir(os.path.join("./"+newfolder+"/", "books"))

breaktime=3
difficulty=0
with open('data.csv') as booksdata:
    reader = csv.reader(booksdata, quoting=csv.QUOTE_MINIMAL)
    next(reader) # skip first line
    with open(os.path.join("./"+newfolder+"/reports/", 'Not Found.csv'), mode='w') as notfound_csv, \
            open(os.path.join("./" + newfolder + "/reports/", 'Main List.csv'), mode='w') as summary, \
            open(os.path.join("./" + newfolder + "/reports", 'Mainlog.log'), mode='w') as log:
        csv_writer_summary = csv.writer(summary, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer_notfound = csv.writer(notfound_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            printwreset(Fore.BLUE + str(datetime.now()))
            print(datetime.now(), file=log)
            if breaktime<1.5:
                breaktime=1.5 # minimum breaktime is 1.5 seconds
            GRBookInfo=row[2]+", "+row[1]
            GRBookAuthor=row[2]
            printwreset(Fore.BLACK+Back.WHITE + GRBookInfo)
            print("Book by "+GRBookAuthor, file=log)
            ISBN=row[3]
            URL="https://www.abebooks.com/servlet/SearchResults?cm_sp=sort-_-SRP-_-Results&sortby=17&isbn="+ISBN
            r = requests.get(URL)
            tree = html.fromstring(r.content)
            proceed = False
            # checks if the webpage has errors in two known places
            danger = tree.xpath('//*[@id="main"]/div/div[1]/div/div/text()')
            danger2 = tree.xpath('//*[@id="main"]/div/div[1]/div/h2/text()')
            if danger==['\n            ', '\n            The ISBN is not valid.\n          ']:
                print("Changing to alternate ISBN")
                print("Changing to alternate ISBN", file=log)
                ISBN = row[4]
                URL = "https://www.abebooks.com/servlet/SearchResults?cm_sp=sort-_-SRP-_-Results&sortby=17&isbn=" + ISBN
                r = requests.get(URL)
                print(r.status_code)
                tree = html.fromstring(r.content)
                danger = tree.xpath('//*[@id="main"]/div/div[1]/div/div/text()')
                danger2 = tree.xpath('//*[@id="main"]/div/div[1]/div/h2/text()')
            if r.status_code==429:
                status=429
                print("Status Code: ", r.status_code)
                print("Status Code: ",r.status_code, file=log)
                while status==429:
                    # print(r.headers)
                    # print(r.headers, file=log)
                    # print(r.content)
                    # print(r.content, file=log)
                    breaktime = breaktime * 1.5  # increase wait by factor of 1.5
                    print("BREAK FOR "+str(breaktime)+" SECONDS")
                    print("BREAK FOR " + str(breaktime) + " SECONDS", file=log)
                    time.sleep(breaktime)
                    r = requests.get(URL)
                    print("Status Code: ", r.status_code)
                    print("Status Code: ", r.status_code, file=log)
                    if r.status_code!=429:
                        status=r.status_code
                        print("Status Code: ",r.status_code, file=log)
                    tree = html.fromstring(r.content)
            breaktime = breaktime * 0.75
            if danger==[] and danger2==[] and r.status_code!=429:
                proceed=True
            else:
                print(danger)
                print(danger2)
            printwreset(Fore.CYAN+"Proceed: "+str(proceed))
            print("Proceed: ", proceed, file = log)
            if proceed:
                    with open(os.path.join("./"+newfolder+"/books/", GRBookAuthor+' '+ISBN+'.csv'), mode='w') as book_info:
                        csv_writer = csv.writer(book_info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        results=tree.xpath('//*[@class="cf result"]')
                        bookid_ = 1
                        for result in results:
                            bookid=str(bookid_)
                            title = tree.xpath('//*[@id="book-'+bookid+'"]/div[2]/div[1]/h2/a/span/text()')
                            url = tree.xpath('//*[@id="book-'+bookid+'"]/div[2]/div[1]/h2/a/@href')
                            price = tree.xpath('//*[@id="srp-item-price-'+bookid+'"]/text()')
                            shipping = tree.xpath('//*[@id="srp-item-shipping-price-'+bookid+'"]/text()')
                            # print(title[0])
                            # print("https://abebooks.com/"+url[0])
                            # print(price[0], " + ", shipping[0])
                            if title!=[] and shipping!=[] and title!=[] and url!=[]: # check if all values were found on the page
                                csv_writer.writerow([price[0],shipping[0], title[0], "https://abebooks.com/"+url[0], ISBN])
                            else:
                                printwreset(Fore.RED+"One of the values to write was empty")
                                print("One of the values to write was empty", file=log)
                            if bookid_==1:
                                    csv_writer_summary.writerow([price[0], shipping[0], title[0], row[2], row[6], "https://abebooks.com/" + url[0], ISBN])
                            bookid_+=1
            else:
                    csv_writer_notfound.writerow([GRBookInfo, ISBN, r.status_code, URL])
            if breaktime>30 and breaktime<120:
                breaktime=breaktime*0.75
                printwreset(Fore.BLUE+"BREAK AT END OF ROW FOR " + str(breaktime) + " SECONDS")
                print("BREAK AT END OF ROW FOR " + str(breaktime) + " SECONDS", file=log)
                time.sleep(breaktime)
            print("\n")
print("\n")