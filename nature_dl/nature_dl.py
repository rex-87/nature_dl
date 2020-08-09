# -*- coding: utf-8 -*-
"""
	Nature Download
	
	This project is an example of a Python project generated from cookiecutter-python.
"""

## -------- COMMAND LINE ARGUMENTS ---------------------------
## https://docs.python.org/3.7/howto/argparse.html
import argparse
CmdLineArgParser = argparse.ArgumentParser()
CmdLineArgParser.add_argument(
	"-v",
	"--verbose",
	help = "display debug messages in console",
	action = "store_true",
)
CmdLineArgs = CmdLineArgParser.parse_args()

## -------- LOGGING INITIALISATION ---------------------------
import misc
misc.MyLoggersObj.SetConsoleVerbosity(ConsoleVerbosity = {True : "DEBUG", False : "INFO"}[CmdLineArgs.verbose])
LOG, handle_retval_and_log = misc.CreateLogger(__name__)

try:
	
	## -------------------------------------------------------
	## THE MAIN PROGRAM STARTS HERE
	## -------------------------------------------------------	

	import requests
	from bs4 import BeautifulSoup
	import os
	from PyPDF2 import PdfFileMerger
	import subprocess
	
	weekly_url = r'https://www.nature.com/nature/current-issue'
	page = requests.get(weekly_url)
	soup = BeautifulSoup(page.text, 'html.parser')

	issue_title = '{}'.format(soup.title.text)
	pdf_folder = os.path.join('pdf', issue_title)
	articles_folder = os.path.join(pdf_folder, 'articles')
	if not os.path.exists('pdf'):
		os.mkdir('pdf')
	if not os.path.exists(pdf_folder):
		os.mkdir(pdf_folder)
	if not os.path.exists(articles_folder):
		os.mkdir(articles_folder)
	
	pdf_merger = PdfFileMerger()

	# import IPython; IPython.embed(colors='Neutral')

	# url_l = []
	pdf_stream_l = []
	for link in soup.find_all('a'):
		href = link.get('href')
		if '/articles/' in href:

			# url_l.append('https://www.nature.com'+link.get('href'))
			id_ = href.replace('/articles/', '')
			pdf_url = 'https://media.nature.com/original/magazine-assets/{id_}/{id_}.pdf'.format(id_ = id_)
			# url_l.append(pdf_url)
			print("Request:", pdf_url)
			pdf_req = requests.get(pdf_url)

			# NOT FOUND will return some html, not pdf data: skip
			if b'%PDF-' == pdf_req.content[0:5]:
				
				link_url = 'https://www.nature.com'+link.get('href')
				link_page = requests.get(link_url)
				link_soup = BeautifulSoup(link_page.text, 'html.parser')
				
				def my_replace(tin):
					return tin.replace(':', '_').replace('?', '_').replace('.', '_')
				if ": Research Highlights" in link_soup.title.text:
					title = my_replace(link_soup.title.text.replace(" : Research Highlights", ""))
					category = "RESEARCH HIGHLIGHTS"
				else:
					title = my_replace(link_soup.title.text)

					category_div = link_soup.find('div', class_ = 'article__type')
					if category_div is None:
						category_div = link_soup.find('p', class_ = 'article-item__subject')

					category = my_replace(category_div.text.split('\n')[0])

				# pdf_name = '{}.pdf'.format(id_)
				pdf_name = os.path.join(articles_folder, '{} - {}.pdf'.format(category, title))
				print("Export to PDF:", pdf_name)
				with open(pdf_name, 'wb') as fout:
					fout.write(pdf_req.content)

				# with open(pdf_name, 'rb') as fin:
				pdf_stream_l.append(open(pdf_name, 'rb'))
				pdf_merger.append(pdf_stream_l[-1])

	issue_path = os.path.join(pdf_folder, "Nature, "+issue_title+".pdf")
	with open(issue_path, 'wb') as fout:
		pdf_merger.write(fout)

	for pdf_stream in pdf_stream_l:
		pdf_stream.close()


## -------- SOMETHING WENT WRONG -----------------------------	
except:

	import traceback
	LOG.error("Something went wrong! Exception details:\n{}".format(traceback.format_exc()))

## -------- GIVE THE USER A CHANCE TO READ MESSAGES-----------
finally:
	
	# input("Press any key to exit ...")
	pass
