/* Puente para Android: expone getcontext/makecontext/swapcontext sin
 * prefijo, reenviando a las funciones reales de libucontext (que solo
 * declara sus nombres como libucontext_*). */
#ifndef PSX_ANDROID_UCONTEXT_SHIM_H
#define PSX_ANDROID_UCONTEXT_SHIM_H

#include <libucontext/libucontext.h>

typedef libucontext_ucontext_t ucontext_t;

int  getcontext(ucontext_t *ucp);
int  setcontext(const ucontext_t *ucp);
void makecontext(ucontext_t *ucp, void (*func)(), int argc, ...);
int  swapcontext(ucontext_t *oucp, const ucontext_t *ucp);

#endif
