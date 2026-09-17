/* Puente para Android: expone getcontext/makecontext/swapcontext sin
 * prefijo, reenviando a las funciones reales de libucontext (que solo
 * declara sus nombres como libucontext_*).
 *
 * Usamos #define en vez de typedef para "ucontext_t" porque bionic (la
 * libc de Android) ya trae su propio struct ucontext (para manejo de
 * señales) definido por dentro de <signal.h>, el cual libucontext.h
 * termina incluyendo transitivamente. Un typedef nuevo chocaria con
 * ese; un #define solo sustituye texto de aqui en adelante, sin pelear
 * con lo que el sistema ya declaro antes de llegar aqui. */
#ifndef PSX_ANDROID_UCONTEXT_SHIM_H
#define PSX_ANDROID_UCONTEXT_SHIM_H

#include <libucontext/libucontext.h>

#define ucontext_t libucontext_ucontext_t

int  getcontext(ucontext_t *ucp);
int  setcontext(const ucontext_t *ucp);
void makecontext(ucontext_t *ucp, void (*func)(), int argc, ...);
int  swapcontext(ucontext_t *oucp, const ucontext_t *ucp);

#endif
