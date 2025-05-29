import requests 
import sys 
import datetime
import time 
import logging 

# Useful functions

def load_wordlist(_filename : str) -> list : 
	with open(_filename, "r") as f:
			loaded_wordlist = f.readlines()
	return loaded_wordlist

def clean_word(_word : str) -> str : 
	# Sanitize word to be used
	try:
		return _word.decode(encoding="utf-8", errors='ignore').strip()
	except AttributeError:
		return _word.strip()

def errors_handler(_error) : 
	print(_error)
	exit(-1)

def join_str_list(_str_list) : 
	a = ""
	for i in _str_list : 
		a += clean_word(i) + "/"
	return a

def new_url_name(_url, _path) : 
	return _url.replace("fuzz", join_str_list(_path)) + "fuzz"

def create_path(_path_list : list, _url : str) -> list : 
	curr_path = ""
	for i in _path_list : 
		curr_path += i + "/"

	curr_path += "fuzz"

	return _url.replace("fuzz", curr_path)

#-----

def version_screen() :
	print("\t0.1 smth\n")
	exit(0)

def initial_screen() : 
	screen = f'''
                                                                  
	@@@@@@@   @@@ @@@  @@@@@@@@  @@@  @@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@   
	@@@@@@@@  @@@ @@@  @@@@@@@@  @@@  @@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  
	@@!  @@@  @@! !@@  @@!       @@!  @@@       @@!       @@!  @@!       @@!  @@@  
	!@!  @!@  !@! @!!  !@!       !@!  @!@      !@!       !@!   !@!       !@!  @!@  
	@!@@!@!    !@!@!   @!!!:!    @!@  !@!     @!!       @!!    @!!!:!    @!@!!@!   
	!!@!!!      @!!!   !!!!!:    !@!  !!!    !!!       !!!     !!!!!:    !!@!@!    
	!!:         !!:    !!:       !!:  !!!   !!:       !!:      !!:       !!: :!!   
	:!:         :!:    :!:       :!:  !:!  :!:       :!:       :!:       :!:  !:!  
	 ::          ::     ::       ::::: ::   :: ::::   :: ::::   :: ::::  ::   :::  
	 :           :      :         : :  :   : :: : :  : :: : :  : :: ::    :   : :

	I DID IT BECAUSE I CAN.

	'''

	print(screen)

def help_screen() -> None: 
	help = f''' 
	+{"-" * 15}|HELP SCREEN|{"-" * 15}+
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

	 '''
	print(help)
	exit(0)

def args_parser(_argv, _arguments_dict) -> dict : 

	arguments = _arguments_dict

	for index, value in enumerate(_argv) : 
		match value:
			case "-v" | "--version":
				version_screen()

			case "-h" | "--help":
				help_screen()

			case "-w" | "--wordlist":
				arguments["wordlist"] = _argv[index + 1]

			case "-u" | "--url":
				arguments["url"] = _argv[index + 1]

			case "-f" | "--file-search":
				arguments["file_search"] = True

			case "-ss" | "--string-search":
				arguments["string_search"] = _argv[index + 1].split(",")

			case "-e" | "--extension":
				arguments["extension"] = _argv[index + 1].split(",")

			case "-i" | "--ignore":
				arguments["ignore_list"] = list(map(lambda x: int(x), _argv[index + 1].split(",")))
				arguments["ignore_list"].append(404)

			case "-b" | "--blacklist":
				arguments["blacklist"] = _argv[index + 1].split(",")

			case "-l" | "--logging": 
				arguments["logging"] = True

			case "-p" | "--pause":
				arguments["pause"] = int(_argv[index + 1])

			case "-m" | "--method":
				arguments["method"] = _argv[index + 1]

			case "-d" | "--download":
				arguments["download"] = True

			case "-pl" | "--page-length":
				arguments["page_length"] = int(_argv[index + 1])
			case _:
				pass

	return arguments
	
def send_request_and_get_status(_url, _argv) :
	
	try:
		if _argv["pause"] > 0 :
			time.sleep(_argv["pause"] / 1000)

		url = _url if _url.find("http") == 0 else "http://" + _url
		request_result = requests.request(_argv["method"], url=url)

		result = f"\t[!] - [{request_result.status_code}] [Pg Len] = {len(request_result.text)} | {url} "

		if request_result.status_code not in _argv["ignore_list"] and len(request_result.text) >= _argv["page_length"]:
			if len(_argv["string_search"]) > 0 :
				for string in _argv["string_search"] : 
					if request_result.text.lower().find(string.lower()) != -1:
						result += "| found '" + string + "' "
						
			print(result)

			if not (_argv["logger"] is None) : 
				_argv["logger"].info(result)

	except KeyboardInterrupt :
		print("\t[X] - Interruped, EXITING...")
		exit()


	return request_result.status_code

