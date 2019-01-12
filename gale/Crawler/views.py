from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template import loader

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

from urllib.parse import urlsplit

class Crawl(object):
    main_URL = ""          # base URL given by the user
    pageList = []          # list which will contain all the links in the end
    toCrawl = []           # list of pages which are to be crawled
    crawled = []           # list of pages which are already crawled
    # A list of common file type which should not be crawled (as per the current needs of this research)
    # also an attempt to avoid any sort of form
    isAFileLink = ['.pdf',      # .pdf files
                   '.doc',      # documents files
                   '.docx',     # modern document files
                   '.jpg',      # image files
                   '.jpge',     # image files
                   '#',         # multiple page like structuring on same page or sometimes for form/javascript purpose
                   '.txt',      # for text files (unusual but still) / robots.txt
                   '.py',       # for any py file connected to form
                   '.c',        # for any .c server side files
                   '.cpp',      # for any .cpp server side files
                   '.zip',      # for any zip (usually a download)
                   '?',         # used in get method of HTML while passing values to another page from a form
                   'js',        # for javascript files
                   'css',       # for style script file
                   'asp',       # for server side asp files
                   'aspx',      # for server side aspx files
                   'javascript:',     # for javascript popups
                   '=',         # for any form values or query passing
                   'mailto'     # for avoiding Mail links
     ]

    def __init__(self,WebUrl):
        self.main_URL = WebUrl

    # Check if a link is actully a file or a web page.
    def fileLinksCheck(self,URL):
        if any(x in URL for x in self.isAFileLink):
            return True
        else:
            return False

    # function to check if the link exists or not
    def check_Link(self,URL):
        conn = requests.get(URL)
        if conn.status_code == 200 :
            conn.close()
            return True

    # This function finds all the links and passes it to a dictionary with title of page and URL.
    def fetch_Links(self,URL):
        # If the link is already fetched then don't repeat this process
        try:
            conn = requests.get(URL)
            if URL in self.crawled and conn.status_code != 200 :
                conn.close()
                self.toCrawl.remove(URL)
                self.logs.append(URL+"Not a URL")
                return
            conn.close()
        except requests.exceptions.MissingSchema:
            self.toCrawl.remove(URL)
            self.logs.append(URL + "Not a URL")
            conn.close()
            return

        # looking out for run time errors due to consistent requests being made
        try:
            sourceCode = requests.get(URL)
        except TimeoutError:
            self.logs.append("Connection Time Out "+URL)
            return
        except requests.exceptions.ConnectionError:
            self.logs.append("Connection Error "+URL)
            return
        except ConnectionResetError:
            self.logs.append("Connection reset")
            return

        pageLinks = []

        packets = sourceCode.text
        soup = BeautifulSoup(packets,"html.parser")
        run = 0

        # A check to see the number of links in page are not zero.
        # If they are 0 then remove link from the toCrawl list and exit
        if len(soup.find_all('a',href=True)) == 0:
            if URL in self.toCrawl:
                self.toCrawl.remove(URL)
            if URL not in self.crawled:
                self.crawled.append(URL)
            self.logs.append(URL + " Crawled, Single Link Page")
            return

        # find all the links (anchor tag with href attribute) in the page
        for a in soup.find_all('a',href=True):
            links = str(a['href'])
            if run == 0:
                print("Found links on page : "+URL)
            run += 1

            # checking every link with the file list we have
            if self.fileLinksCheck(links):
                continue

            # check for relative URL and convert them to Absolute URL
            if not links.startswith('http'):
                links = urljoin(URL,links)
                # print(links)

            # check if the link belongs to the same domain
            if links.startswith(self.main_URL):
                pageLinks.append(links)

                # Check all the links in the page are already crawled or not
                if links in self.crawled:
                    continue
                else:
                    if not links in self.toCrawl:
                        self.toCrawl.append(links)


        """
        get title of the page &
        if title is not there then use URL as page title to avoid empty values from getting passed
        """

        # Put the current link in crawled list as it has been processed.
        if URL not in self.crawled:
            self.crawled.append(URL)

        # remove the page URL from toCrawl.
        if URL in self.toCrawl:
            self.toCrawl.remove(URL)

        # for getting logs in terminal
        print("Total links found",len(self.pageList))
        print("Links Remaining",len(self.toCrawl))
        print("Current Page ",URL)

        # Always close all sorts of connections
        sourceCode.close()

    #TODO : Look out for more RUNTIME errors - Run on more than one website
    #TODO : Store the data in mysql database

    # Create your views here.
    @csrf_exempt
    def galeCall(self,WebUrl):
        url = WebUrl
        t = loader.get_template('templates/index.html')
        if self.fileLinksCheck is True:
            if self.check_Link(url):
                self.fetch_Links(url)
            else:
                return HttpResponse(t.render("link dosen't exists", url), content_type='application/xhtml+xml')
        else:
            return HttpResponse(t.render("not a link", url), content_type='application/xhtml+xml')
        render(WebUrl,"index.html")

