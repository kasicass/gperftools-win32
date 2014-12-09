import DbgHelp

WEBSYM = ";SRV*c:\\symbols*http://msdl.microsoft.com/download/symbols"

class HeapProfileAddressTable(object):
	def __init__(self, parser):
		self.parser   = parser
		self.addrDict = {} # { addr : ("func", "source:line"), }

	def buildTable(self):
		libDict = {} # { "C:\Windows\SysWOW64\ntdll.dll" : (begin, [addr1, addr2, ... ]) }
		for name, begin, end in self.parser.libInfo:
			libDict[name] = (begin, [])
			for _, addrList in self.parser.addressInfo:
				for addr in addrList:
					if begin <= addr < end:
						libDict[name][1].append(addr)

		hProcess = DbgHelp.GetCurrentProcess()
		DbgHelp.SymInitialize(hProcess, None, False)

		oldSearchPath = DbgHelp.SymGetSearchPath(hProcess)
		DbgHelp.SymSetSearchPath(hProcess, oldSearchPath + WEBSYM)
		DbgHelp.SymSetOptions(DbgHelp.SYMOPT_DEFERRED_LOADS | DbgHelp.SYMOPT_DEBUG | DbgHelp.SYMOPT_LOAD_LINES | DbgHelp.SYMOPT_UNDNAME)

		self.addrDict = {}
		for libName, (begin, addrList) in libDict.iteritems():
			moduleBase = DbgHelp.SymLoadModuleEx(hProcess, libName)
			if not moduleBase:
				# print 'SymLoadModuleEx(%s) failed' % libName
				continue

			for addr in addrList:
				realAddr     = addr - begin + moduleBase
				source, line = DbgHelp.SymGetLineFromAddr64(hProcess, realAddr)
				funcName     = DbgHelp.SymFromAddr(hProcess, realAddr)
				self.addrDict[addr] = (funcName, source, line)

			DbgHelp.SymUnloadModule64(hProcess, moduleBase)

		DbgHelp.SymCleanup(hProcess)

	def addr2name(self, addr):
		return self.addrDict[addr]

if __name__ == '__main__':
	import sys
	import HeapProfileParser

	parser = HeapProfileParser.HeapProfileParser()
	parser.parseIt(sys.argv[1])

	at = HeapProfileAddressTable(parser)
	at.buildTable()
	print parser.addressInfo[0][1]
	for addr in parser.addressInfo[0][1]:
		print at.addr2name(addr)

