#include <Windows.h>
#include <stdio.h>

extern "C" void HeapProfilerStart(const char* prefix);
extern "C" void HeapProfilerDump(const char *reason);
extern "C" void HeapProfilerStop();

void *mallocMe(unsigned int n)
{
	return malloc(n);
}

int main()
{
	// set by vc: "HEAPPROFILE=heap", below is ignore
	// HeapProfilerStart("D:\\heap");

	::Sleep(1000);

	//printf("begin\n");
	char *p = new char[1024];
	//Sleep(1000*10);
	HeapProfilerDump("Try1");
	delete[] p;
	//printf("end\n");

	::Sleep(1000);

	const int N = 3;
	void *pv[N] = {0};
	for (int i = 0; i < N; ++i)
	{
		pv[i] = mallocMe(1024*(i+1));
	}
	
	HeapProfilerDump("Try2");

	::Sleep(1000);

	for (int i = 0; i < N; ++i)
	{
		free(pv[i]);
		pv[i] = 0;
	}

	HLOCAL localPtr = LocalAlloc(LMEM_MOVEABLE, 1024);
	HeapProfilerDump("Try3");

	::Sleep(1000);

	LocalFree(localPtr);
	HeapProfilerDump("Try4");

//	void* p1 = HeapAlloc(GetProcessHeap(), 0, 1024);
//	HeapProfilerDump("Try3");
//	HeapFree(GetProcessHeap(), 0, p1);
//	HeapProfilerDump("Try4");

//	HLOCAL ptr = GlobalAlloc(GPTR, 1024);
//	HeapProfilerDump("Try3");
//	GlobalFree(ptr);
//	HeapProfilerDump("Try4");

	::Sleep(1000);

//	HeapProfilerStop();  // should call this manually, or it'll crashed in VS2015
	return 0;
}

