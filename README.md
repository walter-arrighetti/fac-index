# fac-index
Generates an ASCII text file reporting basic information on a filesystem path and its contents (which is the only mandatory argument to the tool), after scanning its metadata.
Such information include:
* Basic filesystem data: full path, free/used size, numer of files and folders
* Identity of the username and host the tool was launched from (and time of the scan)
* Graphical representation (with ASCII characters) of the sub-directory structure
* Partial size of each subdirectory and of each file in it

File sequences (e.g. `file001.ext`, `file002.ext`, ..., `file999.ext`) are acknowledged and reported as single items (1 line); their total size is only reported, plus placeholder for their numerical order. Missing file number(s) in a contiguous sequence are also reported.

The file is generated, by default, in the current folder, and named `facility_`_`FACILITYNAME`_`.txt`, where _`FACILITYNAME`_ is the tape/disk/volume/faciluty number asked for input at the beginning.
A primary and an optional secondary path to store such ASCII text files can be specified as well (secondary path can usually be the path to a remote-share that acts as a vault).

Optionally, the same index can be sent via email to predetermined recipient(s). Optional authentication to an SMTP server is available (with or without SSL).

The script is flexible to any organization's data-management and security policies. All its customization can be done by editing the (commented) values in the script's `DATA` Python-language dictionary, without affecting the original funcitonalities.
Customizable items are, for example, default primary/secondary paths, email information (SMTP hostname, email recipients, etc.).

Besides, the script only accesses standard POSIX metadata within the specified path; it does *not* require read access to files. For this reason it can be run from within secure environments with restricted access to sensible storage. These scanarios may include but not limited to:
* segregated mounts of a Storage Area Network (SAN) with access to file metadata only,
* LTO tapes written in LTFS (only requires read-access to the LTFS' index partition)
* NFS or SMB/CIFS shares with poor sequential-packets' I/O data-rates

Running the script without arguments further exposes additional syntax.

A sample ASCII output of this tool is the following:

```
	<----------------------------------------------------------->
	          fac-index: Disk Index quick report sheet           
	<----------------------------------------------------------->
	            Volume full Path:   /san/fs01
	         TDI Facility/Tape #:   TEST-VOLUME
	        Used Filesystem Size:   615.21GiB
	      Filesystem Cardinality:   38925 files, 1101 folders

	         Index creation date:   Fri, 04 Nov 2016, 01:55
	      Facility name/location:   ColorScience Lab
	         Host creating index:   cslabvmtest04
	         User creating index:   walter-arrighetti
	<----------------------------------------------------------->

  [73.57GiB]  ALEXA_ARRIRAW   (10053 files, 168 dirs)
           |   [4.19GiB]  3Dtest_montarsi__R001R1LZ   (643 files, 8 dirs)
           |           |  [333.9MiB]  001-C001L   (50 files, 0 dirs)
           |           |           |SEQ 333.9MiB  001-C001L.{%07}.ari   [36090-36139]
           |           |           |           \----->
           |           |  [888.2MiB]  001-C002L   (133 files, 0 dirs)
           |           |           |SEQ 888.2MiB  001-C002L.{%07}.ari   [62240-64951], miss=2579
           |           |           |           \----->
           |           |  [888.2MiB]  001-C002R   (133 files, 0 dirs)
           |           |           |SEQ 888.2MiB  001-C002R.{%07}.ari   [62240-64951], miss=2579
           |           |           |           \----->
           |           |  [460.8MiB]  001-C004L   (69 files, 0 dirs)
           |           |           |SEQ 460.8MiB  001-C004L.{%07}.ari   [68030-68098]
           |           |           |           \----->
           |           |           \----->
           |  [360.1MiB]  provini_DPX   (810 files, 1 dirs)
           |           |  [360.1MiB]  2048x1152   (810 files, 0 dirs)
           |           |           | SEQ 18.0MiB  A001_C001_0713MU.{%07}.dpx   [0-99]
           |           |           | SEQ 18.0MiB  A001_C002_0713RQ.{%07}.dpx   [0-99], miss=50
           |           |           | SEQ 18.0MiB  A001_C004_0713Y3.{%07}.dpx   [0-99]
           |           |           | SEQ 18.0MiB  A001_C005_07130P.{%07}.dpx   [0-99]
           |           |           | SEQ 18.0MiB  A001_C006_0713NG.{%07}.dpx   [0-99]
           |           |           | SEQ 18.0MiB  B001_C003_0713IV.{%07}.dpx   [0-99], miss=20
           |           |           | SEQ 18.0MiB  B001_C004_071326.{%07}.dpx   [0-99], miss=20
           |           |           | SEQ 18.0MiB  B001_C005_071309.{%07}.dpx   [0-99]
           |           |           | SEQ 18.0MiB  B001_C006_0713SK.{%07}.dpx   [0-99]
           |           |           |           \----->
           |           |           \----->
           |     2.46GiB  A001_C002_0605CF_001.R3D
           |     3.08GiB  A001_C006_0214GJ_001.R3D
           |          8B  digital_magazine.bin
           |          4B  digital_magdynamic.bin
           |           \----->
    254.4MiB  A001_C003_0603I3_001.R3D
      7.9MiB  A001C007_110309_L263_0285.dpx
    314.9MiB  A002_C005_0622RB_003.R3D
      7.9MiB  A002C002_110309_L263_0118.dpx
    970.7MiB  A007C008_110324_R1M5.mov
     12.2MiB  ALEXA vs 35mm Tests.dpx
           \----->
```
