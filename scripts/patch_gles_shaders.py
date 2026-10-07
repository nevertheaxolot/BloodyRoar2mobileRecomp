p = 'psxrecomp/runtime/src/gpu_gl_renderer.c'
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read().replace('\ufeff', '')
if 'BR2_GLSL_VER' in s:
    print('GLSL: ya parcheado')
else:
    n = s.count('"#version 330\\n"')
    s = s.replace('"#version 330\\n"', 'BR2_GLSL_VER')
    hdr = ('#ifdef __ANDROID__\n'
           '#define BR2_GLSL_VER "#version 300 es\\n" "#extension GL_EXT_blend_func_extended : enable\\n" "precision highp float;\\n" "precision highp int;\\n" "precision highp sampler2D;\\n" "precision highp usampler2D;\\n" "precision highp isampler2D;\\n"\n'
           '#else\n'
           '#define BR2_GLSL_VER "#version 330\\n"\n'
           '#endif\n')
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(hdr + s)
    print('GLSL reemplazos:', n)

# --- diagnostico GL ---
import re
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'GL funcion faltante' in s:
    print('DIAG: ya parcheado')
else:
    s, a = re.subn(r'if\s*\(\s*!p\s*\)\s*ok\s*=\s*0\s*;',
        lambda m: 'if (!p) { ok = 0; fprintf(stdout, "psxrecomp: GL funcion faltante: %s\\n", n); }', s, count=1)
    i = s.find('static int init_gpu_raster(void) {')
    j = s.find('\n}\n', i) if i >= 0 else -1
    b = 0
    if i >= 0 and j > i:
        body, b = re.subn(r'\breturn 0;',
            lambda m: '{ fprintf(stdout, "psxrecomp: init_gpu_raster fallo (linea %d)\\n", __LINE__); return 0; }', s[i:j])
        s = s[:i] + body + s[j:]
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
    print('DIAG: LOAD=%d returns=%d' % (a, b))

# --- dual-source via EXT en ES ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
old = 'LOAD(p_glBindFragDataLocationIndexed, "glBindFragDataLocationIndexed");'
new = ('p_glBindFragDataLocationIndexed = (void *)SDL_GL_GetProcAddress("glBindFragDataLocationIndexed"); '
       'if (!p_glBindFragDataLocationIndexed) p_glBindFragDataLocationIndexed = (void *)SDL_GL_GetProcAddress("glBindFragDataLocationIndexedEXT"); '
       'if (!p_glBindFragDataLocationIndexed) { ok = 0; fprintf(stdout, "psxrecomp: GL funcion faltante: glBindFragDataLocationIndexed(EXT)\\n"); }')
print('IDX:', s.count(old))
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)

# --- noperspective no existe en ES + diag de extension ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
n = len(re.findall(r'\bnoperspective\s+', s))
s = re.sub(r'\bnoperspective\s+', '', s)
if 'EXT_blend_func_extended=' not in s:
    anchor = 'int ok = load_modern_gl();'
    diag = ('{ const char *ex = (const char *)glGetString(0x1F03); '
            'fprintf(stdout, "psxrecomp: EXT_blend_func_extended=%d\\n", (ex && strstr(ex, "GL_EXT_blend_func_extended")) ? 1 : 0); } ')
    print('EXTDIAG anclas:', s.count(anchor))
    s = s.replace(anchor, diag + anchor, 1)
    s = '#include <string.h>\n' + s
open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
print('NOPERSP quitados:', n)

# --- diag: GPU y framebuffer fetch ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'FBFETCH ext=' not in s:
    anchor = 'int ok = load_modern_gl();'
    diag = ('{ const char *ex = (const char *)glGetString(0x1F03); const char *rn = (const char *)glGetString(0x1F01); '
            'fprintf(stdout, "psxrecomp: GL_RENDERER=%s\\n", rn ? rn : "?"); '
            'fprintf(stdout, "psxrecomp: FBFETCH ext=%d arm=%d\\n", (ex && strstr(ex, "GL_EXT_shader_framebuffer_fetch")) ? 1 : 0, (ex && strstr(ex, "GL_ARM_shader_framebuffer_fetch")) ? 1 : 0); } ')
    print('FBDIAG anclas:', s.count(anchor))
    s = s.replace(anchor, diag + anchor, 1)
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)

