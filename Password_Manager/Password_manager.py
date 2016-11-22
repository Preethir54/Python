#import crypto functions
from Crypto import Random
from Crypto.Cipher import AES
import os
import ConfigParser
import hashlib
import sys

#Extract info from config file
config = ConfigParser.ConfigParser()
config.read("appconfig.cfg")
mkey = config.get('keys','mkey')
msecret = config.get('keys','secret')
IV1 = config.get('init_vector','IV')
IV2 = config.get('init_vector','IV2')

#Extracts encrypted key
enckey = config.get('keys', 'key')

#Get key from master secret to decrypt key
dkey = msecret[:32]

#decrypt key
decryptor = AES.new(dkey, AES.MODE_CBC, IV=IV2)
key = decryptor.decrypt(enckey)

#Constants
option = 1
seperate = list()
bs = 32


#file encryption
def encrypt(in_file, out_file,flag):
	
	if flag == 'e':
		cipher = AES.new(key, AES.MODE_ECB, IV1)
	elif flag == 'r':
		cipher = AES.new(key, AES.MODE_CTR, counter=lambda: IV2)
	elif flag == 'c':
		cipher = AES.new(key, AES.MODE_CBC, IV2)

	finished = False
	while not finished:
		chunk = in_file.read(1024 * bs)
		if len(chunk) == 0 or len(chunk) % bs != 0:
			padding_length = (bs - len(chunk) % bs) or bs
			chunk += padding_length * chr(padding_length)
			finished = True
		out_file.write(cipher.encrypt(chunk))

#file decryption
def decrypt(in_file, out_file, flag):
	if flag == 'e':
		cipher = AES.new(key, AES.MODE_ECB, IV1)
	elif flag == 'r':
		cipher = AES.new(key, AES.MODE_CTR, counter=lambda: IV2)
	elif flag == 'c':
		cipher = AES.new(key, AES.MODE_CBC, IV2)
	next_chunk = ''
	finished = False
	while not finished:
		chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
		if len(next_chunk) == 0:
			padding_length = ord(chunk[-1])
			chunk = chunk[:-padding_length]
			finished = True
		out_file.write(chunk)

#Check username
def checkuser(uname, pword, data):
	i = 0	
	for i in range(0,len(uname)):
		if uname[i] == '#' or uname[i] == '$' or uname[i] == ':':
			return True	

	for i in range(0,len(pword)):
		if pword[i] == '#' or pword[i] == '$' or pword[i] == ':':
			return True 	

	for i in range(0,len(data)):
		if data[i] == '#' or data[i] == '$' or data[i] == ':':
			return True	
	return False

#Check password requirements
def checkpass(pword):

	if len(pword) < 8:
		print "Password must be atleast 8 characters long"
		return True

	capital = 0
	letter = 0
	number = 0
	for i in range(0,len(pword)):
		if ord(pword[i]) >= 65 and ord(pword[i]) <= 90:
			capital = 1
			continue

		if ord(pword[i]) >= 97 and ord(pword[i]) <= 122:
			letter = 1
			continue
	
		if pword[i] >= '0' and pword[i] <= '9':
			number = 1
			continue

	if capital == 1 and number == 1 and letter == 1:
		return False
	print "Password must contain one capital letter, one small letter and one number"	
	return True
	
