#include <Windows.h>
#include <stdio.h>

extern "C" void HeapProfilerStart(const char* prefix);
extern "C" void HeapProfilerDump(const char *reason);

void *mallocMe(unsigned int n)
{
	return malloc(n);
}

int main()
{
	HeapProfilerStart("D:\\heap");

	//printf("begin\n");
	char *p = new char[1024];
	//Sleep(1000*10);
	HeapProfilerDump("Try1");
	delete[] p;
	//printf("end\n");

	const int N = 3;
	void *pv[N] = {0};
	for (int i = 0; i < N; ++i)
	{
		pv[i] = mallocMe(1024*(i+1));
	}
	
	HeapProfilerDump("Try2");

	for (int i = 0; i < N; ++i)
	{
		free(pv[i]);
		pv[i] = 0;
	}

	return 0;
}
