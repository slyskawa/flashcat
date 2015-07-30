Flashcat is a python script used to catalogue flash drives and sd cards.  It will do a recursive
directory listing of all files and store them in a sqlite database.

Originally created on Windows, it would ask for a drive letter and then use the volume name as the 
sqlite3 database name. Volume names were created using the following key:
    type-size-letter
    
Where:
    type = FD, FD3, SD, SATA
    size = # MB
    letter = A-Z

Examples:
    FD-8-A
    FD3-32-B
    SD-4-F
