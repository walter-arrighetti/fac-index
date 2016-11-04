#!/usr/bin/python
##########################################################
#  fac-index 2.0                                         #
#                                                        #
#    Scans throughout any storage compatible with the    #
#    host OS and compiles a disk index file in UTF-8     #
#    ASCII text format of the whole folder structure     #
#    file/directory sizes. Sequences of files are also   #
#    acknowledged, computing overall size and their      #
#    numbering range, eventually reporting the number    #
#    of missing files in the sequence.                   #
#                                                        #
#    Copyright (C) 2009 Walter Arrighetti, PhD           #
#    All Rights Reserved.                                #
##########################################################
import smtplib
import string
import stat
import math
import time
import sys
import os
import re

################
##  DATA Dictionary contains all the information to "tailor" this script to your facility data-management needs
##  !!  Please only modify data within the DATA Python dictionary to preserve original funcitonalities.
################
DATA = {
	'Location':"",
	'SI':False,								# Whether SI units (kB,MB,GB,...) will be used rather than binary ones (kiB,MiB,GiB,...)
	'email?':False,							# Whether emails should be also sent or not
	'path':{									# Dictionary with paths (there's an option for differentiating among Windows, Linux and MacOS paths)
		'local':None,							# Path where default text indexes are generated (default path if left to None)
		'remote':None,							# Additional path (e.g. on a remote, redundant storage) for a secondary copy of the indexes (no secondary copy if None)
	},
	'email source':"fac-index@localhost",		# Default sender email address (used if an acknowledged user is not present in dictionary below)
	'recipients':[								# List of email recipients (must be at least one if emails are enabled)
		"recipient1@localhost",
	#	"recipient2@localhost",
	#	"recipient3@localhost",
	],
	'authorized':{						# user-account vs. email address lookup (to acknowledge authorized users only)
	#	"root":"sysadmins@localhost",
	#	"Administrator":"sysadmins@localhost",
	#	"admin":"sysadmins@localhost",
	#	"name.surname":"surnamen@localhost",
		"employee1":"employee1@localhost",
		"employee2":"employee2@localhost",
		"employee3":"employee3@localhost",
		"DataIO":"dataio@localhost",
		"datamgr":"datamanagement@localhost",
		"account":"accounting@localhost",
	},
	'SMTP':{
		'server':"localhost",					# Hostname (or IP address) of SMTP server to send emails to
		'port':None,							# Listening TCP/IP port of the SMTP server (default if left to 'None')
		'username':None,						# Username (email address?) of SMTP authenticating user (leave 'None' for NO authentication)
		'password':"",							# Password for SMTP authentication (if any)
		'SSL?':False,							# Whether SMPTS (SMTP over SSL) is to be used
		}
}



VERSION = "2.0"
if 'HOST' in os.environ.keys():	HostName=os.environ['HOST']
elif 'HOSTNAME' in os.environ.keys():	HostName=os.environ['HOSTNAME']
elif 'COMPUTERNAME' in os.environ.keys():	HostName=os.environ['COMPUTERNAME']
else:	HostName="unknown"
if (('OS' in os.environ.keys()) and os.environ['OS'].lower().startswith('win')) or (('OSTYPE' in os.environ.keys()) and os.environ['OSTYPE'].lower().startswith('win')):
	Windows, dirsep = True, '\\'
	mailing_list_path="C:\\Program Files\\Common Files\\"
	paths={
		'local':DATA['path']['local'],		# Overrides local path for Windows-specific execution
		'remote':DATA['path']['remote'],	# Overrides remote path for Windows-specific execution
	}
	try:
		import win32file
		Win32API = True
	except:	Win32API = True
else:
	Windows, dirsep = False, '/'
	mailing_list_path="/srv/"		# Full path where DI_mailing_list.txt with updated recipients' list is to be found
	paths={
		'local':DATA['path']['local'],		# Overrides local path for non-Windows-specific execution
		'remote':DATA['path']['remote'],	# Overrides remote path for non-Windows-specific execution
	}

CXFSpaths=[]

