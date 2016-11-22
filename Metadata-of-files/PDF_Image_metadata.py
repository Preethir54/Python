import subprocess
import hashlib
import sqlite3
import os
import shutil
import magic
from pyPdf import PdfFileReader
from PIL import Image
from PIL.ExifTags import TAGS
import xlsxwriter
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')



#Recover all files from disk 
def recover(disk_directory):
	output = disk_directory+"/output"
	for f in os.listdir(disk_directory):
		filename = disk_directory+"/"+f

		#uses tsk_recover to extract files
		subprocess.check_output(["tsk_recover","-e",filename,output])




#extracting pdf and image files from the recovered files
def extract(disk_directory, save_directory):
	global ms

	#creates the output directory extract
	os.mkdir(save_directory)

	i = 1
	execute = 0
	for path,dirname,filename in os.walk(disk_directory):
		for files in filename:

			#checks if the file is pdf or image using the magic number of files
			a = ms.file(os.path.join(path,files))

			if a.startswith("PDF"):
				filetype = "PDF"
				os.rename(os.path.join(path,files), save_directory+str(i)+"-"+files)
				pdf_metadata(files,filetype,save_directory+str(i)+"-"+files)
				i = i+1

			elif a.startswith("JPEG") or a.startswith("TIFF") or a.startswith("GIF") or a.startswith("PNG") or a.startswith("PC"):
				filetype = "IMAGE"
				os.rename(os.path.join(path,files), save_directory+str(i)+"-"+files)
				image_metadata(files, filetype, save_directory+str(i)+"-"+files)			
				i = i+1

	


#Metadata of pdf files
def pdf_metadata(fname, filetype, pdf_file):
	global c
	data = "Metadata ="
	pdflist = list()
	try:
		pdflist.append(fname)
		pdflist.append(filetype)
		pdflist.append(hashlib.md5(pdf_file).hexdigest())
		pdf = PdfFileReader(file(pdf_file,'rb'))
		details = pdf.documentInfo
		for k,v in details.items():
			data = data+k+":"+v+";"	
		pdflist.append(data)
		c.execute('INSERT INTO file_info VALUES(?,?,?,?)',pdflist)
	except Exception, e:
		pass
	
	


#Metadata of image files
def image_metadata(fname, filetype, image_file):
	global exif, conn
	imagelist = list()
	data = "Metadata ="
	imagelist.append(fname)
	imagelist.append(filetype)
	try:
		imagelist.append(hashlib.md5(image_file).hexdigest())
		img = Image.open(image_file)
		info = img._getexif()
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			exif[decoded] = value
		temp = dict()
		temp = exif
		for k,v in temp.items():
			data = data+str(k)+":"+str(v)+";"	
		imagelist.append(data)
	except Exception, e:
		imagelist.append("")
	c.execute('INSERT INTO file_info VALUES(?,?,?,?)',imagelist)




#Generate Report in the form of excel sheet
def Report(disk_directory):
	global c
	i = 1
	book = xlsxwriter.Workbook(disk_directory+"/report.xlsx")
	sheet1 = book.add_worksheet()
	sheet1.write(0,0,"FILENAME")
	sheet1.write(0,1,"FILETYPE")
	sheet1.write(0,2,"MD5HASH")
	sheet1.write(0,3,"METADATA")
	dat = c.execute("SELECT * FROM file_info").fetchall()
	for row in dat:
		for j in range(0,4):
			sheet1.write(i,j,row[j])
		i = i+1
	book.close()
		


#Initializing needed variables		
exif = dict()
rowlist = list()
ms = magic.open(magic.MAGIC_NONE)
ms.load()

#Getting the directory as input ans setting the directory to store the pdf and image files
disk_directory = raw_input("Enter the full path of the disk image directory: ")
save_directory = disk_directory+"/extract/"


#Calling recover to extract files from disk
recover(disk_directory)

#Creating the database
conn = sqlite3.connect(disk_directory+"/file_metadata.db")
conn.text_factory = str
c = conn.cursor()
c.execute('''CREATE TABLE File_info(FILENAME text, FILETYPE text, MD5HASH text, Metadata text)''')

#Calling functions to find metadata of required files and generating the report
extract(disk_directory, save_directory)
Report(disk_directory)

#Closing the database and removing "output" directory
shutil.rmtree(disk_directory+"/output")
conn.commit()
conn.close()

