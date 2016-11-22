This program is a python script that takes disk images as input and gives the following as output.

1. A folder that contains all pdf and image files in the given disk images.
2. A database that contains the filename, md5 hash and the metadata of the files stored in the above folder
3. A report containing the same information as the database in the form of an excel sheet (.xlsx).

Python libraries required to execute the script:

subprocess, hashlib, sqlite3, os, shutil, magic (might need to be installed), pyPdf (might need to be installed), PIL (might need to be installed), xlsxwriter (might need to be installed), sys


How to execute this program?

1. Store the disk image files in a folder. No other files must be present in the folder.
2. In the command prompt or terminal run the program using python (name_of_script).py
3. Enter the entire path of the folder that contains the disk images as input.
   (For example, This/is/the/path/to/the/folder)

