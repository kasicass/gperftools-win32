import sys
import argparse
import DbgHelp
from ctypes import windll, WinError

WEBSYM = "SRV*c:\\symbols*http://msdl.microsoft.com/download/symbols"

if __name__ == '__main__':
	ap = argparse.ArgumentParser(description='addr2line-pdb python version')
	ap.add_argument('-f', '--functions', action='store_true', help='print function name')
	ap.add_argument('-C', '--demangle', action='store_true', help='print source:line')
	ap.add_argument('filename', help='filename to parse')
	args = ap.parse_args()

	symopts = DbgHelp.SYMOPT_DEFERRED_LOADS | DbgHelp.SYMOPT_DEBUG | DbgHelp.SYMOPT_LOAD_LINES
	if args.demangle:
		symopts |= DbgHelp.SYMOPT_UNDNAME

	hProcess = windll.kernel32.GetCurrentProcess()
	if not DbgHelp.SymInitialize(hProcess, None, False):
		raise WinError()
		sys.exit(1)

	searchPath = DbgHelp.SymGetSearchPath(hProcess)
	searchPath += (';' + WEBSYM)
	DbgHelp.SymSetSearchPath(hProcess, searchPath)
	
	DbgHelp.SymSetOptions(symopts)
	moduleBase = DbgHelp.SymLoadModuleEx(hProcess, args.filename)
	if not moduleBase:
		print 'SymLoadModuleEx failed:', args.filename
		sys.exit(1)

	print 'moduleBaseAddr: 0x%08x' % moduleBase
	while True:
		line = sys.stdin.readline()
		if not line:
			break

		line = line.strip()
		addr = int(line, 16)
		if args.functions:
			print DbgHelp.SymFromAddr(hProcess, addr)

		print DbgHelp.SymGetLineFromAddr64(hProcess, addr)

	DbgHelp.SymUnloadModule64(hProcess, moduleBase)
	DbgHelp.SymCleanup(hProcess)