# --- sin dual-source: quitar 2a salida y bind ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
a = s.count('out vec4 blend_factor;')
s = s.replace('out vec4 blend_factor;', '')
b = len(re.findall(r'blend_factor\s*=\s*vec4\(', s))
s = re.sub(r'blend_factor\s*=\s*vec4\(', 'vec4 bf_unused = vec4(', s)
c = s.count('if (dual_source) {')
s = s.replace('if (dual_source) {', 'if (0 && dual_source) {')
open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
print('DUAL: out=%d asign=%d bind=%d' % (a, b, c))

# --- diag: trazas del runtime activadas desde main() ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
anchor = 'br2_redirect_stdio();'
if 'BR2_TRACE_ENV' in m:
    print('TRACE: ya parcheado')
else:
    add = ' /*BR2_TRACE_ENV*/ setenv("PSX_CD_DMA_TRACE", "1", 0); setenv("PSX_FPS_TELEMETRY", "1", 0);'
    print('TRACE anclas:', m.count(anchor))
    m = m.replace(anchor, anchor + add, 1)
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)

# --- launcher_warning tambien al log ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'LAUNCHER_WARNING [' in m:
    print('LW: ya parcheado')
else:
    pat = r'static void launcher_warning\(const char\* title, const std::string& msg\)\s*\{'
    add = ' fprintf(stdout, "psxrecomp: LAUNCHER_WARNING [%s] %s\\n", title ? title : "", msg.c_str());'
    m, k = re.subn(pat, lambda x: x.group(0) + add, m, count=1)
    print('LW anclas:', k)
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)

# --- jugador 1 = mando por defecto en Android ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
old = '(i == 0) ? "keyboard" : "none"'
if 'BR2_P1_PAD' in m:
    print('P1: ya parcheado')
else:
    print('P1 anclas:', m.count(old))
    m = m.replace(old, '(i == 0) ? (std::getenv("BR2_P1_DEVICE") ? std::getenv("BR2_P1_DEVICE") : "keyboard") /*BR2_P1_PAD*/ : "none"')
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)

# --- semitransparencia en una pasada (framebuffer fetch) + modo rapido ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'BR2_FAST_MODE' in s:
    print('FAST: ya parcheado')
else:
    cnt = {}
    def rx(name, pat, new):
        global s
        n = len(re.findall(pat, s))
        cnt[name] = n
        if n == 1:
            s = re.sub(pat, lambda m: new, s, count=1)
    rx('EXT', re.escape('"#extension GL_EXT_blend_func_extended : enable\\n"'),
       '"#extension GL_EXT_blend_func_extended : enable\\n" "#extension GL_ARM_shader_framebuffer_fetch : enable\\n"')
    rx('FS', r'frag\s*=\s*vec4\(rgb,\s*\(stp == 1 \|\| u_maskset == 1\)\s*\?\s*1\.0\s*:\s*0\.0\);',
       '\\n#ifdef GL_ARM_shader_framebuffer_fetch\\n  if (u_semimode == 4) rgb += gl_LastFragColorARM.rgb * dst_factor;\\n#endif\\n  frag = vec4(rgb, (stp == 1 || u_maskset == 1) ? 1.0 : 0.0);')
    rx('BL', r'glEnable\(GL_BLEND\);\s*p_glBlendEquationSeparate\(PSXGL_FUNC_ADD,\s*PSXGL_FUNC_ADD\);\s*p_glBlendFuncSeparate\(GL_ONE,\s*PSXGL_SRC1_ALPHA,\s*GL_ONE,\s*GL_ZERO\);',
       'glDisable(GL_BLEND); /* BR2: mezcla en el shader (framebuffer fetch) */')
    rx('ISO', r'int isolate = \(semi >= 0\);',
       'int isolate = (semi >= 0) && !(br2_fast_mode() && batch_semi == 4);')
    rx('HLP', re.escape('static int load_modern_gl(void) {'),
       r'''static int br2_fast_mode(void) { /*BR2_FAST_MODE*/
  static int v = -1;
  if (v < 0) { const char* e = getenv("BR2_FAST"); v = (e && e[0] == '0') ? 0 : 1; fprintf(stdout, "psxrecomp: BR2_FAST=%d\n", v); }
  return v;
}
static int load_modern_gl(void) {''')
    print('FAST anclas:', cnt)
    if all(v == 1 for v in cnt.values()):
        open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
        print('FAST: OK')
    else:
        print('FAST: ANCLAS NO COINCIDEN, no se modifico')

