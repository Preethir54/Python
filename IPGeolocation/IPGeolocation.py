#Importing all required libraries
import dns.resolver
import requests
import pygeoip
import time
import pythonwhois
import sqlite3
import socket
import xlsxwriter
import simplekml


#Function to get the whois information of the url
def whois_inf(url, domain):
	try:
		w = pythonwhois.get_whois(domain)
		time.sleep(20)
		whois_info[url] = str(w)
	except Exception, e:
		whois_info[url] = {}		
		pass


#Function to get the ip_address information of the url
def dnsrec(url, domain):
	dnsrecs[url] = list()
	try:
		mydns = dns.resolver.Resolver()
		ans = mydns.query(domain,"A")
		for ip in ans:
			dnsrecs[url].append(str(ip)) 
	except Exception, e:
		dnsrecs[url] = []
		pass


#Function to get the server information of the url
def server_fingerprint(url):
	serverinfo[url] = list()	
	try:	
		response = requests.get(url) 
		for header in headers:
			try:	
				results = response.headers[header]
				serverinfo[url].append(header+" : "+str(results))
			except Exception, e:
				serverinfo[url].append(header+" : Not present")
	except Exception, e:
		serverinfo[url] = []
		pass


#Function to get the geolocation information of the url
def Geolocation(url, domain):
	templist = []	
	try:
		ip = socket.gethostbyname(domain)
		record = loc.record_by_name(ip)	
		templist.append(url)
		templist.append(record.get('longitude'))
		templist.append(record.get('latitude'))
		kmllist.append(templist)
		geoloc[url] = (str(record))
		templist = []
	except Exception, e:
		geoloc[url] = {}		
		pass		


#Function to append all information to the file_info table in the database
def sqldb(url):
	templist = []
	templist.append(str(url))
	templist.append(str(whois_info.get(url)))
	templist.append(str(dnsrecs.get(url)))
	templist.append(str(serverinfo.get(url)))
	templist.append(str(geoloc.get(url)))
	c.execute('INSERT INTO file_info VALUES(?,?,?,?,?)',templist)

	
#Generate Report in the form of excel sheet that contains all the information contained in the database
def Report():
	global c
	i = 1
	book = xlsxwriter.Workbook("Report.xlsx")
	sheet1 = book.add_worksheet()
	sheet1.write(0,0,"URL")
	sheet1.write(0,1,"WHOIS_INFO")
	sheet1.write(0,2,"IP_ADDRESS")
	sheet1.write(0,3,"SERVER_INFO")
	sheet1.write(0,4,"GEOLOCATION")
	dat = c.execute("SELECT * FROM file_info").fetchall()
	for row in dat:
		for j in range(0,5):
			sheet1.write(i,j,row[j])
		i = i+1
	book.close()


#Function to generate the kml file 
def kmlreport():
	for item in kmllist: 
		kml_file.newpoint(name=item[0],coords=[(item[1], item[2])])
	


#Assigning dictionaries to store all the information
dnsrecs = {}
serverinfo = {}
geoloc = {}
whois_info = {}


#Assigning a list to store the data required to generate the kml file
kmllist = []


#Make all required variables global for use in functions
global headers, loc,c, kml_file


#Open the url file
files = open("url.txt","r")


#Assigning all required information for processing
headers = ['Server','Date','Via','X-Powered-By','X-Country-Code']
loc = pygeoip.GeoIP('/home/osboxes/Downloads/GeoLiteCity.dat')


#Creating the kml file
kml_file = simplekml.Kml(name="Geolocation")


#Creating the database
conn = sqlite3.connect("url_info.db")
conn.text_factory = str
c = conn.cursor()
c.execute('''CREATE TABLE file_info(URL text, WHOIS_INFO text, IP_ADDRESS text, SERVER_INFO text, GEOLOCATION text)''')


#Processing the url information
for line in files:
	url = line.rstrip()
	domain = url.split('//')[1].split('/')[0]
	whois_inf(url, domain)	
	dnsrec(url,domain)
	server_fingerprint(url)
	Geolocation(url, domain)
	sqldb(url)


#Generating the required files
Report()
kmlreport()
kml_file.save("Geolocation.kml")


