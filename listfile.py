#! /usr/bin/python
#Listfile.py 
Version="4.1"
print "Version %s"%Version

#Command line arguments, drive, directory


import os
import sys
import stat
import re
import hashlib
import datetime
import sqlite3


def getVolumeID(dLetter):
    dLetter=dLetter+":"
    vID = os.popen('vol '+dLetter, 'r').read()  #Read windows volume information
    lvID = vID.splitlines()  #Break into two lines
    lvname = lvID[0].split("is") #Get volume name
    print lvname
    vname = lvname[1].strip().replace(" ","_") #remove spaces from name
    vserial = lvID[1].split()[-1:][0]
    return vname,vserial

if len(sys.argv) < 2:
    di = raw_input("Enter VolumeID or Drive letter for flash drive: ")
    diskID = "/Volumes/{}".format(di)
    x = diskID
    did = di.upper()
else:
    if sys.platform == 'darwin':
        diskID=sys.argv[1].upper()
        print diskID
        x="/Volumes/"+diskID
        did = diskID
    if len(sys.argv) == 2:
        driveLetter=sys.argv[1]
        directory=":\\"
    if len(sys.argv) == 3:
        driveLetter=sys.argv[1]
        directory=":\\"+sys.argv[2]
        x=driveLetter+directory
    volumeName,volumeSerial = getVolumeID(driveLetter)
    diskID="%s_%s"%(volumeName,volumeSerial)
    did = diskID
print did
dirCount = 0
fileCount = 0
#Skip Mac hidden files
skip1=".Spotlight"
skip2=".fseventsd"
tSkipMe = (skip1,skip2)
regexSkipMe= skip1 + "|" + skip2
reSkipMe = re.compile(regexSkipMe)
print tSkipMe

dbName = did+".db3"
db=sqlite3.connect(dbName)
print dbName

fileDb=db.cursor()
fileDb.execute("create table if not exists files(filename varchar(255),ext varchar,filesize integer,filedate varchar(30),path varchar(255),MediaID varchar,rundate varchar(30),hash varchar(255))")
fileDb.execute("create table if not exists directory(dir varchar,id varchar)")
fileDb.execute("delete from files")
fileDb.execute("delete from directory")
filesBySize = {}
def get_fingerprint(filename):

    try:
        file = open(filename,'rb')
        loopCnt=20
        digest = hashlib.sha1()
        data = file.read(65536)
        while len(data) != 0:
            digest.update(data)
            data = file.read(65536)
            #2012-01-23 Added loopcount for large files.
            loopCnt = loopCnt - 1
            if loopCnt == 0:
                break
        file.close()
    except:
        return '0'
    else:
        return digest.hexdigest()

def directoryWalker(dirname):
    d = os.getcwd()
    print "Line 120:%s"%dirname
    os.chdir(dirname)
    fileCount = 0
    for root, dirs, allFiles in os.walk(dirname):
        #print "\nRoot=%s, dir=%s, file=%s"%(root,dirs,allFiles)
        #print "\nRoot=%s, dir=%s\n"%(root,dirs)
        for everyDir in dirs:
            fileDb.execute('''insert into directory(dir,id) values("%s","%s")'''%(everyDir,id))
            ldirCount.append(everyDir)
            print "\nDirectory: %s"%(everyDir)
        skipMe = reSkipMe.search(root)
        if skipMe:
            print 20*"#"
            print "\nRoot=%s, dir=%s, file=%s"%(root,dirs,allFiles)
            print "Skipping: %s - %s\n"%(root,everyDir)  
            print 20*"#"
        else:
#start
            for everyFile in allFiles:
                fullName=os.path.join(root,everyFile)
                f=everyFile.lower()
                size = os.stat(fullName)[stat.ST_SIZE]
                ftime = os.stat(fullName)[stat.ST_MTIME]
                ext = os.path.splitext(f)
                extension= ext[1]
                fhash  = get_fingerprint(fullName)
                dname=os.path.splitdrive(root)[1]
                MediaID=id
                todaysDate=datetime.datetime.now().strftime("%Y-%m-%d")
                modifyDate = datetime.datetime.fromtimestamp(ftime)
                tDbValues = (f,extension,size,modifyDate,dname,MediaID,todaysDate,fhash)
                #print "%s, %s, %s, %s, %s \n"%(MediaID,everyFile,extension,dname,modifyDate)
                if dname.startswith(tSkipMe):
                    continue
                else:
                    fileDb.execute('''insert into files(filename,ext,filesize,filedate,path,MediaID,runDate,hash) values("%s","%s","%s","%s","%s","%s","%s","%s")'''%tDbValues)
                    print ".",
                    fileCount += 1
                    #print "%i "%(fileCount),
                    #print f,size,modifyDate,dirname,dname
#end
    totalFiles.append(fileCount)
    os.chdir(d)


print 'Scanning directory "%s"....' % diskID
ldirCount = []

totalFiles=[]
#os.path.walk(x, walker, filesBySize)
directoryWalker(x)
dirCount=len(ldirCount)
fileCount=sum(totalFiles)
print 'Total files: {}'.format(totalFiles)
#added 2012-01-23
#Dir field in directory table only contains dir.  Put in full path pulled.
fileDb.execute("insert into directory SELECT distinct path, MediaID from files")
db.commit()
fileDb.close()
db.close()
print 'ldircount: {}'.format(ldirCount)
print "\n\n%s\nDirectories=%i\nFiles=%i\nScanning complete!"%(dbName,dirCount,fileCount)
print "Version %s"%(Version)
