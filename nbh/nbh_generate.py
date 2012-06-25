import binascii, sys, zlib, struct

#tested under windows
#for the HTC desire Z PC10DIAG.nbh
#so we are able to boot (from a S-OFF phone) our own code

def update_crc32(filename):
  f = open(filename, 'rb')
  data = f.read()
  f.close()

  (crc_file,) = struct.unpack("I", data[0x1BC:0x1BC+4])
  print "Current CRC of %s: 0x%08x" % (filename, crc_file)

  data0 = data[0x300:]
  #regular crc32 python does ^= -1 at the begining and does ^= -1 at the end
  #here we need to use 0 as iv and we do not want the xor at the end so we do it again to cancel it
  crc0 = binascii.crc32(data0, 0xFFFFFFFF)
  crc0 ^= 0xFFFFFFFF
  crc0 &= 0xFFFFFFFF #unsigned int value
  print "Computed CRC = 0x%08x " % (crc0)

  if crc_file == crc0:
    print "CRC is valid, exiting now."
  else:
    print "Updating CRC now..."
    f = open(filename, 'wb')
    data1 = data[:0x1BC] + struct.pack("I", crc0) + data[0x1BC+4:]
    f.write(data1)
    f.close()
    print "Done!"

# DOES include the complete header
def create_nbh(filename, template='PC10DIAG.nbh'):
  f = open("templates/" + template, 'rb')
  header = f.read(0x300)
  junk = f.read(4)
  header2 = f.read(0x570-0x300-4)
  f.close()
 
  f = open(filename, 'rb')
  data = f.read()
  f.close()

  out_filename = template
  print "Writing output file: %s" % out_filename
  f = open(out_filename, 'wb')
  to_write = header + data[0:4] + header2 + data[0x270:] # 0x570-0x300=0x270
  f.write(to_write)
  #we notice empirically the NBH needs to be a multiple of 256 bytes, otherwise the CRC check will fail
  #so we add padding we do not care
  f.write('\x00' * (256-(len(to_write) % 256))) 
  f.close()

  update_crc32(out_filename)

if __name__ == '__main__':
  #update_crc32(filename='PC10DIAG.nbh')
  #create_nbh("nbhcode.bin", template="PG88DIAG.nbh") #saga
  create_nbh("nbhcode.bin") #desire z