# --- FBO perezoso: hr_end() ya no desenlaza el framebuffer (BR2_LAZYFBO) ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'BR2_LAZYFBO' in s:
    print('LAZY: ya parcheado')
else:
    pat = r'static void hr_end\(void\) \{([^}]*?)p_glBindFramebuffer\(PSXGL_FRAMEBUFFER,\s*0\);'
    nhr = len(re.findall(pat, s))
    helper = r'''static int br2_hr_lazy = 0;
static int br2_lazy_enabled(void) { /*BR2_LAZYFBO*/
  static int v = -1;
  if (v < 0) { const char* e = getenv("BR2_LAZYFBO"); v = (e && e[0] == '0') ? 0 : 1; fprintf(stdout, "psxrecomp: BR2_LAZYFBO=%d\n", v); }
  return v;
}
static void br2_hr_release(void) { if (br2_hr_lazy) { br2_hr_lazy = 0; p_glBindFramebuffer(PSXGL_FRAMEBUFFER, 0); } }
'''
    names = []
    if nhr == 1:
        s = re.sub(pat, lambda m: helper + 'static void hr_end(void) {' + m.group(1) + 'if (br2_lazy_enabled()) br2_hr_lazy = 1; else p_glBindFramebuffer(PSXGL_FRAMEBUFFER, 0);', s, count=1)
        pat2 = r'(?m)^((?:int|void)\s+(gl_renderer_[A-Za-z0-9_]+)\s*\([^)]*\)\s*\{)'
        def inj(m):
            nm = m.group(2)
            if 'diag' in nm or 'report' in nm:
                return m.group(0)
            names.append(nm)
            return m.group(1) + ' br2_hr_release();'
        s = re.sub(pat2, inj, s)
    print('LAZY: hr_end=%d entradas=%s' % (nhr, names))
    if nhr == 1 and len(names) >= 1:
        open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
        print('LAZY: OK')
    else:
        print('LAZY: ANCLAS NO COINCIDEN, no se modifico')

# --- FBO perezoso: declaracion adelantada de br2_hr_release ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'BR2_LAZY_FWD' in s:
    print('FWD: ya parcheado')
else:
    a = 'static int load_modern_gl(void) {'
    n = s.count(a)
    has = 'static void br2_hr_release(void) {' in s
    print('FWD anclas:', n, '| definicion presente:', has)
    if n == 1 and has:
        s = s.replace(a, 'static void br2_hr_release(void); /*BR2_LAZY_FWD*/\n' + a, 1)
        open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
        print('FWD: OK')
    else:
        print('FWD: ANCLAS NO COINCIDEN, no se modifico')

