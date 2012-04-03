import binascii, dump_keys, pkcs1
from Crypto.PublicKey import RSA
from Crypto.Util.number import ceil_shift
from Crypto.Hash import SHA256
import random, sys

# htc_unlock\PC1011000_VISION_GINGERBREAD_S_hboot_0.85.0015\{50F2F878-636A-496F-A7CB-544C067E0C4B}\rom\hboot_dz_0.85.0015.dump.bin (31/01/2012 15:36:32)
#   DebutPosition: 00077A64, FinPosition: 00077B40, Longueur: 000000DD
DecodedUnlockCodeStart2 = "\x00\x01\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x30\x31\x30\x0D\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x01\x05\x00\x04\x20"

#Generate HTC public keys in PEM format using data from HBOOT files
def generate_pubkey():
	keys = dump_keys.get_hboot_pubkeys()
	for k,v in keys.items():
		keyname = 'key_0x%x.pem' % k
		pkcs1.create_pub_pem(v[1], long(v[2]), keyname)

#Ciphers a message with a key
def do_encrypt(message, keyname='key_0x8d2bc.pem'):
	key = RSA.importKey(open(keyname).read())
	#see PKCS1_v1_5.py > verify()
	k = ceil_shift(key.size(), 3)
	if len(message) != k:
		print "key length does not match!"
		return ""
	m = key.encrypt(message, 0)[0]
	return m

#Returns a fake identifier token in raw format (bytes only)
def fake_identifier_token():
	first_byte = '\x00'

	#Fake
	imei = '123456789012345'
	sep = '0'
	serialno = 'SH0CERT12345'
	modelid = 'PC10*****'
	cidnum = '11111111'
	dw1dw2dw3dw4 = '\x45\x01\x00\x53\x12\x34\x56\x78\x47\x90\x41\x58\x29\x7f\xad\x4a'
	
	buf = first_byte + imei + sep + serialno + modelid + cidnum + dw1dw2dw3dw4
	
	junk = ''
	for i in range(256-len(buf)):
			junk += chr(random.randint(0,255))
	buf += junk

	return buf

#Returns the short version of a fake identifier token in raw format (bytes only), read from file
#Only check size
def fake_identifier_token_short(filename="idtokenshortreal.bin"):
	f = open(filename, 'rb')
	buf = f.read()
	f.close()

	if len(buf) != 0x3D:
		print "Length of identifier token short is WRONG!"
		return "\xAA"*0x3D
	else:
		print "Short identifier token read from file: %s." % filename
		return buf

#Displays the identifier token like a regular HTC device would do
def display_identifier_token(buf):
	if len(buf) != 256:
		print 'Identifier token length is not valid: %d != 256' % (len(buf))

	print '<<<< Identifier Token Start >>>>'
	for i in range(len(buf)/16):
		print binascii.hexlify(buf[i*16:(i+1)*16]).upper()
	print '<<<<< Identifier Token End >>>>>'

#Get an identifier token from file or generated randomly and displays the encrypted form like a regular HTC device would do
def get_identifier_token(keyname, inputdataname='idtokenreal.bin'):
	
	if True:
		buf = fake_identifier_token()
		f = open('idtoken.bin', 'wb')
		f.write(buf)
		f.close()
	else:
		f = open(inputdataname, 'rb')
		buf = f.read(256)
		f.close()

	print "len=%d bytes" % len(buf)
	m = do_encrypt(buf, keyname=keyname)
	display_identifier_token(m)

#The main function that do what a device would do, i.e. checks an Unlock_code.bin file with public key
# 1. Compute the short version of the identifier token
# 2. Deciphers the Unlock_code.bin
# 3. Checks if it matches
def check_unlock_code(keyname, idtokenname='idtokenshortreal.bin', unlockcodename='Unlock_code1.bin'):

	#read unlock code from HTC
	f = open(unlockcodename, 'rb')
	buf = f.read()
	f.close()
	print "%s is %d bytes." % (unlockcodename, len(buf))

	#decrypt it
	m = do_encrypt(buf, keyname=keyname)
	outname = unlockcodename + '.decrypted'
	f = open(outname, 'wb')
	f.write(m)
	f.close()
	print "Decrypted version is written to %s." % outname

	#compute SHA2 of identifier token short version
	idtokenshort = fake_identifier_token_short(idtokenname)
	h = SHA256.new()
	h.update(idtokenshort)
	print "SHA2 of token identifier: %s (len=%d bytes)" % (binascii.hexlify(h.digest()), len(h.digest()))

	#do we have a match?
	if DecodedUnlockCodeStart2[1:] != m[:223]:
		print "NO MATCHING starting pattern!"
	if m[223:] == h.digest():
		print "Unlock code %s is valid against our %s containing token idenfiers info." % (unlockcodename, idtokenname)
		print "OK"
	else:
		print "Unlock code %s is NOT valid against our %s containing token idenfiers info." % (unlockcodename, idtokenname)
		print "FAILED"

if __name__ == '__main__':
	#generate_pubkey()
	keyname = 'key_0x8d2bc.pem'
	check_unlock_code(keyname=keyname, idtokenname='idtokenshortfake.bin' , unlockcodename='Unlock_code1.bin')