#register function
def register():
	c = True
	
	print "\n#, $ and : special characters are not allowed"
	print "\nPassword must contain atleast 8 characters and one capital letter, one small letter and one number"	
	
	while c:
		uname = raw_input("\nEnter username: ")

		#Checking if username already exists
		c = retrieve(uname)
		if c == True:
			continue

		pword = raw_input("\nEnter password: ")

		#Checking password requirements
		c = checkpass(pword)
		if c == True:
			continue
		secretdata = raw_input("\nEnter secret phrase incase of password retrieval: ")

		#checks if uname, pword or secretdata contains #, $ or :
		c = checkuser(uname, pword, secretdata)
		if c == True:
			print "\n One of the inputs contain #, $ or :"
			continue
	c = True
	while c:
		encryptflag = raw_input("\nPlease enter the mode of encryption \n1. e:ECB \n2. r:CTR \n3. c:CBC \nEnter choice: ")	
		if encryptflag == 'e' or encryptflag == 'c' or encryptflag == 'r':
			c = False
		else:
			print "\n Enter a valid option"

	info = uname+":"+pword+":"+secretdata

	#Write register information to the appropriate file
	if encryptflag == 'e':

		#check if file exists
		if os.path.isfile("eepassfile.txt"):
			pass
		else:
			passfile = open("eepassfile.txt",'w')
			passfile.close()

		if os.stat("eepassfile.txt").st_size == 0:
			pass
		else:
			#decrypt file
			passfile = open("ePassfile.txt",'w')
			decryptfile = open("eepassfile.txt",'r')
			decrypt(decryptfile,passfile,encryptflag)
			decryptfile.close()
			passfile.close()
			
		#Append to file and encrypt
		passfile = open("ePassfile.txt",'a')
		passfile.write(info+":"+"\n")
		passfile.close()
		encryptfile = open("eepassfile.txt",'w')
		passfile = open("ePassfile.txt",'r')
		encrypt(passfile,encryptfile,encryptflag)
		passfile.close()
		encryptfile.close()
		
		#Remove file
		os.remove("ePassfile.txt")
		
	elif encryptflag == 'r':

		#check if file exists
		if os.path.isfile("erpassfile.txt"):
			pass
		else:
			passfile = open("erpassfile.txt",'w')
			passfile.close()

		if os.stat("erpassfile.txt").st_size == 0:
			pass
		else:
			#decrypt file
			passfile = open("rPassfile.txt",'w')
			decryptfile = open("erpassfile.txt",'r')
			decrypt(decryptfile,passfile,encryptflag)
			decryptfile.close()
			passfile.close()

		#Append to file and encrypt
		passfile = open("rPassfile.txt",'a')
		passfile.write(info+":"+"\n")
		passfile.close()
		encryptfile = open("erpassfile.txt",'w')
		passfile = open("rPassfile.txt",'r')
		encrypt(passfile,encryptfile,encryptflag)
		passfile.close()
		encryptfile.close()
	
	elif encryptflag == 'c':

		#check if file exists
		if os.path.isfile("ecpassfile.txt"):
			pass
		else:
			passfile = open("ecpassfile.txt",'w')
			passfile.close()

		if os.stat("ecpassfile.txt").st_size == 0:
			pass
		else:
			#decrypt file
			passfile = open("cPassfile.txt",'w')
			decryptfile = open("ecpassfile.txt",'r')
			decrypt(decryptfile,passfile,encryptflag)
			decryptfile.close()
			passfile.close()

		#Append to file and encrypt
		passfile = open("cPassfile.txt",'a')
		passfile.write(info+":"+"\n")
		passfile.close()
		encryptfile = open("ecpassfile.txt",'w')
		passfile = open("cPassfile.txt",'r')
		encrypt(passfile,encryptfile,encryptflag)
		passfile.close()
		encryptfile.close()


#Authentication function:
def authentication():
	n = 3
	while n > 0: 
		if n != 3:
			print "Try Again!"

		user = raw_input("\nEnter username: ")
		password = raw_input("\nEnter password: ")
		success = False

		if os.path.isfile("eepassfile.txt"):
			#Checking in ECB file:
			passfile = open("ePassfile.txt",'w')
			decryptfile = open("eepassfile.txt",'r')
			decrypt(decryptfile,passfile,'e')
			passfile.close()
			decryptfile.close()

			passfile = open("ePassfile.txt",'r')
			for line in passfile:
				seperate = line.split(":")
				if seperate[0] == user and seperate[1] == password:
					success = True
					break
	
			#Removing decrypted file after check
			os.remove("ePassfile.txt")

			if success == True:
				print "\nAuthenticated"
				return

		if os.path.isfile("ecpassfile.txt"):
			#Checking in CBC file:
			passfile = open("cPassfile.txt",'w')
			decryptfile = open("ecpassfile.txt",'r')
			decrypt(decryptfile,passfile,'c')
			passfile.close()
			decryptfile.close()

			passfile = open("cPassfile.txt",'r')
			for line in passfile:
				seperate = line.split(":")
				if seperate[0] == user and seperate[1] == password:
					success = True
					break
	
			#Removing decrypted file after check
			os.remove("cPassfile.txt")

			if success == True:
				print "\nAuthenticated"
				return	 

		if os.path.isfile("erpassfile.txt"):		
			#Checking in CTR file:
			passfile = open("rPassfile.txt",'w')
			decryptfile = open("erpassfile.txt",'r')
			decrypt(decryptfile,passfile,'r')
			passfile.close()
			decryptfile.close()

			passfile = open("rPassfile.txt",'r')
			for line in passfile:
				seperate = line.split(":")
				if seperate[0] == user and seperate[1] == password:
					success = True
					break

			#Removing decrypted file after check
			os.remove("rPassfile.txt")
	
			if success == True:
				print "\nAuthenticated"
				return	 

		if success == False:
			print "\nAuthentication failed"
			n = n-1
	if n == 0:
		print "Too many wrong attempts....Application terminated"
		sys.exit()