SI=DATA['SI']
writetxt=True
sendmail=sendable=DATA['email?']
mailing_list=DATA['recipients']
full_perm=stat.S_ISUID|stat.S_ISGID|stat.S_IREAD|stat.S_IWRITE|stat.S_IEXEC|stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH|stat.S_IWUSR|stat.S_IWGRP|stat.S_IWOTH|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH|stat.S_IEXEC|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH

outx=[""]
metatree={}

#	List of directory names to EXCLUDE from the disk indexes
exclude_dirs = CXFS_exclude_dirs = [
	"_","Disk_Index",
	"RECYCLER","Recycled",".Trash-root",".Trashes",".Spotlight-V100","$RECYCLE.BIN","$Recycle.Bin",".fseventsd",
	"System Volume Information",".DS_Store","$$PendingFiles","FOUND.000","FOUND.001","FOUND.002","FOUND.003","FOUND.004","FOUND.005","FOUND.006","FOUND.007","FOUND.008","FOUND.009","FOUND.010","FOUND.000","Found.001","Found.002","Found.003","Found.004","Found.005","Found.006","Found.007","Found.008","Found.009","Found.010",
	"wt","192.168.2.75@wt","stonefs","sacc_data"
]
excluded_files=["autorun.inf","autorun.ico",".desktop",".Desktop",".Thumbs.db","._.Trashes",".dustbust-data"]


def getdirsize(path,stream=sys.stdout):
	dirtree=[]
	for root, dirs, files in os.walk(path):
		dirsize=sum(os.path.getsize(os.path.join(root,name)) for name in files)
		dirfilenum=len(files)
		print >>stream, ("%sB\t%s\t%s"%(sizeprint(dirsize),dirfilenum,root))


def sizeprint(mag, SI=True, decimaldigits=-1):
	size,prefix=float(mag),''
	if SI:
		if size > 1000000000000000L:
			size /= 1000000000000000L
			prefix='P'
		elif size > 1000000000000L:
			size /= 1000000000000L
			prefix='T'
		elif size > 1000000000:
			size /= 1000000000
			prefix='G'
		elif size > 1000000:
			size /= 1000000
			prefix='M'
		elif size > 1024:
			size /= 1000
			prefix='k'
	else:
		if size > 1125899906842624L:
			size /= 1125899906842624L
			prefix='Pi'
		elif size > 1099511627776L:
			size /= 1099511627776L
			prefix='Ti'
		elif size > 1073741824L:
			size /= 1073741824L
			prefix='Gi'
		elif size > 1048576:
			size /= 1048576
			prefix='Mi'
		if size > 2047:
			size /= 1024
			prefix='ki'
	if decimaldigits<0:
		if size%1==0:	return "%d%s"%(int(size),prefix)
		else:
			if prefix in ['k','M','ki','Mi']:	return ("%.01f%s"%(size,prefix))
			else:	return ("%.02f%s"%(size,prefix))
	return (("%%.%df%%s"%decimaldigits)%(size,prefix))


