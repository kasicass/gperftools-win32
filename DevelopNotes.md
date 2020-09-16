# Develop Notes

## 2020-09-16

 * 给 logger.cc 增加异步线程写文件，保证 NewHook / DeleteHook 不触发内存分配
 * 打开 FAT_LOGGING_ASYNCIO 宏启用，需要手工 Fat::AsyncIO::Init / Shutdown

## 2020-09-15

 * 升级 gperftools 2.8

```
HeapProfilerDump() 还是会 block 住，需要修改 NewHook / DeleteHook，增加 "if (dumping) return;"
block 的原因是同一线程，两次调用了 SpinLock.Lock()，修改 NewHook / DeleteHook 只能减缓问题发生概率，不能根治。

参考以前的提交记录，https://github.com/kasicass/gperftools-win32/commit/81bce141febbddf30d379f080d50ab4e49545016
可以解决 block 的问题。但记录可能会稍许不准确。需要调整一下 PrintHeapMax.py 兼容下。
```
