// -*- Mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*-
// Copyright (c) 2007, Google Inc.
// All rights reserved.
// 
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
// 
//     * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//     * Neither the name of Google Inc. nor the names of its
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// ---
// This file just provides storage for FLAGS_verbose.

#include <config.h>
#include "base/logging.h"
#include "base/commandlineflags.h"

DEFINE_int32(verbose, EnvToInt("PERFTOOLS_VERBOSE", 0),
             "Set to numbers >0 for more verbose output, or <0 for less.  "
             "--verbose == -4 means we log fatal errors only.");

#if defined(FAT_LOGGING_ASYNCIO)

#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <assert.h>

namespace Fat { namespace AsyncIO {

template <typename T, int MAX_ITEMS>
class threadsafe_queue
{
public:
	threadsafe_queue() :
		read_(0),
		write_(0)
	{

	}

	threadsafe_queue(const threadsafe_queue& rhs) = delete;
	threadsafe_queue& operator=(const threadsafe_queue&) = delete;

	void push(T new_value)
	{
		std::lock_guard<std::mutex> lock(mutex_);
		data_queue_[write_++] = new_value;
		write_ = write_ % MAX_ITEMS;
		cond_.notify_one();
	}

	bool try_pop(T& value)
	{
		std::lock_guard<std::mutex> lock(mutex_);
		if (data_queue_empty())
			return false;
		value = data_queue_[read_++];
		read_ = read_ % MAX_ITEMS;
		return true;
	}

	void wait_and_pop(T& value)
	{
		std::unique_lock<std::mutex> lock(mutex_);
		cond_.wait(lock, [this] { return !data_queue_empty(); });
		value = data_queue_[read_++];
		read_ = read_ % MAX_ITEMS;
	}

	bool empty() const
	{
		std::lock_guard<std::mutex> lock(mutex_);
		return data_queue_empty();
	}

protected:
	bool data_queue_empty() const
	{
		return (read_ == write_);
	}

private:
	mutable std::mutex mutex_;
	std::condition_variable cond_;
	T data_queue_[MAX_ITEMS];
	int read_;
	int write_;
};

struct MyCmd
{
	enum { OP_WRITE = 0, OP_QUIT };
	int op;
	char* filename;
	void* data;
	size_t length;
};
typedef threadsafe_queue<MyCmd, 8> MyQueue;

class MyThreadEntry
{
public:
	MyThreadEntry(MyQueue& que) : que_(que) {}

	void WriteToFile(MyCmd& cmd)
	{
		FILE *fp = fopen(cmd.filename, "wb");
		if (fp == NULL)
			return;

		fwrite(cmd.data, cmd.length, 1, fp);
		fclose(fp);
	}

	void operator()()
	{
		bool running = true;
		MyCmd cmd;
		while (running)
		{
			que_.wait_and_pop(cmd);
			switch (cmd.op)
			{
			case MyCmd::OP_WRITE:
				WriteToFile(cmd);
				break;

			case MyCmd::OP_QUIT:
				running = false;
				break;

			default:
				assert(0);
				break;
			}
		}
	}

private:
	MyQueue& que_;
};

static MyQueue& CommandQueue()
{
	static MyQueue s_myQueue;
	return s_myQueue;
}

static std::thread* s_myIOThread = nullptr;

void Init()
{
	static MyThreadEntry s_myThreadEntry(CommandQueue());
	s_myIOThread = new std::thread(s_myThreadEntry);
//	std::thread myThread(s_myThreadEntry);
//	myThread.detach();
}

void Shutdown()
{
	MyCmd cmd;
	cmd.op = MyCmd::OP_QUIT;
	CommandQueue().push(cmd);

	// wait i/o thread quit
	// std::this_thread::sleep_for(std::chrono::milliseconds(100));
	s_myIOThread->join();
	delete s_myIOThread;
}

}}

template <typename T, int MAX_ITEMS>
class cache_queue
{
public:
	cache_queue() :
		write_(0)
	{

	}

