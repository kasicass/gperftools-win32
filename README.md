# gperftools-win32

## FEATURES

 * [https://github.com/gperftools/gperftools][1]
 * make heap-profiler runs in win32
 * simple .heap parser in [tools]

## KNOWN ISSUES

```
 VS2015 Update 3, Debug Build, crashed when program exit
   exit_program() => Load a DLL => PatchAllModules() =>
   crt iterator_check => crashed in ntdll.dll
   Release Build is ok
```

[1]:https://github.com/gperftools/gperftools
