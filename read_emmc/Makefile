all: usb

usb: usb.cpp
	g++ -lfuse -lserial -D_FILE_OFFSET_BITS=64 -DFUSE_USE_VERSION=22 -Wall usb.cpp -o usb
clean:
	rm usb 
