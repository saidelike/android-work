from os import listdir
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import binascii
import struct, sys

ROOT_PATH='DAT_2.1.1\\HTC Android\\'

def parse_hboot(data):
  version = data[0x4:0x10]
  spl = data[0x10:0x18]
  print 'hboot version: %s - %s' % (version, spl)
  ship = data[0x20:0x24]
  print 'shipped version: %s' % ship
  hboot_logo = data[0x30:0x3a]
  print 'logo: %s' % hboot_logo
  dirty = data[0x40:0x48]
  if dirty[0:4] == '\x00\x00\x00\x00':
    dirty = '(none)'
  print 'dirty: %s' % dirty

def parse_nbh(filename):
  f = open(filename, 'rb')
  data = f.read()
  f.close()
  print 'NBH size: %d kB' % (len(data) / 1024)

  #signature
  signature = data[:0x100]
  h = SHA.new()
  h.update(data[0x100:])
  print "digest: %s" % binascii.hexlify(h.digest())

  #magic
  magic = ''.join([data[0x100+i] for i in [0, 4, 8, 12, 16, 20, 24, 28]])
  print "magic: %s" % magic

  #update.zip name
  update = data[0x120:0x120+0x9]
  print 'update name: %s' % update

  #unknown
  unk_141 = ord(data[0x141])
  unk_1bX = struct.unpack('<I', data[0x1BC:0x1C0])[0]
  unk_1c1 = ord(data[0x1C1])
  unk_240 = struct.unpack('<I', data[0x240:0x244])[0]
  print 'unk_141=%02x, unk_1bX=%08x, unk_1c1=%02x, unk_240=%08x' % (unk_141, unk_1bX, unk_1c1, unk_240)

  for i in range(0x130, 0x2B0):
    if i == 0x141 or i in [0x1BC, 0x1BD, 0x1BE, 0x1BF] or i == 0x1c1 or i in range(0x240, 0x245):
      continue
    if data[i] != '\x00':
      print '%x -> %x' % (i, ord(data[i]))

  #cid
  cid = data[0x2C0:0x2C8]
  print 'cid=%s' % cid

  #unknown2
  for i in range(0x2C8, 0x2E0):
    if data[i] != '\x00':
      print '%x -> %x' % (i, ord(data[i]))

  #version
  version = data[0x2E0:0x2E8]
  info = data[0x2F0:0x2F8]
  print 'version=%s %s' % (version, info)

  #HBOOT
  hboot = data[0x300:]
  parse_hboot(hboot)

def loop_on_files(filters=[]):
  for dir1 in listdir(ROOT_PATH):
    if filters and dir1 not in filters:
      continue
    print '----------- %s -----------' % dir1
    for dir2 in listdir(ROOT_PATH + dir1):
      for f in listdir(ROOT_PATH + dir1 + '\\' + dir2):
        filename = ROOT_PATH + dir1 + '\\' + dir2 + '\\' + f
        print filename
        parse_nbh(filename)
      print ''

if __name__ == '__main__':
  #loop_on_files()
  #loop_on_files(filters=['Bravo - Desire'])
  parse_nbh(sys.argv[1])
