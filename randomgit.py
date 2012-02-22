#!/usr/bin/env python
## TODO: less mixed file types DONE
## TODO: less ramifications (truncate after a certain depth) DONE
## TODO: file/dir modification and removal DONE
from __future__ import print_function
import os, random, string, subprocess, time, shutil, md5

extensions = ['css', 'js', 'html', 'cpp', 'txt', 'png', 'c']

def make_empty_file(path, name):
	fullpath = os.path.join(path, name)
	with open(fullpath, "a"):
		os.utime(fullpath, None)

def make_directory(path, name):
	fullpath = os.path.join(path, name)
	if not os.path.exists(fullpath):
		os.mkdir(fullpath)

def make_random_name():
	return ''.join(random.choice(string.hexdigits[:-6]) for n in range(32))

def make_random_extension():
	return random.choice(extensions)

def make_not_so_random_extension(path):
	return extensions[((int(path.encode('hex'), 16) % len(extensions)) + random.randrange(2)) % len(extensions)]

# def make_random_file(path):
# 	name = make_random_name()
# 	make_empty_file(path, name)
# 	return name

def make_random_file(path):
	name = make_random_name()
	
	if random.random() < .95:
		name = '.'.join([name, make_not_so_random_extension(path)])
	
	make_empty_file(path, name)

	return name

def make_random_directory(path):
	name = make_random_name()
	make_directory(path, name)
	return name


this_dir = os.getcwd()

# Path selection
while True:
	print("Choose base path (type 'c' for path based on %s)"%this_dir)

	user_dir = raw_input()

	if user_dir is "c":
		print("Available subdirectories: " + str(os.walk(this_dir).next()[1]))
		print(this_dir, end="/")
		user_dir = os.path.join(this_dir, raw_input())

	if os.path.exists(user_dir):
		break
	else:
		print("Sorry, the chosen path does not exist")
		continue

# Set current dir to selected dir
os.chdir(user_dir)




cycle = 0

while True:
	walker = os.walk(user_dir)
	cycle += 1

	max_new_files = random.randrange(1, 10)
	max_new_dirs = random.randrange(1, 3)
	max_edits = random.randrange(1, 4)
	max_removals = random.randrange(1, 2)

	new_files, new_dirs, edits, removals = 0, 0, 0, 0

	try:
		while True:
			name, directories, files = walker.next()

			# Shuffle directories and files so that they're explored in a different order each time
			random.shuffle(directories)
			random.shuffle(files)

			continue_making_files = len(files) < 25
			continue_making_dirs = len(directories) < 15

			depth = name.count(os.sep) - user_dir.count(os.sep)

			print("\n ==> In: %s"%name)
			
			# Check for hidden directories and don't explore them
			for directory in directories:
				if directory.startswith('.'):
					del directories[directories.index(directory)]
			
			# Remove some directories
			for directory in directories:
				if random.random() > .999:
					shutil.rmtree(os.path.join(name, directory))
					print("  => Removed dir: %s"%directory)
					del directories[directories.index(directory)]

				

			for file in files:
				if random.random() > .998 and edits < max_edits:
					with open(os.path.join(name, file), 'w') as open_file:
						open_file.write(make_random_name())
					edits += 1
					print("  => Wrote to file: %s"%file)
				else:
					if random.random() > .998 and removals < max_removals:
						os.remove(os.path.join(name, file))
						removals += 1
						print("  => Removed file: %s"%file)


			for n in range(random.randrange(0, 4)):
				if new_files < max_new_files and continue_making_files and random.random() > .80:
					rand_name = make_random_file(name)
					new_files += 1
					print("  => Created file: %s"%rand_name)

			for n in range(random.randrange(0, depth+2)):
				if new_dirs < max_new_dirs and continue_making_dirs and depth < 4 and random.random() > .80:
					rand_name = make_random_directory(name)
					new_dirs += 1
					print("  => Created dir: %s"%rand_name)


	except StopIteration:
		print("===> Committing changes")
		#time.sleep(0.2)
		#time.sleep(2)
		# Add files
		subprocess.call(["git", "add", "."])

		# Commit
		subprocess.call(["git", "commit", "-a", "-m", "%d"%cycle])

		continue