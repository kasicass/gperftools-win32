# usage:
#   python PrintHeapMax.py -l 50 xxx.heap    # print liveBytes >= 50Mb callstacks

import sys
import argparse
import HeapProfileParser
import HeapProfileAddressTable

if __name__ == '__main__':
	ap = argparse.ArgumentParser(description='Print callstacks that liveBytes >= LIMIT Mb')
	ap.add_argument('-l', '--limit', dest='limit', type=int, default=1, help='> LIMIT Mb to print')
	ap.add_argument('filename', help='.heap file to parse')
	args = ap.parse_args()

	parser = HeapProfileParser.HeapProfileParser()
	parser.parseIt(args.filename)

	# filter "liveBytes >= LIMIT Mb"
	addressInfo = []
	args.limit  = args.limit*1024*1024
	for countInfo, stackInfo in parser.addressInfo:
		if countInfo[1] >= args.limit:
			addressInfo.append((countInfo, stackInfo))

	if not addressInfo:
		sys.exit(0)

	parser.addressInfo = addressInfo
	at = HeapProfileAddressTable.HeapProfileAddressTable(parser)
	at.buildTable()

	result = [] # (liveCount, liveBytes, sumCount, sumBytes, callstack)
	for countInfo, stackInfo in parser.addressInfo:
		callstack = []
		for addr in stackInfo:
			name = at.addr2name(addr)
			callstack.append('%s(%s:%d)' %(name[0], name[1], name[2]))
		result.append((countInfo[0], countInfo[1], countInfo[2], countInfo[3], callstack))

	for v in result:
		print 'liveCount: %d, liveBytes: %.2f Mb, sumCount: %d, sumBytes: %.2f Mb' % (v[0], v[1]/(1024.0*1024.0), v[2], v[3]/(1024.0*1024.0))
		for line in v[4]:
			print '  ', line
		print

