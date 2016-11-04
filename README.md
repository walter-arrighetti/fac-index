# fac-index
Generates an ASCII text file reporting basic information on a filesystem path and its contents (which is the only mandatory argument to the tool), after scanning its metadata.
Such information include:
* Basic filesystem data: full path, free/used size, numer of files and folders
* Identity of the username and host the tool was launched from (and time of the scan)
* Graphical representation (with ASCII characters) of the sub-directory structure
* Partial size of each subdirectory and of each file in it
File sequences (e.g. file001.ext, file002.ext, ..., file999.ext) are acknowledged and reported as single items (1 line); their total size is only reported, plus placeholder for their numerical order. Missing file number(s) in a contiguous sequence are also reported.

The file is generated, by default, in the current folder, and named "facility_FACILITYNAME.txt", where FACILITYNAME is the tape/disk/volume/faciluty number asked for input at the beginning.
A primary and an optional secondary path to store such ASCII text files can be specified as well (secondary path can usually be the path to a remote-share that acts as a vault).

Optionally, the same index can be sent via email to predetermined recipient(s). Optional authentication to an SMTP server is available (with or without SSL).

The script is flexible to any organization's data-management and security policies. All its customization can be done by editing the (commented) values in the script's DATA dictionary (Python language), without affecting the original funcitonalities.
Customizable items are, for example, default primary/secondary paths, email information (SMTP hostname, email recipients, etc.).

Besides, the script only accesses standard POSIX metadata within the specified path; it does *not* require read access to files. For this reason it can be run from within secure environments with restricted access to sensible storage. These scanarios may include but not limited to:
* metadata-only segregated mounts of a Storage Area Network (SAN),
* LTO tapes written in LTFS (only requires read-access to the LTFS' index partition)
* NFS (or SMB/CIFS) shares with poor sequential-packets' data-rates

Running the script without arguments further exposes additional syntax.