def listfileseq(path, recurse=False, BLKsize=0, include_exts=[], exclude_dirs=[]):
	isseq,result = False,None
	filecount=dircount=totsize=totBLKsize=0
	min=max=cur=0
	objsize=filesize=missing=idx=pidx=0
	dir=name=base=ext=pbase=pext=""
	FS = re.compile(r"(?P<prefix>.*\D)?(?P<idx>\d*)")
	exts=['.'+e.lower() for e in include_exts]
	L=[]
	try:	basepath=os.path.abspath(path)
	except:
		if BLKsize:	elems = [[path,0,0,0,0],"!"]
		else:	elems = [[path,0,0,0],"!"]
		return elems
	if recurse:
		if BLKsize:	elems = [[basepath,0,0,0,0]]
		else:	elems = [[basepath,0,0,0]]
	else:	elems = []
	try:	preL = sorted(os.listdir(basepath), cmp=lambda x,y: cmp(x.lower(),y.lower()))
	except:
		elems.append(["!",True,basepath])
		return elems
	for k in range(0,len(preL)):
		if os.path.isdir(os.path.join(basepath,preL[k])):	L.append(preL[k])
	for k in range(0,len(preL)):
		if os.path.isfile(os.path.join(basepath,preL[k])):	L.append(preL[k])
	del preL
	for k in range(0,len(L)):
		LL=os.path.join(basepath,L[k])
		(dir,name)=os.path.split(LL)
		(base,ext)=os.path.splitext(name)
		if os.path.isfile(LL):
			filecount += 1
			try:	filesize=os.path.getsize(LL)
			except:
				continue
				filesize=0
			totsize += filesize
			if BLKsize:
				fileblk = int(math.ceil(float(filesize)/BLKsize))
				totBLKsize += fileblk
			result=FS.search(base)
			if result.group('idx')=="" and isseq:
				if min==max:
					if pidx:
						if BLKsize:	elems.append((False,("%%s%%0%dd"%pidx)%(pbase,max),0,pext,0,0,objsize,fileblk,0))
						else:	elems.append((False,("%%s%%0%dd"%pidx)%(pbase,max),0,pext,0,0,objsize,0))
				else:
					if BLKsize:	elems.append((True,pbase,pidx,pext,min,max,objsize,fileblk,missing))
					else:	elems.append((True,pbase,pidx,pext,min,max,objsize,missing))
				min=max=cur=pidx=idx=missing=0
				isseq=False
				pbase=pext=""
			if exts==[] or (exts!=[] and (base[0]!='.' and ext!='' and ext.lower() in exts)):
				if result.group('idx')=="":
					if BLKsize:	elems.append((False,base,0,ext,0,0,filesize,fileblk,0))
					else:	elems.append((False,base,0,ext,0,0,filesize,0))
				else:
					base,cur,ext = result.group('prefix'),int(result.group('idx')),os.path.splitext(name)[1]
					if not base:	base=""
					idx=len(result.group('idx'))
					if base==pbase and idx==pidx and ext==pext:
						if cur!=max+1:	missing += cur-max-1
						max=cur
						objsize += filesize
					else:
						if isseq:
							if min==max:
								if BLKsize:	elems.append((False,("%%s%%0%dd"%pidx)%(pbase,max),0,pext,0,0,objsize,fileblk,0))
								else:	elems.append((False,("%%s%%0%dd"%pidx)%(pbase,max),0,pext,0,0,objsize,0))
							else:
								if BLKsize:	elems.append((False,("%%s%%0%dd"%pidx)%(pbase,max),0,pext,0,0,objsize,fileblk,0))
								else:	elems.append((True,pbase,pidx,pext,min,max,objsize,missing))
						pbase,pidx,pext = base,idx,ext
						min=max=cur
						idx=missing=0
						isseq=True
						objsize = filesize
					if k==len(L)-1:
						if min==max:
							if BLKsize:	elems.append((False,("%%s%%0%dd"%idx)%(base,max),0,ext,0,0,objsize,fileblk,0))
							else:	elems.append((False,("%%s%%0%dd"%idx)%(base,max),0,ext,0,0,objsize,0))
						else:
							if BLKsize:	elems.append((True,base,idx,ext,min,max,objsize,fileblk,missing))
							else:	elems.append((True,base,idx,ext,min,max,objsize,missing))
		elif os.path.isdir(LL):
			dircount += 1
			if len(LL)<70:	shortLL=LL
			else:	shortLL="%s<...>%s"%(LL[:31],LL[-32:])
			print ("\rIndexing %s\r"%shortLL).ljust(78," "),
			if recurse:
				token = listfileseq(LL,recurse,BLKsize,include_exts,exclude_dirs)
				filecount += token[0][1]
				dircount += token[0][2]
				totsize += token[0][3]
				if BLKsize:	totBLKsize += token[0][4]
				if LL.endswith(dirsep):	last_dir_path = os.path.split(LL.rstrip(dirsep))[-1]
				else:	last_dir_path = os.path.split(LL)[-1]
				if exclude_dirs==[] or (exclude_dirs!=[] and (last_dir_path not in exclude_dirs)):
					elems.extend(token)
					token = []
	if recurse:
		if BLKsize:	elems[0]=[basepath,filecount,dircount,totsize,totBLKsize]
		else:	elems[0]=[basepath,filecount,dircount,totsize]
		elems.append("..")
	print '\r                                                                              \r',
	return elems


