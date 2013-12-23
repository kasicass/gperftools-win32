#include <Windows.h>
#include <stdio.h>

extern "C" void HeapProfilerStart(const char* prefix);
extern "C" void HeapProfilerDump(const char *reason);

int main()
{
	HeapProfilerStart("D:\\heap");

	printf("begin\n");
	char *p = new char[1024];
	//Sleep(1000*10);
	HeapProfilerDump("Try1");
	delete[] p;
	printf("end\n");

	return 0;
}
