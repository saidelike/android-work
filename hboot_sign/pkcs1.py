from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import binascii
import os.path
import dump_keys
from Crypto.Util.number import ceil_shift
from os import listdir

#Create a public key in PEM format using modulus and exponent
def create_pub_pem(n, e, pemname):
	key = RSA.construct((n, e))
	f = open(pemname, 'wb')
	f.write(key.exportKey('PEM'))
	f.close()

#Create a private key in PEM format using modulus and exponents
def create_priv_pem(n, e, d, pemname):
	key = RSA.construct((n, e, d))
	f = open(pemname, 'wb')
	f.write(key.exportKey('PEM'))
	f.close()

#Sign a message with a private key
def do_sign(message, keyname='priv.der'):
	key = RSA.importKey(open(keyname).read())
	h = SHA.new()
	h.update(message)
	signature = PKCS1_v1_5.sign(h, key)
	return signature

#useful when we need to compute hash one for all and test various keys
#use this before call
#h = SHA.new()
#h.update(message)
def do_verify_hash(h, signature, keyname='pub.der'):
	key = RSA.importKey(open(keyname).read())
	if PKCS1_v1_5.verify(h, key, signature):
		return True
	else:
		return False

def do_encrypt_hash(h, signature, keyname='pub.der'):
	key = RSA.importKey(open(keyname).read())
	#see PKCS1_v1_5.py > verify()
	k = ceil_shift(key.size(), 3)
	if len(signature) != k:
		print "key length does not match!"
		return False
	m = key.encrypt(signature, 0)[0]
	print "deciphered signature: %s" % binascii.hexlify(m)
	return False

#verify a message signature with a public key
def do_verify(message, signature, keyname='pub.der'):
	key = RSA.importKey(open(keyname).read())
	h = SHA.new()
	h.update(message)
	print "digest: %s" % binascii.hexlify(h.digest())
	if PKCS1_v1_5.verify(h, key, signature):
		return True
	else:
		return False

def check_htc(filename='rom.zip'):
	f = open(filename)
	signature = f.read(256)
	data = f.read()
	print "filename: %s" % filename
	#print "data length: %d bytes" % len(data)
	#print "Zip/Nbh begins with %s" % data[:2]
	h = SHA.new()
	h.update(data)
	print "digest: %s" % binascii.hexlify(h.digest())

	keys = dump_keys.get_hboot_pubkeys()
	for k,v in keys.items():

    #create public keys
		keyname = 'keys/key_0x%x.pem' % k
		create_pub_pem(v[1], long(v[2]), keyname)

		if do_verify_hash(h, signature, keyname):
			print "key match: 0x%x" % k

def check_all_files():
	for f in listdir('files'):
		check_htc('files/' + f)

def check_all_xtc():
	for dir1 in listdir('xtc'):
		for dir2 in listdir('xtc/' + dir1):
			print '-------- %s --------' % dir1
			for f in listdir('xtc/' + dir1 + '/' + dir2):
				check_htc('xtc/' + dir1 + '/' + dir2 + '/' + f)

if __name__ == '__main__':
	check_htc(filename='HBOOT-0.82.X000_PC10diag.nbh')
	#check_all_files()
	#check_all_xtc()
