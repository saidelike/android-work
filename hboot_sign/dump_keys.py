import binascii
import struct

#Get public keys from an HBOOT file
#with RSA public key format
#typedef struct RSAPublicKey {
#       int len;                  /* Length of n[] in number of uint32_t */
#       uint32_t n0inv;           /* -1 / n[0] mod 2^32 */
#       uint32_t n[RSANUMWORDS];  /* modulus as little endian array */
#       uint32_t rr[RSANUMWORDS]; /* R^2 as little endian array */
#} RSAPublicKey;
#source: platform/bootable/bootloader/legacy.git;a=blob;f=libc/rsa.h
def get_hboot_pubkeys(hbootname='hboot_7230_Vision_HEP_0.85.0015_111220.nb0', offsets_keys=[0x8D08D2BC]):

	realoffsets_keys = [x-0x8D000000 for x in offsets_keys]
	
	f = open(hbootname, 'rb')
	data = f.read()
	data += f.read()
	f.close()
	
	keys = {}
	for key in realoffsets_keys:
		key_data = data[key:key+520] # 4(size)|4(n0inv)|256(rsa_n)|256(rr)
		size_old = binascii.hexlify(key_data[0:4])
		size = ''
		for i in range(len(size_old), 0, -2):
			size += size_old[i-2:i]
		#print "size=0x%x" % int(size, 16)
		id_old = binascii.hexlify(key_data[4:8])
		id = ''
		for i in range(len(id_old), 0, -2):
			id += id_old[i-2:i]
		#print "id=0x%s" % id
		rsa_n_old = binascii.hexlify(key_data[8:8+256])
		rsa_n = ''
		for i in range(len(rsa_n_old), 0, -2):
			rsa_n += rsa_n_old[i-2:i]

    #RSA exponent is hardcoded, could be deduced from other parameters, but we are lazy here
		#rsa_e = '3' #hardcoded for htc hboot signature check
		rsa_e = '10001' #harcoded for htc unlock procedure
	
		keys[key] = [int(id, 16), int(rsa_n, 16), int(rsa_e, 16)]

	return keys

if __name__ == '__main__':

	#hbootname = 'mmcblk0p18.bin'
	#offsets_keys = [0x8D0812A4,0x8D0814AC,0x8D082358,0x8D082C7C,0x8D0834E0,0x8D084830,0x8D084A38,0x8D084C40,0x8D084E48,0x8D085050]
	#offsets_keys = [0x8D0834E0]
  #keys = get_hboot_pubkeys(hbootname, offsets_keys)

  keys = get_hboot_pubkeys()
  for k,v in keys.items():
		print "-- key at 0x%x --" % k
		print "id=0x%x" % v[0]
		print "rsa_n=0x%x" % v[1]
		print "rsa_e=0x%x" % v[2]
	
