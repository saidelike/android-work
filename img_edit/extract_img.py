import struct, sys, zlib, gzip, os

def convert_bytes(bytes):
		bytes = float(bytes)
		if bytes >= 1099511627776:
				terabytes = bytes / 1099511627776
				size = '%.2fT' % terabytes
		elif bytes >= 1073741824:
				gigabytes = bytes / 1073741824
				size = '%.2fG' % gigabytes
		elif bytes >= 1048576:
				megabytes = bytes / 1048576
				size = '%.2fM' % megabytes
		elif bytes >= 1024:
				kilobytes = bytes / 1024
				size = '%.2fK' % kilobytes
		else:
				size = '%.2fb' % bytes
		return size

# see: http://android.git.kernel.org/?p=platform/system/core.git;a=blob;f=mkbootimg/bootimg.h
# http://www.simtec.co.uk/products/SWLINUX/files/booting_article.html#d0e309
def extract_img(SOURCE='boot'):
	
	IMG_FILENAME = '%s.img' % SOURCE
	KERNEL_FILENAME = '%s_kernel.zImage.bin' % SOURCE
	RAMDISK_FILENAME = '%s_ramdisk.cpio'% SOURCE
	
	f = open(IMG_FILENAME, 'rb')
	data = f.read()
	f.close()
	#print "file size: %d bytes" % len(data)
	
	armGzipDecodingCodeOffset = 0x800 # code that gzip decode the kernel and ramdisk
	gzip_pattern = '\x1F\x8B\x08\x00'
	
	res = struct.unpack('8sIIIIIIIIII16s512s8I', data[:0x260])
	(magic, kernelSize, kernelLoadAddr, ramdiskSize, ramdiskLoadAddr, ram2Size, ram2LoadAddr, tagsAddr, pageSize, unused1, unused2, bootName, cmdLine, id1, id2, id3, id4, id5, id6, id7, id8) = res

	if magic != 'ANDROID!':
		print 'The magic is not valid!'
		sys.exit(0)

	if True:
		print 'magic=%s' % magic
		print 'kernelSize=%X (%s)' % (kernelSize, convert_bytes(kernelSize))
		print 'kernelLoadAddr=%08X' % kernelLoadAddr
		print 'ramdiskSize=%X (%s)' % (ramdiskSize, convert_bytes(ramdiskSize))
		print 'ramdiskLoadAddr=%08X' % ramdiskLoadAddr
		print 'ram2Size=%X' % ram2Size
		print 'ram2LoadAddr=%X' % ram2LoadAddr
		print 'tagsAddr=%X' % tagsAddr
		print 'pageSize=%X' % pageSize
		print 'unused1=%X' % unused1
		print 'unused2=%X' % unused2
		print 'bootName=%s' % bootName
		print 'cmdLine=%s' % cmdLine
		print 'id=%x,%x,%x,%x,%x,%x,%x,%x' % (id1,id2,id3,id4,id5,id6,id7,id8) # offset is 0x240 from boot_img_hdr

	#debug
	#sys.exit(0)

	#check zImage consistency
	kernelOffset = 0x800
	res = struct.unpack('III', data[kernelOffset+0x24:kernelOffset+0x24+0xC])
	(magic_zImage, addrStart_zImage, addrEnd_zImage) = res
	if magic_zImage != 0x016F2818:
		print "Kernel zImage is not a valid one :%x!" % magic_zImage
		sys.exit(0)
	print "Kernel zImage length: %s" % convert_bytes(addrEnd_zImage-addrStart_zImage)

	#count how many ramdisks we have (here we only support extracting one!)
	cnt_gzip = 0
	start = 0
	off = data.find(gzip_pattern, start)
	while off != -1:
		start = start + off + 1
		off = data.find(gzip_pattern, start)
		cnt_gzip += 1
	print "Found %d GZIPed ramdisks" % cnt_gzip
	if cnt_gzip == 0:
		print "No ramdisk found, check your .img file"
		sys.exit(0)
	ramdiskOffset = data.find(gzip_pattern)

	#kernel zImage is from 0x800 to begining of first GZIPPED ramdisk (trailing zeros betweens them)
	f2 = open(KERNEL_FILENAME, 'wb')
	kernel = data[kernelOffset:ramdiskOffset]
	f2.write(kernel)
	f2.close()

	#ramdisk
	print "Extracting the first ramdisk only..."
	f3 = open(RAMDISK_FILENAME, 'wb')
	ramdisk = zlib.decompress(data[ramdiskOffset:], 16+zlib.MAX_WBITS)
	f3.write(ramdisk)
	f3.close()

	print '%s and %s extracted! Done.' % (KERNEL_FILENAME, RAMDISK_FILENAME)

def extract_cpio(SOURCE="boot"):
	print "Extracting CPIO ramdisk..."
	ramdisk = '%s_ramdisk.cpio'% SOURCE
	ramdiskdir = '%s_ramdisk' % SOURCE
	cwd = os.getcwd()
	print cwd
	os.mkdir(ramdiskdir)
	os.chdir(ramdiskdir)
	cmd = "cat ../../" + ramdisk + " | cpio -i"
	print cmd
	os.system(cmd)
	os.chdir(cwd)

def cleanup(SOURCE="boot"):

	IMG_FILENAME = '%s.img' % SOURCE
	if not os.access(IMG_FILENAME, os.R_OK):
		print "File not valid to execute a cleanup"
		return
	print "Cleaning temporary files..."

	ramdisk = '%s_ramdisk.cpio'% SOURCE
	KERNEL_FILENAME = '%s_kernel.zImage.bin' % SOURCE
	ramdiskcompressed = '%s_ramdisk.cpio.gz'% SOURCE
	ramdiskdir = '%s_ramdisk' % SOURCE
	output = '%s-new.img'% SOURCE
	try:
		os.remove(ramdisk)
	except OSError:
		pass
	try:
		os.remove(KERNEL_FILENAME)
	except OSError:
		pass
	try:
		os.remove(ramdiskcompressed)
	except OSError:
		pass
	try:
		os.remove(output)
	except OSError:
		pass
	cmd = "rm -Rf " + ramdiskdir
	print cmd
	os.system(cmd)

def usage():
	print 'Usage: extract_img.py <filename.img>'
	print 'Eg: valid filenames: boot.img, recovery.img'
	sys.exit(0)

if __name__ == '__main__':

	if len(sys.argv) != 2:
		usage()

	if sys.argv[1][-4:] != '.img':
		print 'You must provide an .img file path.'
		usage()

	cleanup(sys.argv[1][:-4])
	extract_img(sys.argv[1][:-4])
	extract_cpio(sys.argv[1][:-4])
