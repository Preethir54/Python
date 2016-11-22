from Crypto import Random
from Crypto.Cipher import AES
import ConfigParser
import os

#Creating config file
cfgfile = open("appconfig.cfg",'w')

#initializing values of keys and IV
IV = 32 * '\x00'
IVhalf = 16 * '\x00'
keyrand = os.urandom(32)
masterkey = '7e472acf339432f257068efb56baf925cea5eeba675552aba34142ec616340ac'
msecret = 'a00bec422eb3e93cfc8315ba2fff0367b394be0d166bdd4b7be0734cfeb7e4bc'
enckey = msecret[:32]
encryptor = AES.new(enckey, AES.MODE_CBC, IV=IVhalf)
key = encryptor.encrypt(keyrand)

#Adding data to config file
config = ConfigParser.ConfigParser()

config.add_section('keys')
config.set('keys', 'key', key)
config.set('keys', 'mkey', masterkey)
config.set('keys', 'secret', msecret)
config.add_section('init_vector')
config.set('init_vector', 'IV', IV)
config.set('init_vector', 'IV2', IVhalf)
config.write(cfgfile)

#close the file
cfgfile.close()
