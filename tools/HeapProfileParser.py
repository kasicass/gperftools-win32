import sys

class HeapProfileParser(object):
	def __init__(self):
		self.header = None
		self.addressToCounts = {}  # address : (liveCount, liveBytes, sumCount, sumBytes)
		self.addressTree = {}      # addr1 : {
		                           #   addr2 : {},
		                           #   addr3 : {
		                           #     addr4 : {},
		                           #     addr5 : {},
		                           #   },
		                           # }

	def parseAddressLine(self, line):
		# line = "liveCount: liveBytes [ sumCount: sumBytes] @ addr1 addr2 ... addrN"
		# return ((liveCount, liveBytes, sumCount, sumBytes), [addrN, ..., addr2, addr1])
		tmp = line.split('@')
		countStr = tmp[0].replace('[', ':').replace(']', ':')
		countTmp = countStr.split(':')
		countInfo = (int(countTmp[0]), int(countTmp[1]), int(countTmp[2]), int(countTmp[3]))
		stackInfo = tmp[1].strip().split(' ')
		return (countInfo, stackInfo)

	def parseIt(self, filename):
		addressInfo = []
		
		f = open(filename, 'r')
		for line in f.xreadlines():
			line = line.strip()

			if not line:
				continue

			if self.header is None:
				self.header = line
			elif line.startswith('MAPPED_LIBRARIES'):
				break
			else:
				addressInfo.append(self.parseAddressLine(line))
		f.close()

		# build addressToCounts
		for countInfo, stackInfo in addressInfo:
			for addr in stackInfo:
				if self.addressToCounts.has_key(addr):
					v = self.addressToCounts[addr]
					self.addressToCounts[addr] = (countInfo[0]+v[0], countInfo[1]+v[1], countInfo[2]+v[2], countInfo[3]+v[3])
				else:
					self.addressToCounts[addr] = countInfo

		# build addressTree
		for countInfo, stackInfo in addressInfo:
			addressDict = self.addressTree
			for addr in stackInfo:
				addressDict = addressDict.setdefault(addr, {})

	def printMe(self):
		#print self.addressTree
		self.printAddressDict(self.addressTree, 1)

	def printAddressDict(self, addressDict, indent):
		for k, v in addressDict.iteritems():
			print '%s%s' % (' '*indent, k)
			self.printAddressDict(v, indent+1)

if __name__ == '__main__':
	parser = HeapProfileParser()
	parser.parseIt(sys.argv[1])
	parser.printMe()

