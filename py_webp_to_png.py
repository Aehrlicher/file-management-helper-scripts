import subprocess
import re
import os
import sys
# not needed import optparse

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

# Convert given input file from 'webp' to 'png' via given program path
def convert_file(program_path, file_in):
  file_out = file_in[:-5] + ".png"    # replace '.webp' file ending with '.png'
  test = subprocess.check_call([program_path, file_in, "-o", file_out])


print("======= BEGIN WEBP Conversion Script =======")
print("This script will convert the given webp file(s) to png. \nIt utilises the webp library, either from your systems PATH, or as an executable in the current working directory!")

#set path to find webps in: either user provided and valid, or OSs current working directory
target_paths = []
inputs = []
if(len(sys.argv) < 2):
  inputs = input("Please enter the file(s) or path to convert, leave BLANK for the current workng directory. \n")
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


# Get OS environment and set executable program name accordingly
dwebp_path = ""
if (os.name == "posix"):
  # test if dwebp is available, or throw Exception
  try:
    print("Decoder package version: ")
    subprocess.check_call(["dwebp", "-version"])
    dwebp_path = "dwebp"
  except OSError as ose:
    print("ERROR: No webp decoder package found!")
    raise
elif(os.name == "nt"):
  # If Windows, find dwebp.exe either in a local folder or in PATH
  dwebp_match = re.match(r"(.+\\)*dwebp\.exe", os.environ('PATH'))
  if(not dwebp_match):
    dwebp_path = os.path.join(os.getcwd(), "libwebp", "bin", "dwebp.exe")
    if(not os.path.isfile(dwebp_path)):
      dwebp_path = os.path.join(os.getcwd(), "libwebp", "dwebp.exe")
      if(not os.path.isfile(dwebp_path)):
        raise Exception("No valid dwebp location found (Not in PATH or current working directory)!")
  else:
    dwepp_path = dwebp_match.group(0)
else:
  raise Exception("OS not recognised. Only Linux and Windows are supported!")


# Run conversion for all given pathes/files
for targets in target_paths:
  try:
    if(os.path.isdir(targets)):
      # If provided a directory convert all webp files in the directory
      # get all in current directory via os.walk() iterator, but only take next object, which will be the first, a list of all files
      convert_count = 0
      # (second then list of all sub directories) (See: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory)
      filenames = [x for x in next(os.walk(targets), (None, None, []))[2] if x.endswith('.webp')]
      if not filenames:
        raise Exception("Directory contains no webp-files. Skipping.")
      for webpfile in filenames:
        # construct full path to current webp file
        tmpinpath = os.path.join(targets, webpfile)
        convert_file(dwebp_path, tmpinpath)
        convert_count += 1
      print("Converted%2d images." % (convert_count))

    elif(os.path.isfile(targets)):
      # Convert given file
      convert_file(dwebp_path, targets)
    else:
      raise Exception("Not a directory or file.")
  except Exception as exct:
    # catch possible exceptions to continue script
    print ("Warning in directory or file '{}': {}".format(targets, exct))


print("======= END Script =======")
os._exit(os.EX_OK)
