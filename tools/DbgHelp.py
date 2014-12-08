from ctypes import Structure, sizeof, byref
from ctypes import WINFUNCTYPE, WinError
from ctypes import cdll, windll
from ctypes import create_string_buffer
from ctypes import c_char, c_void_p, c_uint64
from ctypes import POINTER
from ctypes.wintypes import BOOL, HANDLE, LPCSTR, LPSTR, DWORD, ULONG

CHAR     = c_char
PVOID    = c_void_p
DWORD64  = c_uint64
ULONG64  = c_uint64
PDWORD   = POINTER(DWORD)
PDWORD64 = POINTER(DWORD64)

prototype = WINFUNCTYPE(BOOL, HANDLE, LPCSTR, BOOL)
paramflags = ((1, "hProcess"), (1, "UserSearchPath"), (1, "fInvadeProcess"))
SymInitialize = prototype(("SymInitialize", cdll.DbgHelp), paramflags)

prototype = WINFUNCTYPE(BOOL, HANDLE)
paramflags = ((1, "hProcess"),)
SymCleanup = prototype(("SymCleanup", cdll.DbgHelp), paramflags)

prototype = WINFUNCTYPE(BOOL, HANDLE, LPSTR, DWORD)
paramflags = ((1, "hProcess"), (1, "SearchPath"), (1, "SearchPathLength"))
SymGetSearchPath_ = prototype(("SymGetSearchPath", cdll.DbgHelp), paramflags)
def SymGetSearchPath_errcheck(result, func, args):
	if not result:
		raise WinError()
	return args[1].value
SymGetSearchPath_.errcheck = SymGetSearchPath_errcheck
def SymGetSearchPath(hProcess):
	s = create_string_buffer(256)
	return SymGetSearchPath_(hProcess, s, 256)

prototype = WINFUNCTYPE(BOOL, HANDLE, LPCSTR)
paramflags = ((1, "hProcess"), (1, "SearchPath"))
SymSetSearchPath = prototype(("SymSetSearchPath", cdll.DbgHelp), paramflags)


SYMOPT_CASE_INSENSITIVE          = 0x00000001
SYMOPT_UNDNAME                   = 0x00000002
SYMOPT_DEFERRED_LOADS            = 0x00000004
SYMOPT_NO_CPP                    = 0x00000008
SYMOPT_LOAD_LINES                = 0x00000010
SYMOPT_OMAP_FIND_NEAREST         = 0x00000020
SYMOPT_LOAD_ANYTHING             = 0x00000040
SYMOPT_IGNORE_CVREC              = 0x00000080
SYMOPT_NO_UNQUALIFIED_LOADS      = 0x00000100
SYMOPT_FAIL_CRITICAL_ERRORS      = 0x00000200
SYMOPT_EXACT_SYMBOLS             = 0x00000400
SYMOPT_ALLOW_ABSOLUTE_SYMBOLS    = 0x00000800
SYMOPT_IGNORE_NT_SYMPATH         = 0x00001000
SYMOPT_INCLUDE_32BIT_MODULES     = 0x00002000
SYMOPT_PUBLICS_ONLY              = 0x00004000
SYMOPT_NO_PUBLICS                = 0x00008000
SYMOPT_AUTO_PUBLICS              = 0x00010000
SYMOPT_NO_IMAGE_SEARCH           = 0x00020000
SYMOPT_SECURE                    = 0x00040000
SYMOPT_NO_PROMPTS                = 0x00080000
SYMOPT_OVERWRITE                 = 0x00100000
SYMOPT_IGNORE_IMAGEDIR           = 0x00200000
SYMOPT_FLAT_DIRECTORY            = 0x00400000
SYMOPT_FAVOR_COMPRESSED          = 0x00800000
SYMOPT_ALLOW_ZERO_ADDRESS        = 0x01000000
SYMOPT_DISABLE_SYMSRV_AUTODETECT = 0x02000000
SYMOPT_READONLY_CACHE            = 0x04000000
SYMOPT_SYMPATH_LAST              = 0x08000000
SYMOPT_DEBUG                     = 0x80000000

prototype = WINFUNCTYPE(DWORD)
SymGetOptions = prototype(("SymGetOptions", cdll.DbgHelp))

prototype = WINFUNCTYPE(DWORD, DWORD)
paramflags = ((1, "SymOptions"), )
SymSetOptions = prototype(("SymSetOptions", cdll.DbgHelp), paramflags)


class IMAGEHLP_LINE64(Structure):
	_fields_ = [
		("SizeOfStruct", DWORD),
		("Key", PVOID),
		("LineNumber", DWORD),
		("FileName", LPSTR),
		("Address", DWORD64)
	]