def syntax():
	print "   Syntax:  fac-index [-m|F|S|b] [#code] [-o=output_dir] [path1 [path2 [... [pathN]]]]\n"
	print "             path?   Root path(s) to index for"
	print "             #code   Facility/Tape number  (on multiple paths it's asked for)"
	print "                -m   Sends index(es) by email"
	print "                -F   Does NOT write index(es) on file(s)"
	print "                -S   Uses SI prefixes for data sizes (MB, GB, ...)"
	print "                -b   Uses binary prefixes for data sizes (MiB, GiB, ...; default)"
	print "     -o=output_dir   Saves disk indexes into output_path (current by default)\n"
	sys.exit(1)


curdir = os.getcwd()
print "fac-index %s - CXFS Index generator for Technicolor digital facilities"%VERSION
print "Copyright (C) 2009 Walter Arrighetti, Ph.D."
print "All Rights Reserved.\n"

if not DATA['path']['local']:	outpath = os.getcwd()
elif os.path.isdir(DATA['path']['local']):	outpath = os.path.abspath(DATA['path']['local'])
else:
	print "ERROR!: Path \"%s\" does not seem to exist as primary target to this index."%os.path.abspath(DATA['path']['local'])
	sys.exit(9)
if not DATA['path']['remote']:	remotepath = None
elif os.path.isdir(DATA['path']['remote']):	remotepath = os.path.abspath(DATA['path']['remote'])
else:
	print "ERROR!: Path \"%s\" does not seem to exist as secondary target to this index."%os.path.abspath(DATA['path']['remote'])
	sys.exit(9)


tmpstring = Facility = ''

if len(sys.argv)>1:
	for arg in sys.argv[1:]:
		if arg=="-S":	SI=True
		elif arg=="-b":	SI=False
		elif arg=="-m":	sendmail=True
		elif arg=="-F":	writetxt=False
		elif arg.startswith("-o=") and len(arg)>3:
			if not os.path.isdir(os.path.abspath(arg[3:])):
				print "ERROR!: Specified path with '-o' does not exist!\n"
			else:
				outpath = os.path.abspath(arg[3:])
				print "  Text and HTML disk indexes output in %s\n"%outpath
		elif arg.startswith('#') and len(arg)>2:	Facility=arg[1:]
		elif os.path.isdir(arg):
			CXFSpaths.append(os.path.abspath(arg))
		else:	syntax()
else:	syntax()
if CXFSpaths==[]:	syntax()

if len(CXFSpaths)>1 and Facility!='':
	print "    Facility # cannot be specified for more than one to-index paths !"
	syntax()

if sendmail:
	if os.environ['USERNAME'] in DATA['authorized'].keys():	sendable=True
	else:	print "WARNING!:  User %s has no configured email management rights."%os.environ['USERNAME']
	try:
		maill = open(os.path.join(mailing_list_path,"fac-index_mailing_list.txt"),"r")
		mailing_list = maill.readlines()
		maill.close()
	except:	print "WARNING!: Invalid recipients' mailing list in %s. Using default addresses instead."%os.path.join(mailing_list_path,"fac-index_mailing_list.txt")


	
