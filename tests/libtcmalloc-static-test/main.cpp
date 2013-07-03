#include <Windows.h>
#include <stdio.h>

int main()
{
	printf("begin\n");
	char *p = new char[1024];
	Sleep(1000*10);
	delete[] p;
	printf("end\n");
	return 0;
}
