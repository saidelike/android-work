import os, struct, sys, zlib, gzip

def build_img(SOURCE="boot"):

	template = '%s.img' % SOURCE
	kernel = '%s_kernel.zImage.bin' % SOURCE
	#ramdisk = '%s_ramdisk.cpio'% SOURCE #also working
	ramdiskcompressed = '%s_ramdisk.cpio.gz'% SOURCE
	output = '%s-new.img'% SOURCE

	#get base address from template
	f = open(template, "rb")
	data = f.read(0x10)
	f.close()
	kernelLoadAddr, = struct.unpack("I", data[0xC:])
	baseAddr = kernelLoadAddr - 0x8000
	base = "0x%08X" % baseAddr

	#combine the kernel and your new ramdisk into the full image, using the mkbootimg program
	cmd = "mkbootimg --cmdline 'no_console_suspend=1 console=null' --base " + base + " --kernel " + kernel + " --ramdisk " + ramdiskcompressed + " --output " + output
	print cmd
	os.system(cmd)

def build_cpio_gzip(SOURCE='boot'):
	print "Rebuilding GZIPPED CPIO ramdisk..."

	ramdiskdir = '%s_ramdisk' % SOURCE
	ramdiskcompressed = '%s_ramdisk.cpio.gz'% SOURCE
	cwd = os.getcwd()
	os.chdir(ramdiskdir)
	cmd = "find . | cpio -o -H newc | gzip > ../../" + ramdiskcompressed 
	print cmd
	os.system(cmd)
	os.chdir(cwd)

def usage():
	print 'Usage: build_img.py <template.img>'
	print 'Eg: valid filenames: boot.img, recovery.img'
	sys.exit(0)

if __name__ == '__main__':


	if len(sys.argv) != 2:
		usage()

	if sys.argv[1][-4:] != '.img':
		print 'You must provide an .img file path.'
		usage()

	build_cpio_gzip(SOURCE=sys.argv[1][:-4])
	build_img(SOURCE=sys.argv[1][:-4])
