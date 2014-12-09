import sys

class HeapProfileParser(object):
	def __init__(self):
		self.resetData()

	def resetData(self):
		self.header = None
		self.addressInfo = []
		self.libInfo = []

	def parseAddressLine(self, line):
		# line = "liveCount: liveBytes [ sumCount: sumBytes] @ addr1 addr2 ... addrN"
		# return ((liveCount, liveBytes, sumCount, sumBytes), [addrN, ..., addr2, addr1])
		tmp = line.split('@')
		countStr = tmp[0].replace('[', ':').replace(']', ':')
		countTmp = countStr.split(':')
		countInfo = (int(countTmp[0]), int(countTmp[1]), int(countTmp[2]), int(countTmp[3]))
		stackInfo = tmp[1].strip().split(' ')
		stackInfo = [int(a, 16) for a in stackInfo]
		return (countInfo, stackInfo)

	def parseLibLine(self, line):
		# line = "766f0000-76800000 r-xp 00000000 00:00 0           C:\Windows\syswow64\kernel32.dll"
		# return ("C:\Windows\syswow64\kernel32.dll", begin, end)
		tmp  = line.split()
		addr = tmp[0].split('-')
		return (tmp[-1], int(addr[0],16), int(addr[1],16))

	def parseIt(self, filename):
		self.resetData()
	
		beginLib = False	
		f = open(filename, 'r')
		for line in f.xreadlines():
			line = line.strip()

			if not line:
				continue

			if line[0] == '#':
				continue
			elif self.header is None:
				self.header = line
			elif line.startswith('MAPPED_LIBRARIES'):
				beginLib = True
			elif beginLib:
				self.libInfo.append(self.parseLibLine(line))
			else:
				self.addressInfo.append(self.parseAddressLine(line))
		f.close()

if __name__ == '__main__':
	parser = HeapProfileParser()
	parser.parseIt(sys.argv[1])

	print '==== LibInfo ===='
	for lib in parser.libInfo:
		print lib

	print '\n==== AddressInfo ===='
	for addr in parser.addressInfo:
		print addr