for path in CXFSpaths:
	basepath=os.path.abspath(path)
	basepathlvl=treelvl=string.count(basepath,dirsep)-1
	emptydir=False
	outx=[]
	if os.path.exists(basepath):
		if len(CXFSpaths)>1:	Facility=''
		if Facility=='':	Facility=str(raw_input("ENTER FACILITY/TAPE NUMBER: "))
		for c in range(0,len(Facility)):
			if Facility[c] in " \t\n\r":	Facility[c] = '_'
			elif Facility[c] not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_+-*/\\.=,:;()[]'\"!&^":	Facility[c] = '-'
		outfname = os.path.join(outpath,("facility_%s.txt"%Facility))
		if remotepath:	CXFSfname = os.path.join(remotepath,("facility_%s.txt"%Facility))
		outf = []
		if Windows and Win32API:
			try:
				FS_sectors_cluster, FS_bytes_sector, FS_free_clusters, FS_total_clusters = win32file.GetDiskFreeSpace(basepath)
				TotalSize = FS_total_clusters * FS_sectors_cluster * FS_bytes_sector
				FreeSize = FS_free_clusters * FS_sectors_cluster * FS_bytes_sector
				sizeok = True
			except:	sizeok = False
		elif not Windows:
			try:
				FSinfo = os.statvfs(basepath)
				FS_preferred_block_size,FS_fundamental_block_size,FS_total_blocks,FS_free_blocks,FS_available_blocks,FS_total_inodes,FS_free_inodes,FS_available_inodes,FS_max_file_len = FSinfo[statvfs.F_BSIZE],FSinfo[statvfs.F_FRSIZE],FSinfo[statvfs.F_BLOCKS],FSinfo[statvfs.F_BFREE],FSinfo[statvfs.F_BAVAIL],FSinfo[statvfs.F_FILES],FSinfo[statvfs.F_FREE],FSinfo[statvfs.F_FFREE],FSinfo[statvfs.F_FAVAIL],FSinfo[statvfs.F_NAMEMAX]
				TotalSize = FS_total_blocks * FS_fundamental_block_size
				FreeSize = FS_available_blocks * FS_fundamental_block_size
				sizeok = True
			except:	sizeok = False
		if sizeok:	freespaceondevice=int(100*(float(FreeSize)/TotalSize))
		
		tree=listfileseq(os.path.abspath(path), True, 0, [], CXFS_exclude_dirs)
		root=tree[0][0]
		prevlvl=treelvl=string.count(root,dirsep)-1
		if 'USERNAME' in os.environ.keys():	UserName = os.environ['USERNAME']
		elif 'USER' in os.environ.keys():	UserName = os.environ['USER']
		else:	UserName = '**unknown**'

		tmpstring = '\t<----------------------------------------------------------->'
		tmpstring += '\n\t          fac-index: Disk Index quick report sheet           '
		tmpstring += '\n\t<----------------------------------------------------------->'
		tmpstring += '\n\t            Volume full Path:   %s'%path
		tmpstring += '\n\t         TDI Facility/Tape #:   %s'%Facility
		if sizeok:	tmpstring += '\n\t           Volume Total Size:   %sB'%sizeprint(TotalSize,SI)
		tmpstring += '\n\t        Used Filesystem Size:   %sB'%sizeprint(tree[0][3],SI)
		tmpstring += '\n\t      Filesystem Cardinality:   %d files, %d folders'%(tree[0][1],tree[0][2])
		if sizeok:	tmpstring += '\n\t            Volume Free Size:   %sB  (%d%%)'%(sizeprint(FreeSize,SI),freespaceondevice)
		tmpstring+='\n\n\t         Index creation date:   %s'%time.strftime("%a, %d %b %Y, %H:%M")
		tmpstring += '\n\t      Facility name/location:   %s'%DATA['Location']
		tmpstring += '\n\t         Host creating index:   %s'%HostName
		tmpstring += '\n\t         User creating index:   %s'%UserName
		tmpstring += '\n\t<----------------------------------------------------------->\n'
		print '\r'+tmpstring
		outx.append(tmpstring+'\n')

		for obj in tree[1:]:
			prevlvl=treelvl
			if obj=="..":								# End of a folder
				if not emptydir:
					outx.append('%s           \\----->\n'%('           |'*(treelvl-1)))
				else:	emptydir=False
				treelvl -= 1
			elif len(obj)==3 and obj[0]=="!":			# Unreadable filesystem object
				tmpstring = '           |'*prevlvl
				if obj[1]:								# Unaccessible folder
					tmpstring += '   *FileErr*'
					treelvl -= 1
				else:	tmpstring += '    [DIRerr]'		# Unreadable file
				tmpstring += '  %s\n'%obj[2]
				outx.append(tmpstring)
			elif len(obj)==4:							# Beginning of a folder
				root,files = obj[0],obj[1]
				treelvl=string.count(root,dirsep)-basepathlvl
				if treelvl >= prevlvl and root!=".":
					tmpstring = '           |'*(prevlvl-1)
					if files==0 and obj[2]==0:
						tmpstring += '  [emptyDIR]'
						emptydir=True
					else:
						emptydir=False
						tmpstring += ('[%sB]'%sizeprint(obj[3],SI)).rjust(12,' ')
					tmpstring += '  %s'%(string.split(root,dirsep)[-1])
					if files or obj[2]:
						tmpstring += '   (%d files, %d dirs)'%(files, obj[2])
					tmpstring += '\n'
					outx.append(tmpstring)
			else:
				fstr = '           |'*(treelvl-1)
				if obj[0]:						# File sequence
					fstr += ('SEQ %sB'%sizeprint(obj[6],SI)).rjust(12,' ')
					fstr += '  %s{%%%02d}%s   [%d-%d]'%(obj[1],obj[2],obj[3],obj[4],obj[5])
					if obj[7]>0:	fstr+= ', miss=%d'%obj[7]
				else:							# Single file
					fstr += ('%sB'%sizeprint(obj[6],SI)).rjust(12,' ')
					fstr += '  %s%s'%(obj[1], obj[3])
				fstr += '\n'
				outx.append(fstr)
		
		if treelvl>2:
			for clos in range(1,treelvl-2):	outx.append('%s     \\----->\n'%('           |'*(treelvl-2)))
		
		if writetxt:
			print "Saving Fac-Index text file " + outfname,
			try:
				outf = open(outfname,"w")
				outf.writelines(outx)
				outf.close()
				atleastone = True
			except:	print "  [ ERROR! ]"
			else:	print "  [   OK   ]"

		if remotepath:
			print "Saving Fac-Index backup copy " + CXFSfname,
			try:
				outf = open(CXFSfname,"w")
				outf.writelines(outx)
				outf.close()
				atleastone = True
			except:	print "  [ ERROR! ]"
			else:	print "  [   OK   ]"

		if sendmail and sendable:
			mailsent = False
			print ("Emailing Fac-Index for " + path).ljust(66," "),
			if os.environ['USERNAME'] in DATA['authorized'].keys():
				FromAddress = DATA['authorized'][os.environ['USERNAME']]
			else:	FromAddress = DATA['email source']
			mail_header = "From: %s\nTo: %s\nDate: %s\nSubject: Facility #%s index\n"%(FromAddress,(("%s, "*len(mailing_list))%tuple(mailing_list))[:-2],time.ctime(time.time()),Facility)
			mail_out = mail_header + ''.join(outx)
			try:
				if DATA['SMTP']['SSL?']:
					if DATA['SMTP']['port'] and DATA['SMTP']['port'].isdigit():
						mail = smtplib.SMTP_SSL(DATA['SMTP']['server'],DATA['SMTP']['port'])
					else:	mail = smtplib.SMTP_SSL(DATA['SMTP']['server'])
				else:
					if DATA['SMTP']['port'] and DATA['SMTP']['port'].isdigit():
						mail = smtplib.SMTP(DATA['SMTP']['server'],DATA['SMTP']['port'])
					else:	mail = smtplib.SMTP(DATA['SMTP']['server'])
				if DATA['SMTP']['username']:
					mail.login(DATA['SMTP']['username'],DATA['SMTP']['password'])
			#	mail.set_debuglevel(1)
				mail_outcome = mail.sendmail(FromAddress, mailing_list, mail_out)
				mail.quit()
				if mail_outcome:	raise BaseException
			except:	print "  [ ERROR! ]"
			else:
				print "  [   OK   ]"
				mailsent=atleastone=True
	else:
		print "No " + path + " exist(s): no disk indexes created."
sys.exit(0)