# --- muestreador de PC (BR2_PROF=1); apagado por defecto ---
ph = 'psxrecomp/runtime/src/android_stdio_log.h'
h = open(ph, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'br2_prof_thread' in h:
    print('BR2_PROF: ya parcheado')
else:
    a1 = 'static inline void br2_redirect_stdio() {\n  setvbuf(stdout'
    a2 = 'pthread_detach(t);\n}\n#else'
    print('BR2_PROF anclas: a1=%d a2=%d' % (h.count(a1), h.count(a2)))
    code = r'''#include <stdint.h>
#include <signal.h>
#include <ucontext.h>
#include <dlfcn.h>
#include <sys/syscall.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#ifndef BR2_PROF_WIN_SEC
#define BR2_PROF_WIN_SEC 10
#endif
#ifndef BR2_PROF_HZ
#define BR2_PROF_HZ 2000
#endif
#define BR2_PC(uc) ((uintptr_t)((ucontext_t*)(uc))->uc_mcontext.pc)
static volatile int br2_game_tid = 0;
static uintptr_t br2_samples[16384];
static volatile unsigned br2_head = 0;
static void br2_prof_handler(int, siginfo_t*, void* uc) {
  br2_samples[br2_head++ & 16383u] = BR2_PC(uc);
}
struct br2_pe { uintptr_t k; unsigned n; };
struct br2_le { char name[40]; unsigned n; };
static br2_pe br2_ptab[32768];
static br2_le br2_ltab[24];
static int br2_pe_cmp(const void* a, const void* b) {
  const br2_pe* x = (const br2_pe*)a; const br2_pe* y = (const br2_pe*)b;
  return (x->n < y->n) - (x->n > y->n);
}
static int br2_le_cmp(const void* a, const void* b) {
  const br2_le* x = (const br2_le*)a; const br2_le* y = (const br2_le*)b;
  return (x->n < y->n) - (x->n > y->n);
}
static void* br2_prof_thread(void*) {
  const pid_t pid = getpid();
  Dl_info mi; memset(&mi, 0, sizeof mi);
  uintptr_t base = 0;
  if (dladdr((void*)&br2_prof_thread, &mi) && mi.dli_fbase) base = (uintptr_t)mi.dli_fbase;
  const int per_sec = BR2_PROF_HZ;
  const long step_ns = 1000000000L / per_sec;
  unsigned last = br2_head;
  for (int win = 1; win <= 60; win++) {
    memset(br2_ptab, 0, sizeof br2_ptab); memset(br2_ltab, 0, sizeof br2_ltab);
    unsigned total = 0, inlib = 0, dropped = 0;
    for (int s = 0; s < BR2_PROF_WIN_SEC; s++) {
      for (int i = 0; i < per_sec; i++) {
        struct timespec ts = {0, step_ns}; nanosleep(&ts, nullptr);
        syscall(SYS_tgkill, pid, (pid_t)br2_game_tid, SIGPROF);
      }
      unsigned cnt = br2_head - last;
      if (cnt > 16384u) { dropped += cnt - 16384u; cnt = 16384u; last = br2_head - cnt; }
      for (unsigned i = 0; i < cnt; i++) {
        uintptr_t pc = br2_samples[(last + i) & 16383u];
        total++;
        Dl_info di; memset(&di, 0, sizeof di);
        if (dladdr((void*)pc, &di) && di.dli_fbase == (void*)base && pc >= base) {
          uintptr_t k = (pc - base) >> 4; inlib++;
          unsigned h = (unsigned)((k * 2654435761u) >> 7) & 32767u;
          for (int probe = 0; probe < 32768; probe++, h = (h + 1) & 32767u) {
            if (br2_ptab[h].n == 0) { br2_ptab[h].k = k; br2_ptab[h].n = 1; break; }
            if (br2_ptab[h].k == k) { br2_ptab[h].n++; break; }
          }
        } else {
          const char* fn = di.dli_fname ? strrchr(di.dli_fname, '/') : nullptr;
          fn = fn ? fn + 1 : (di.dli_fname ? di.dli_fname : "?");
          int f = -1;
          for (int j = 0; j < 24; j++) if (br2_ltab[j].n && strncmp(br2_ltab[j].name, fn, 39) == 0) { f = j; break; }
          if (f < 0) for (int j = 0; j < 24; j++) if (!br2_ltab[j].n) { f = j; snprintf(br2_ltab[j].name, 40, "%s", fn); break; }
          if (f >= 0) br2_ltab[f].n++;
        }
      }
      last = br2_head;
    }
    qsort(br2_ltab, 24, sizeof(br2_le), br2_le_cmp);
    char line[1200]; int o = snprintf(line, sizeof line, "BR2PROF win=%d n=%u inlib=%u drop=%u base=0x%lx other:", win, total, inlib, dropped, (unsigned long)base);
    for (int j = 0; j < 5 && br2_ltab[j].n && o < 1000; j++)
      o += snprintf(line + o, sizeof line - o, " %s=%u", br2_ltab[j].name, br2_ltab[j].n);
    fprintf(stdout, "%s\n", line);
    qsort(br2_ptab, 32768, sizeof(br2_pe), br2_pe_cmp);
    char out[3200]; int p = 0;
    for (int j = 0; j < 1200 && br2_ptab[j].n; j++) {
      if (p == 0) p = snprintf(out, sizeof out, "BR2PCS w%d", win);
      p += snprintf(out + p, sizeof out - p, " %lx:%u", (unsigned long)(br2_ptab[j].k << 4), br2_ptab[j].n);
      if (p > 3000) { fprintf(stdout, "%s\n", out); p = 0; }
    }
    if (p) fprintf(stdout, "%s\n", out);
    fflush(stdout);
  }
  return nullptr;
}
static inline void br2_start_prof() {
  const char* e = getenv("BR2_PROF");
  if (!e || e[0] != '1') return;
  br2_game_tid = (int)syscall(SYS_gettid);
  stack_t ss; ss.ss_sp = malloc(65536); ss.ss_size = 65536; ss.ss_flags = 0;
  if (ss.ss_sp && sigaltstack(&ss, nullptr) == 0) {
    struct sigaction sa; memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = br2_prof_handler; sa.sa_flags = SA_SIGINFO | SA_ONSTACK | SA_RESTART;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGPROF, &sa, nullptr) == 0) {
      pthread_t t2;
      if (pthread_create(&t2, nullptr, br2_prof_thread, nullptr) == 0) pthread_detach(t2);
    }
  }
}
'''
    if h.count(a1) == 1 and h.count(a2) == 1:
        h = h.replace(a1, code + a1, 1)
        h = h.replace(a2, 'pthread_detach(t);\n  br2_start_prof();\n}\n#else', 1)
        open(ph, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(h)
        print('BR2_PROF: OK')
    else:
        print('BR2_PROF: ANCLAS NO COINCIDEN, no se modifico')

# --- log de "unknown dispatch" (BR2Fatal) ---
pt = 'psxrecomp/runtime/src/traps.c'
t = open(pt, encoding='utf-8', errors='surrogateescape', newline='').read()
anc = '        if (s_fail_fast) {\n            extern void psx_crash_trace_dump(const char *reason, void *seh_info);'
print('BR2Fatal ancla:', t.count(anc))
if t.count(anc) == 1 and 'BR2Fatal' not in t:
    add = ('#ifdef __ANDROID__\n'
           '        { extern int __android_log_print(int, const char *, const char *, ...);\n'
           '          static int br2_n = 0;\n'
           '          if (br2_n++ < 40) __android_log_print(6, "BR2Fatal", "unknown dispatch addr=0x%08X phys=0x%08X ra=0x%08X a0=0x%08X a1=0x%08X failfast=%d", addr, phys, cpu->gpr[31], cpu->gpr[4], cpu->gpr[5], s_fail_fast); }\n'
           '#endif\n')
    t = t.replace(anc, add + anc, 1)
    open(pt, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(t)
    print('BR2Fatal: OK')

# --- BR2_NOGUARD: permite saltar el guard de la imagen de texto ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
anc = '    if (game_config_path)\n        arm_text_image_guard(text_guard_exe_path, text_guard_load_addr,\n                             disc_path_str);\n'
print('BR2_NOGUARD ancla:', m.count(anc))
if m.count(anc) == 1 and 'BR2_NOGUARD' not in m:
    new = ('    if (game_config_path && !(getenv("BR2_NOGUARD") && getenv("BR2_NOGUARD")[0] == \'1\'))\n'
           '        arm_text_image_guard(text_guard_exe_path, text_guard_load_addr,\n'
           '                             disc_path_str);\n'
           '    else if (game_config_path)\n'
           '        std::fprintf(stdout, "psxrecomp: BR2_NOGUARD=1 (text image guard skipped)\\n");\n')
    m = m.replace(anc, new, 1)
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)
    print('BR2_NOGUARD: OK')