#Retrieve function
def retrieve(uname):

	reg = 0 
	check = 0
	
	if option != '1':
		user = raw_input("\nEnter the username: ")
		data = raw_input("\nEnter secret phrase: ")

	#check if file exists
	if os.path.isfile("eepassfile.txt"):

		#Checking in ECB file:
		passfile = open("ePassfile.txt",'w')
		decryptfile = open("eepassfile.txt",'r')
		decrypt(decryptfile,passfile,'e')
		passfile.close()
		decryptfile.close()

		passfile = open("ePassfile.txt",'r')
		for line in passfile:
			seperate = line.split(":")
			if option == '1':
				if seperate[0] == uname:
					print "Username already exists"
					return True
					reg = 1
			else:
				if seperate[0] == user and seperate[2] == data:
					print "Your password is "+seperate[1]
					check = 1
	
		#Removing decrypted file after check
		os.remove("ePassfile.txt")


	if os.path.isfile("ecpassfile.txt"):
	
		#Checking in CBC file:
		passfile = open("cPassfile.txt",'w')
		decryptfile = open("ecpassfile.txt",'r')
		decrypt(decryptfile,passfile,'c')
		passfile.close()
		decryptfile.close()

		passfile = open("cPassfile.txt",'r')
		for line in passfile:
			seperate = line.split(":")
			if option == '1':
				if seperate[0] == uname:
					print "Username already exists"
					return True
					reg = 1
			else:
				if seperate[0] == user and seperate[2] == data:
					print "Your password is "+seperate[1]
					check = 1
	
		#Removing decrypted file after check
		os.remove("cPassfile.txt")

	if os.path.isfile("erpassfile.txt"):

		#Checking in CTR file:
		passfile = open("rPassfile.txt",'w')
		decryptfile = open("erpassfile.txt",'r')
		decrypt(decryptfile,passfile,'r')
		passfile.close()
		decryptfile.close()

		passfile = open("rPassfile.txt",'r')
		for line in passfile:
			seperate = line.split(":")
			if option == '1':
				if seperate[0] == uname:
					print "Username already exists"
					return True
					reg = 1
			else:
				if seperate[0] == user and seperate[2] == data:
					print "Your password is "+seperate[1]
					check = 1

		#Removing decrypted file after check
		os.remove("rPassfile.txt")
	
	if option == '1':
		if reg == 0:
			return False

	if check == 0:
		print "\n There is no match for the given information. Please try again!!"
		return

#Change masterkey
def changekey():
	musersecret = raw_input("\nEnter secret phrase to change key: ")
	if msecret == hashlib.sha256(musersecret).hexdigest():
		changekey = raw_input("\nEnter new master key: ")
		cfgfile = open("appconfig.cfg",'w')
		config.set('keys','mkey',hashlib.sha256(changekey).hexdigest())
		config.write(cfgfile)
		cfgfile.close 	
	else:
		print "Incorrect phrase entered"

#check masterkey
n = 3
while n > 0:
	#ASk for masterkey and check
	Masterkey = raw_input("Please enter the passcode: ")
	if hashlib.sha256(Masterkey).hexdigest() == mkey:
		while option != '5':
			option = raw_input("\n1. Register \n2. Authentication \n3. Retreive password \n4. Change passcode \n5. Exit \n\n Enter choice:")

			if option == '1':
				register()

			elif option == '2':
				authentication()

			elif option == '3':
				retrieve(None)

			elif option == '4':
				changekey()

			elif option == '5':
				sys.exit()

			else:
				print "\n\n   Invalid option! Please enter the valid option"
	else:
		print "Incorrect passcode!"
		n = n-1
if n == 0:
	print "Too many wrong attempts....Application terminated"

