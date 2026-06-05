import subprocess
import os
import sys
import re
import hashlib

# Recursive directory finder
def recursive_run(dir):
  return _recursive_run(dir)

def _recursive_run(dir):
  loc_dir = next(os.walk(dir), (None, None, None))
  dirs = loc_dir[1]
  cpath = loc_dir[0]
  ret = [dir]

  if not dirs:
    return [dir]

  for d in dirs:
    ret = ret + _recursive_run(os.path.join(cpath, d))
  return ret

#hash a file. Compatible with any Py 3 versions. From https://stackoverflow.com/a/44873382
def hash_file(filename):
  hash = hashlib.sha256()
  byte_array = bytearray(128*1024)
  mem_view = memoryview(byte_array)
  with open(filename, "rb", buffering=0) as f:
    for n in iter(lambda : f.readinto(mem_view), 0):
      hash.update(mem_view[:n])
  return hash.hexdigest()

#function for when walk runs into scandir errors, which are otherwise ignored
def report_walk_error(oserr: OSError):
  print("WARNING: Error in os.walk function: " + oserr)

print("======= BEGIN Duplicate Sorting Script =======")
print("This script will find duplicate files by their SHA256 hashes in a given directory and move them to a subdirectory called '__dup_files__'.")
#set path to find webps in: either user provided and valid, or OSs current working directory
target_paths = []
inputs = []
if(len(sys.argv) < 2):
  inputs = input("Please enter the directory(ies) to process. \n")
  target_paths = inputs.split(" ")
else:
  # collect all provided paths/files from args
  if (re.match(r"-+r(ecursive)?", sys.argv[1]) is not None):
    for arg in sys.argv[2:]:
     inputs += recursive_run(arg)
  else:
    inputs = sys.argv[1:]
  target_paths = inputs

print("Pathes provided: '{}'".format(target_paths))

# Prob. don't need to log moved duplicates
#out_file = open("duplicate_files.txt", "w")
for d in target_paths:

  #get all files in current dir
  filelist = next(os.walk(d, onerror=report_walk_error), (None, None, []))[2]
  dup_files_dir = os.path.join(d, "__dup_files__")
  dup_count = 0
  file_hash_list = set()
  for filename in filelist:
    file_path = os.path.join(d, filename)
    hashh = hash_file(file_path)
    if hashh not in file_hash_list:
      file_hash_list.add(hashh)
    else:
      dup_count += 1
      #make a dir to move duplicate files into if needed and not exists yet
      if (dup_count == 1):
        if not os.path.exists(dup_files_dir):
          os.makedirs(dup_files_dir)
      #move any subsequent duplicate files into the subdirectory
      dup_file_path = os.path.join(dup_files_dir, filename)
      os.replace(file_path, dup_file_path)
      print("Found duplicate file: '{}'".format(file_path))

      # out_file.write(file_path)
    #out_file.close()
  print("Folder %56s Found %2d duplicate files in this folder." % (d, dup_count))
print("======= END Script =======")
os._exit(os.EX_OK)
