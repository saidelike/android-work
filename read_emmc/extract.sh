# Mount the phone userdata partition and get the listed files from it on the local PC

#FILES_LIST=files_list_DZ.txt #HTC Desire Z
FILES_LIST=files_unlock.txt #to unlock the HTC Desire Z
MOUNT_POINT=mnt2 #mounted using FUSE+mount
OUT_DIR=dump
CACHE_DIR=out

echo "Mouting userdata partition..."
time mount -o loop,ro -t ext2 mnt/dev mnt2

echo "Making a copy of the cache index (in case of)..."
cp $CACHE_DIR/index $CACHE_DIR/index_mnt

if [ ! -d $OUT_DIR ]
then
	mkdir $OUT_DIR
fi

for filename in $(cat $FILES_LIST)
do
	filepath=`echo $MOUNT_POINT/${filename:6}` #remove /data/ (6 characters) because we read userdata directly (mounted as /data in filesystem)
	echo "Processing: "$filepath"..."
	time cp $filepath $OUT_DIR/
done
echo "Done."