def recursive_fuzzer(_argv, _path_list):

	path_list = _path_list
	file_search = _argv["file_search"]

	try :
		for word in _argv["loaded_wordlist"] : 
			new_url = new_url_name(_argv["url"], path_list)

			if file_search : 
				extension_fuzzer(
					_url 	= new_url, 
					_argv	= _argv
				)
				file_search 		= False

			new_url = new_url.replace("fuzz", clean_word(word))
			status = send_request_and_get_status(
				_url 	= new_url,
				_argv	= _argv
			)
			
			# CAREFUL : Can go into an infinite loop if the ignore list is badly defined.
			if status not in _argv["ignore_list"] : 
				# Append newfound folder to pathlist.
				path_list.append(word)
				recursive_fuzzer(
					_argv = _argv, 
					_path_list = path_list
				)

		try:
			path_list.pop()
		except IndexError : 
			pass
	except KeyboardInterrupt : 
		print("\t[X] - Interruped, EXITING...")
		exit()

def extension_fuzzer(_url, _argv):

	try:
		for word in _argv["loaded_wordlist"] : 
			url = _url.replace("fuzz", clean_word(word))
			req_list = list(map(lambda ex : send_request_and_get_status(
				_url 	= url + '.' + ex, 
				_argv	= _argv
				), _argv["extension"]))

	except KeyboardInterrupt:
		print("\t[X] - Interruped, EXITING...")
		exit()

def load_ressources(_argv) :
	
	argv = _argv

	try :

		# Check for problems
		if argv["url"].lower().find("fuzz") == -1:
			raise Exception("URL contain no 'fuzz' landmark, aborting...")

		argv["loaded_wordlist"] = load_wordlist(argv["wordlist"])

		if argv["logging"] : 
			logger = logging.getLogger(__name__)
			logger.setLevel(logging.INFO)

			handler = logging.FileHandler(f"pyfuzzer.log", mode='a')
			formatter = logging.Formatter("%(asctime)s %(message)s")

			handler.setFormatter(formatter)
			logger.addHandler(handler )

			argv["logger"] = logger

		recursive_fuzzer(_argv = argv, _path_list = [])
			
	except IOError as e: 
		errors_handler(e)

def main():
	initial_screen()

	#DEFAULT CONSTANT
	CURRENT_VERSION			= "0.1 smth"
	DEFAULT_URL 			= "localhost:8000/foldertree_test/fuzz"
	DEFAULT_WORDLIST 		= "./wordlist.txt"
	DEFAULT_FILE_SEARCH   	= False
	DEFAULT_STRING_SEARCH 	= ["password", "user"]
	DEFAULT_EXTENSION 		= ["html", "pdf", "txt", "php"]
	DEFAULT_IGNORE 			= [404, 501]
	DEFAULT_LOGGING 		= False
	DEFAULT_BLACKLIST 		= []
	DEFAULT_PAUSE 			= 0
	DEFAULT_DOWNLOAD 		= False
	DEFAULT_METHOD			= "GET"
	DEFAULT_PAGE_LENGTH		= 0
	
	#GATHER ARGUMENTS
	arguments = {
		"url" 				: None,
		"wordlist" 			: None,
		"file_search" 		: None,
		"string_search" 	: None,
		"extension" 		: None,
		"logging" 			: None,
		"ignore_list" 		: None,
		"blacklist" 		: None, 
		"pause" 			: None,
		"download"			: None,
		"method" 			: None,
		"page_length"		: None, 
		"logger"			: None,
		"loaded_wordlist"	: None,
	}

	if len(sys.argv) > 1 :
		arguments = args_parser(sys.argv, arguments)

	#ASSIGN DICT VALUES
	arguments['url'] 			= DEFAULT_URL if arguments["url"] is None else arguments["url"]
	arguments["wordlist"] 		= DEFAULT_WORDLIST if arguments["wordlist"] is None else arguments["wordlist"]
	arguments["file_search"] 	= DEFAULT_FILE_SEARCH if arguments["file_search"] is None else arguments["file_search"]
	arguments["string_search"] 	= DEFAULT_STRING_SEARCH if arguments["string_search"] is None else arguments["string_search"]
	arguments["extension"] 		= DEFAULT_EXTENSION if arguments["extension"] is None else arguments["extension"]
	arguments["ignore_list"] 	= DEFAULT_IGNORE if arguments["ignore_list"] is None else arguments["ignore_list"]
	arguments["logging"] 		= DEFAULT_LOGGING if arguments["logging"] is None else arguments["logging"]
	arguments["blacklist"] 		= DEFAULT_BLACKLIST if arguments["blacklist"] is None else arguments["blacklist"] # Not implemented
	arguments["pause"] 			= DEFAULT_PAUSE if arguments["pause"] is None else arguments["pause"] # Not implemented
	arguments["download"] 		= DEFAULT_DOWNLOAD if arguments["download"] is None else arguments["download"] # Not implemented
	arguments["method"]			= DEFAULT_METHOD if arguments["method"] is None else arguments["method"]
	arguments["page_length"] 	= DEFAULT_PAGE_LENGTH if arguments["page_length"] is None else arguments["page_length"]

	#LOAD EVERYTHING
	load_ressources(
	_argv = arguments
	)

	print()

if __name__ == "__main__":
	main()