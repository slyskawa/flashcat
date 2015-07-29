#! /usr/bin/python
#Listfile.py Version 4.0

#Command line arguments, drive, directory


import os
import sys
import stat
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
        print "Enter VolumeID or Drive letter for flash drive"
        exit()
if sys.platform == 'darwin':
    diskID=sys.argv[1].upper()
    print diskID
else:
    if len(sys.argv) == 2:
        driveLetter=sys.argv[1]
        directory=":\\"
    if len(sys.argv) == 3:
        driveLetter=sys.argv[1]
        directory=":\\"+sys.argv[2]
    volumeName,volumeSerial = getVolumeID(driveLetter)
    diskID="%s_%s"%(volumeName,volumeSerial)
id = diskID
dirCount = 0
fileCount = 0

skip1=x+"/.Spotlight"
skip2=x+"/.fseventsd"
tSkipMe = (skip1,skip2)
print tSkipMe

dbName=id+".db3"
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

def walker(arg, dirname, fnames):
    d = os.getcwd()
    os.chdir(dirname)
    fileCount = 0
    for f in fnames:
        print "f"
        if not os.path.isfile(f):
            fileDb.execute('''insert into directory(dir,id) values("%s","%s")'''%(f,id))
            ldirCount.append(f)
            print "\nDir %s"%(f)
        else:
            f=f.lower()
            size = os.stat(f)[stat.ST_SIZE]
            ftime = os.stat(f)[stat.ST_MTIME]
            ext = os.path.splitext(f)
            extension= ext[1]
            fhash  = get_fingerprint(f)
            dname=os.path.splitdrive(dirname)[1]
            MediaID=id
            todaysDate=datetime.datetime.now().strftime("%Y-%m-%d")
            modifyDate = datetime.datetime.fromtimestamp(ftime)
            tDbValues = (f,extension,size,modifyDate,dname,MediaID,todaysDate,fhash)
            print "%s, %s, %s, %s, %s \n"%(MediaID,filename,ext,path,filedate)
            fileDb.execute('''insert into files(filename,ext,filesize,filedate,path,MediaID,runDate,hash) values("%s","%s","%s","%s","%s","%s","%s","%s")'''%tDbValues)
            #print ".",
            fileCount += 1
            print "%i "%(fileCount),
            #print f,size,modifyDate,dirname,fhash
    totalFiles.append(fileCount)
    os.chdir(d)

def directoryWalker(dirname):
    d = os.getcwd()
    os.chdir(dirname)
    fileCount = 0
    for root, dirs, allFiles in os.walk(dirname):
        #print "\nRoot=%s, dir=%s, file=%s"%(root,dirs,allFiles)
        for everyDir in dirs:
            fileDb.execute('''insert into directory(dir,id) values("%s","%s")'''%(everyDir,id))
            ldirCount.append(everyDir)
            print "\nDir %s"%(everyDir)
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
            if dname.startswith(tSkipMe):
                continue
            else:
                fileDb.execute('''insert into files(filename,ext,filesize,filedate,path,MediaID,runDate,hash) values("%s","%s","%s","%s","%s","%s","%s","%s")'''%tDbValues)
                #print ".",
                fileCount += 1
                print "%i "%(fileCount),
                print f,size,modifyDate,dirname,dname
    totalFiles.append(fileCount)
    os.chdir(d)


print 'Scanning directory "%s"....' % x
ldirCount = []

totalFiles=[]
#os.path.walk(x, walker, filesBySize)
directoryWalker(x)
dirCount=len(ldirCount)
fileCount=sum(totalFiles)
print totalFiles
#added 2012-01-23
#Dir field in directory table only contains dir.  Put in full path pulled.
fileDb.execute("insert into directory SELECT distinct path, MediaID from files")
db.commit()
fileDb.close()
db.close()
print ldirCount
print "\n\n%s\nDirectories=%i\nFiles=%i\nScanning complete!"%(dbName,dirCount,fileCount)
