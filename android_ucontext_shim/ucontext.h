#ifndef PSX_ANDROID_UCONTEXT_SHIM_H
#define PSX_ANDROID_UCONTEXT_SHIM_H

#include <libucontext/libucontext.h>

#define ucontext_t   libucontext_ucontext_t
#define getcontext   libucontext_getcontext
#define setcontext   libucontext_setcontext
#define makecontext  libucontext_makecontext
#define swapcontext  libucontext_swapcontext

#endif