PIMAGEHLP_LINE64 = POINTER(IMAGEHLP_LINE64)

prototype = WINFUNCTYPE(BOOL, HANDLE, DWORD64, PDWORD, PIMAGEHLP_LINE64)
paramflags = ((1, "hProcess"), (1, "dwAddr"), (1, "pdwDisplacement"), (1, "Line"))
SymGetLineFromAddr64_ = prototype(("SymGetLineFromAddr64", cdll.DbgHelp), paramflags)
def SymGetLineFromAddr64(hProcess, dwAddr):
	line = IMAGEHLP_LINE64()
	line.SizeOfStruct = sizeof(line)
	dummy = DWORD()
	if SymGetLineFromAddr64_(hProcess, dwAddr, byref(dummy), byref(line)):
		return line.FileName, line.LineNumber
	else:
		return "??", 0


class MODLOAD_DATA(Structure):
	_fields_ = [
		("ssize", DWORD),
		("ssig", DWORD),
		("data", PVOID),
		("size", DWORD),
		("flags", DWORD)
	]
PMODLOAD_DATA = POINTER(MODLOAD_DATA)

prototype = WINFUNCTYPE(DWORD64, HANDLE, HANDLE, LPSTR, LPSTR, DWORD64, DWORD, PMODLOAD_DATA, DWORD)
paramflags = ((1, "hProcess"), (1, "hFile"), (1, "ImageName"), (1, "ModuleName"),
	(1, "BaseOfDll"), (1, "DllSize"), (1, "Data"), (1, "Flags"))
SymLoadModuleEx = prototype(("SymLoadModuleEx", cdll.DbgHelp), paramflags)
def SymLoadModuleEx_errcheck(result, func, args):
	if not result:
		raise WinError()
	return result
SymLoadModuleEx.errcheck = SymLoadModuleEx_errcheck


MAX_SYM_NAME = 2000
class SYMBOL_INFO(Structure):
	_fields_ = [
		("SizeOfStruct", ULONG),
		("TypeIndex", ULONG),
		("Reserved", ULONG64*2),
		("Index", ULONG),
		("Size", ULONG),
		("ModBase", ULONG64),
		("Flags", ULONG),
		("Value", ULONG64),
		("Address", ULONG64),
		("Register", ULONG),
		("Scope", ULONG),
		("Tag", ULONG),
		("NameLen", ULONG),
		("MaxNameLen", ULONG),
		("Name", CHAR*MAX_SYM_NAME),  # http://msdn.microsoft.com/en-us/library/windows/desktop/ms681323(v=vs.85).aspx
	]
PSYMBOL_INFO = POINTER(SYMBOL_INFO)

prototype = WINFUNCTYPE(BOOL, HANDLE, DWORD64, PDWORD64, PSYMBOL_INFO)
paramflags = ((1, "hProcess"), (1, "Address"), (1, "Displacement"), (1, "Symbol"))
SymFromAddr_ = prototype(("SymFromAddr", cdll.DbgHelp), paramflags)
def SymFromAddr(hProcess, Address):
	symbol = SYMBOL_INFO()
	symbol.SizeOfStruct = sizeof(symbol) - MAX_SYM_NAME # hack
	symbol.MaxNameLen = MAX_SYM_NAME
	dummy = ULONG64()
	if not SymFromAddr_(hProcess, Address, byref(dummy), byref(symbol)):
		return "??"
	else:
		return str(symbol.Name)

if __name__ == '__main__':
	hProcess = -1
	print 'SymInitialize', SymInitialize(hProcess, None, False)
	s = SymGetSearchPath(hProcess)
	print 'SymSetSearchPath', SymSetSearchPath(hProcess, s + ";" + "SRV*c:\\websymbols*http://msdl.microsoft.com/download/symbols")
	print 'set opt 0x%08x' % SymSetOptions(SYMOPT_DEFERRED_LOADS | SYMOPT_DEBUG | SYMOPT_LOAD_LINES | SYMOPT_UNDNAME)
	moduleBase = SymLoadModuleEx(hProcess, None, r"D:\myprj\gperftools-win32\bin\Win32\Debug\libtcmalloc-static-test.exe",
		None, 0, 0, None, 0)
	print 'moduleBase: 0x%08x' % moduleBase
	print SymGetLineFromAddr64(hProcess, 0x003ba3da - 0x002e0000 + moduleBase)
	print SymGetLineFromAddr64(hProcess, 0x003682ea - 0x002e0000 + moduleBase)
	print SymFromAddr(hProcess, 0x003682ea - 0x002e0000 + moduleBase)
	print 'SymCleanup', SymCleanup(hProcess)