	cache_queue(const cache_queue& rhs) = delete;
	cache_queue& operator=(const cache_queue&) = delete;

	T& get()
	{
		T& ret = data_queue_[write_++];
		write_ = write_ % MAX_ITEMS;
		return ret;
	}

private:
	T data_queue_[MAX_ITEMS];
	int write_;
};

struct FileContext
{
	enum { FILENAME_LENGTH = 256, FILE_MAX_LENGTH = (2*1024*1024) };
	char filename[FILENAME_LENGTH];
	char data[FILE_MAX_LENGTH];
	size_t length;
};

typedef cache_queue<FileContext, 4> FileContextQueue;
static FileContextQueue& GlobalFileQueue()
{
	static FileContextQueue s_fileQueue;
	return s_fileQueue;
}

RawFD RawOpenForWriting(const char* filename)
{
	FileContext& fc = GlobalFileQueue().get();
	strcpy(fc.filename, filename);
	fc.length = 0;
	return (RawFD)&fc;
}

void RawWrite(RawFD fd, const char* buf, size_t len)
{
	FileContext& fc = *(FileContext*)fd;
	assert(fc.length + len <= FileContext::FILE_MAX_LENGTH);
	memcpy(fc.data + fc.length, buf, len);
	fc.length += len;
}

void RawClose(RawFD fd)
{
	using namespace Fat::AsyncIO;

	FileContext& fc = *(FileContext*)fd;
	MyCmd cmd;
	cmd.op = MyCmd::OP_WRITE;
	cmd.filename = fc.filename;
	cmd.data     = fc.data;
	cmd.length   = fc.length;
	CommandQueue().push(cmd);
}


#else

#if defined(_WIN32) || defined(__CYGWIN__) || defined(__CYGWIN32__)

// While windows does have a POSIX-compatible API
// (_open/_write/_close), it acquires memory.  Using this lower-level
// windows API is the closest we can get to being "raw".
RawFD RawOpenForWriting(const char* filename) {
  // CreateFile allocates memory if file_name isn't absolute, so if
  // that ever becomes a problem then we ought to compute the absolute
  // path on its behalf (perhaps the ntdll/kernel function isn't aware
  // of the working directory?)
  RawFD fd = CreateFileA(filename, GENERIC_WRITE, 0, NULL,
                         CREATE_ALWAYS, 0, NULL);
  if (fd != kIllegalRawFD && GetLastError() == ERROR_ALREADY_EXISTS)
    SetEndOfFile(fd);    // truncate the existing file
  return fd;
}

void RawWrite(RawFD handle, const char* buf, size_t len) {
  while (len > 0) {
    DWORD wrote;
    BOOL ok = WriteFile(handle, buf, len, &wrote, NULL);
    // We do not use an asynchronous file handle, so ok==false means an error
    if (!ok) break;
    buf += wrote;
    len -= wrote;
  }
}

void RawClose(RawFD handle) {
  CloseHandle(handle);
}

#else  // _WIN32 || __CYGWIN__ || __CYGWIN32__

#ifdef HAVE_SYS_TYPES_H
#include <sys/types.h>
#endif
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#ifdef HAVE_FCNTL_H
#include <fcntl.h>
#endif

// Re-run fn until it doesn't cause EINTR.
#define NO_INTR(fn)  do {} while ((fn) < 0 && errno == EINTR)

RawFD RawOpenForWriting(const char* filename) {
  return open(filename, O_WRONLY|O_CREAT|O_TRUNC, 0664);
}

void RawWrite(RawFD fd, const char* buf, size_t len) {
  while (len > 0) {
    ssize_t r;
    NO_INTR(r = write(fd, buf, len));
    if (r <= 0) break;
    buf += r;
    len -= r;
  }
}

void RawClose(RawFD fd) {
  NO_INTR(close(fd));
}

#endif  // _WIN32 || __CYGWIN__ || __CYGWIN32__

#endif  // FAT_LOGGING_ASYNCIO
