A simple mass fuzzer scan written is python.

Can define default values directly in the program or use the command line arguments below to edit them.
Command line arguments :
```
-v, --version : Show version, then exit the program.

-h, --help : Show the help screen then exit the program.

-e, --extensions <filetype> : extension to append to searched files instead of using the default one, need to add file search to be used.
e.g : fuzz.py -f -e html,pdf

-w, --wordlist <path to file> : to use a wordlist.
e.g : fuzz.py -w wordlist.txt

-u, --url <hostname> : to define the hostname.

-f, --file-search : to do a file scan

-ss, --string-search <strings>: search for a string in every file scanned, need file search to work. It also put every files and strings to search to lowercase.
e.g : fuzz.py -f -s password,user,secret

-i, --ignore <status code> : to ignore specific status code, 404 is activated by default to avoid infinite looping.

-b, --blacklist <strings> : not implemented, avoid blacklisted directory name.

-l, --logging : activate the logging system, log the current scan in a file .log with the date and hour of the scan.

-p, --pause : Slow down the packet sending rate by adding a waiting time, in milliseconds. So 1000 is 1 second

-d, --download : not implemented, write every file scanned to the local host.

-pl, --page-length : Set minimum page length

-m, --method : Use another HTTP method

```

Command line example : 

```
python .\PyFuzzer.py -w ..\..\wordlist.txt -u localhost:8000/foldertree_test/fuzz -f -ss secret,password -p 500 -l -e txt,html
```

Next stuff to implements :

- Blacklisting, to avoid some directory names
- Download, download every files scanned
