#! /usr/bin/python
#Listfile.py Version 3.1


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
    vname = lvname[1].strip().replace(" ","_") #remove spaces from name
    vserial = lvID[1].split()[-1:][0]
    return vname,vserial

    if len(sys.argv) > 1:
        driveLetter=sys.argv[1]

x=driveLetter+":\\"
volumeName,volumeSerial = getVolumeID(driveLetter)
diskID="%s_%s"%(volumeName,volumeSerial)
id = diskID

dbName=id+".db3"
db=sqlite3.connect(dbName)
print dbName

fileDb=db.cursor()
fileDb.execute("create table if not exists files(filename varchar(255),ext varchar,filesize integer,filedate varchar(30),path varchar(255),MediaID varchar,rundate varchar(30),hash varchar(255))")
fileDb.execute("create table if not exists directory(dir varchar,id varchar)")
#fileDb.execute("delete from files")
#fileDb.execute("delete from directory")
filesBySize = {}
def get_fingerprint(filename):

    try:
        file = open(filename,'rb')
        digest = hashlib.sha1()
        data = file.read(65536)
        while len(data) != 0:
            digest.update(data)
            data = file.read(65536)
        file.close()
    except:
        return '0'
    else:
        return digest.hexdigest()
"""
        f = file(filename, "rb")
        try:
            f.seek(0)
        except:
            print filename, ": unable to seek"
            return 0
        return hashlib.md5(f.read(16000)).hexdigest()
"""

def walker(arg, dirname, fnames):
    d = os.getcwd()
    os.chdir(dirname)
    for f in fnames:
        if not os.path.isfile(f):
            fileDb.execute('''insert into directory(dir,id) values("%s","%s")'''%(f,id))
        else:
            f=f.lower()
            size = os.stat(f)[stat.ST_SIZE]
            ftime = os.stat(f)[stat.ST_MTIME]
            ext = os.path.splitext(f)
            extension= ext[1]
            fhash  = get_fingerprint(f)
            MediaID=id
            todaysDate=datetime.datetime.now().strftime("%m/%d/%Y")
            modifyDate = datetime.datetime.fromtimestamp(ftime)
            tDbValues = (f,extension,size,modifyDate,dirname,MediaID,todaysDate,fhash)
            fileDb.execute('''insert into files(filename,ext,filesize,filedate,path,MediaID,runDate,hash) values("%s","%s","%s","%s","%s","%s","%s","%s")'''%tDbValues)
            print ".",
            #print f,size,modifyDate,dirname,fhash
    os.chdir(d)


print 'Scanning directory "%s"....' % x
os.path.walk(x, walker, filesBySize)
db.commit()
fileDb.close()
db.close()

