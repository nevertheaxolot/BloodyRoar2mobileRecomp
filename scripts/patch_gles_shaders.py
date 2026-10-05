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
    add = ' /*BR2_TRACE_ENV*/ setenv("PSX_CD_DMA_TRACE", "1", 1); setenv("PSX_FPS_TELEMETRY", "1", 1);'
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

# --- diag: mando (GUID, mapeo y eventos de botones) ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'BR2PAD' in m:
    print('PAD: ya parcheado')
else:
    pat = r'(std::fprintf\(stdout, "psxrecomp runtime: opened controller for slot: %s\\n",\s*name \? name : "\(unnamed\)"\);)'
    add = r'''
 { char* br2mp = SDL_GameControllerMapping(p.handle);
   std::fprintf(stdout, "BR2PAD opened guid=%s mapping=%s\n", p.guid, br2mp ? br2mp : "(none)");
   if (br2mp) SDL_free(br2mp);
   static bool br2w = false;
   if (!br2w) { br2w = true;
     SDL_AddEventWatch([](void*, SDL_Event* e) -> int {
       if (e->type == SDL_CONTROLLERBUTTONDOWN || e->type == SDL_CONTROLLERBUTTONUP)
         std::fprintf(stdout, "BR2PAD cbutton %s %s\n", SDL_GameControllerGetStringForButton((SDL_GameControllerButton)e->cbutton.button), e->type == SDL_CONTROLLERBUTTONDOWN ? "down" : "up");
       else if (e->type == SDL_JOYBUTTONDOWN || e->type == SDL_JOYBUTTONUP)
         std::fprintf(stdout, "BR2PAD joybutton %d %s\n", (int)e->jbutton.button, e->type == SDL_JOYBUTTONDOWN ? "down" : "up");
       else if (e->type == SDL_JOYHATMOTION)
         std::fprintf(stdout, "BR2PAD hat %d value %d\n", (int)e->jhat.hat, (int)e->jhat.value);
       return 0; }, nullptr); } }'''
    m, k = re.subn(pat, lambda x: x.group(1) + add, m)
    print('PAD anclas:', k)
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)

# --- diag: eventos de entrada (teclas, joystick, mando) ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'br2_evwatch' in s:
    print('IN: ya parcheado')
else:
    fn = r'''static int br2_evwatch(void *ud, SDL_Event *e) {
    (void)ud;
    if ((e->type == SDL_KEYDOWN && !e->key.repeat) || e->type == SDL_KEYUP)
        fprintf(stdout, "BR2IN key %s %s\n", SDL_GetKeyName(e->key.keysym.sym), e->type == SDL_KEYDOWN ? "down" : "up");
    else if (e->type == SDL_JOYBUTTONDOWN || e->type == SDL_JOYBUTTONUP)
        fprintf(stdout, "BR2IN joybutton %d %s\n", (int)e->jbutton.button, e->type == SDL_JOYBUTTONDOWN ? "down" : "up");
    else if (e->type == SDL_CONTROLLERBUTTONDOWN || e->type == SDL_CONTROLLERBUTTONUP)
        fprintf(stdout, "BR2IN cbutton %s %s\n", SDL_GameControllerGetStringForButton((SDL_GameControllerButton)e->cbutton.button), e->type == SDL_CONTROLLERBUTTONDOWN ? "down" : "up");
    else if (e->type == SDL_JOYHATMOTION)
        fprintf(stdout, "BR2IN hat %d value %d\n", (int)e->jhat.hat, (int)e->jhat.value);
    else if (e->type == SDL_JOYDEVICEADDED || e->type == SDL_CONTROLLERDEVICEADDED)
        fprintf(stdout, "BR2IN device added index=%d\n", (int)e->jdevice.which);
    return 0;
}
'''
    a1 = 'static int load_modern_gl(void) {'
    a2 = 'int ok = load_modern_gl();'
    add2 = r'''SDL_AddEventWatch(br2_evwatch, NULL); fprintf(stdout, "BR2IN joysticks=%d\n", SDL_NumJoysticks()); '''
    print('IN anclas: a1=%d a2=%d' % (s.count(a1), s.count(a2)))
    s = s.replace(a1, fn + a1, 1)
    s = s.replace(a2, add2 + a2, 1)
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)

# --- diag: PSX_GL_PERF activado ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
anc = 'setenv("PSX_FPS_TELEMETRY", "1", 1);'
if 'BR2_GL_PERF_ENV' in m:
    print('PERF: ya parcheado')
else:
    print('PERF anclas:', m.count(anc))
    m = m.replace(anc, anc + ' /*BR2_GL_PERF_ENV*/ setenv("PSX_GL_PERF", "1", 1);', 1)
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)

# --- diag: PSX_GL_PERF activado ---
pm = 'psxrecomp/runtime/src/main.cpp'
m = open(pm, encoding='utf-8', errors='surrogateescape', newline='').read()
anc = 'setenv("PSX_FPS_TELEMETRY", "1", 1);'
if 'BR2_GL_PERF_ENV' in m:
    print('PERF: ya parcheado')
else:
    print('PERF anclas:', m.count(anc))
    m = m.replace(anc, anc + ' /*BR2_GL_PERF_ENV*/ setenv("PSX_GL_PERF", "1", 1);', 1)
    open(pm, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(m)

# --- diag: info detallada de joysticks ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
old = 'fprintf(stdout, "BR2IN joysticks=%d\\n", SDL_NumJoysticks());'
if 'BR2IN joy[' in s:
    print('JOY: ya parcheado')
else:
    new = ('{ int br2n = SDL_NumJoysticks(); fprintf(stdout, "BR2IN joysticks=%d\\n", br2n); '
           'for (int i = 0; i < br2n; i++) { char gs[64]; SDL_JoystickGUID g = SDL_JoystickGetDeviceGUID(i); SDL_JoystickGetGUIDString(g, gs, (int)sizeof gs); '
           'SDL_Joystick *j = NULL; const char *jn = SDL_JoystickNameForIndex(i); '
           'fprintf(stdout, "BR2IN joy[%d] name=%s guid=%s isGC=%d buttons=%d axes=%d hats=%d\\n", i, jn ? jn : "?", gs, (int)SDL_IsGameController(i), j ? SDL_JoystickNumButtons(j) : -1, j ? SDL_JoystickNumAxes(j) : -1, j ? SDL_JoystickNumHats(j) : -1); '
           'char *mp = SDL_GameControllerMappingForGUID(g); fprintf(stdout, "BR2IN joy[%d] mapping=%s\\n", i, mp ? mp : "(none)"); if (mp) SDL_free(mp); } } ')
    print('JOY anclas:', s.count(old))
    s = s.replace(old, new, 1)
    ax = 'else if (e->type == SDL_JOYHATMOTION)'
    axnew = 'else if (e->type == SDL_JOYAXISMOTION && (e->jaxis.value > 20000 || e->jaxis.value < -20000)) fprintf(stdout, "BR2IN axis %d value %d\\n", (int)e->jaxis.axis, (int)e->jaxis.value);\n    ' + ax
    print('AXIS anclas:', s.count(ax))
    s = s.replace(ax, axnew, 1)
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)

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

# --- diag: hilos, nucleos y frecuencias (BR2PERF) ---
ph = 'psxrecomp/runtime/src/android_stdio_log.h'
h = open(ph, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'br2_perf_thread' in h:
    print('PERF2: ya parcheado')
else:
    a1 = 'static inline void br2_redirect_stdio() {\n  setvbuf(stdout'
    a2 = 'pthread_detach(t);\n}\n#else'
    print('PERF2 anclas: a1=%d a2=%d' % (h.count(a1), h.count(a2)))
    code = r'''#include <dirent.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define BR2S5 "%*s %*s %*s %*s %*s "
struct br2_ti { int tid; unsigned long long t; int cpu; char name[24]; };
static void* br2_perf_thread(void*) {
  static br2_ti prev[512]; static int np = 0;
  static br2_ti cur[512];
  const long hz = sysconf(_SC_CLK_TCK);
  for (;;) {
    struct timespec ts = {2, 0}; nanosleep(&ts, nullptr);
    int n = 0;
    DIR* d = opendir("/proc/self/task");
    if (!d) continue;
    struct dirent* e;
    while ((e = readdir(d)) != nullptr && n < 512) {
      int tid = atoi(e->d_name); if (tid <= 0) continue;
      char p[96], buf[640];
      snprintf(p, sizeof p, "/proc/self/task/%d/stat", tid);
      FILE* f = fopen(p, "r"); if (!f) continue;
      size_t k = fread(buf, 1, sizeof buf - 1, f); fclose(f); buf[k] = 0;
      char* rp = strrchr(buf, ')'); if (!rp) continue;
      unsigned long long ut = 0, st = 0; int cpu = -1;
      if (sscanf(rp + 2, "%*s %*s %*s %*s %*s %*s %*s %*s %*s %*s %*s %llu %llu " BR2S5 BR2S5 BR2S5 BR2S5 "%*s %*s %*s %d", &ut, &st, &cpu) < 2) continue;
      cur[n].name[0] = 0;
      snprintf(p, sizeof p, "/proc/self/task/%d/comm", tid);
      f = fopen(p, "r");
      if (f) { if (fgets(cur[n].name, sizeof cur[n].name, f)) { size_t L = strlen(cur[n].name); while (L && cur[n].name[L - 1] == '\n') cur[n].name[--L] = 0; } fclose(f); }
      cur[n].tid = tid; cur[n].t = ut + st; cur[n].cpu = cpu; n++;
    }
    closedir(d);
    int best[4] = {-1, -1, -1, -1}; double bp[4] = {0, 0, 0, 0};
    for (int i = 0; i < n; i++) {
      unsigned long long pt = 0;
      for (int j = 0; j < np; j++) if (prev[j].tid == cur[i].tid) { pt = prev[j].t; break; }
      double pct = (pt && cur[i].t >= pt) ? 100.0 * (double)(cur[i].t - pt) / (double)(hz * 2) : 0.0;
      for (int s = 0; s < 4; s++) {
        if (best[s] < 0 || pct > bp[s]) {
          for (int m = 3; m > s; m--) { best[m] = best[m - 1]; bp[m] = bp[m - 1]; }
          best[s] = i; bp[s] = pct; break;
        }
      }
    }
    char line[512]; int o = snprintf(line, sizeof line, "BR2PERF");
    for (int s = 0; s < 4 && best[s] >= 0 && o < 380; s++)
      o += snprintf(line + o, sizeof line - o, " [%s tid=%d %.0f%% cpu%d]", cur[best[s]].name, cur[best[s]].tid, bp[s], cur[best[s]].cpu);
    o += snprintf(line + o, sizeof line - o, " | MHz:");
    for (int c = 0; c < 8 && o < 470; c++) {
      char p2[96]; snprintf(p2, sizeof p2, "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_cur_freq", c);
      FILE* f = fopen(p2, "r"); long fr = 0;
      if (f) { if (fscanf(f, "%ld", &fr) != 1) fr = 0; fclose(f); }
      o += snprintf(line + o, sizeof line - o, " %ld", fr / 1000);
    }
    fprintf(stdout, "%s\n", line);
    memcpy(prev, cur, sizeof(br2_ti) * n); np = n;
  }
  return nullptr;
}
static inline void br2_start_perf() { pthread_t t; if (pthread_create(&t, nullptr, br2_perf_thread, nullptr) == 0) pthread_detach(t); }
'''
    if h.count(a1) == 1 and h.count(a2) == 1:
        h = h.replace(a1, code + a1, 1)
        h = h.replace(a2, 'pthread_detach(t);\n  br2_start_perf();\n}\n#else', 1)
        open(ph, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(h)
        print('PERF2: OK')
    else:
        print('PERF2: ANCLAS NO COINCIDEN, no se modifico')

# --- diag: muestreador de funciones (BR2PROF) ---
ph = 'psxrecomp/runtime/src/android_stdio_log.h'
h = open(ph, encoding='utf-8', errors='surrogateescape', newline='').read()
old = 'static inline void br2_start_perf() { pthread_t t; if (pthread_create(&t, nullptr, br2_perf_thread, nullptr) == 0) pthread_detach(t); }\n'
if 'br2_prof_thread' in h:
    print('PROF: ya parcheado')
else:
    print('PROF anclas:', h.count(old))
    newcode = r'''#include <signal.h>
#include <ucontext.h>
#include <dlfcn.h>
#include <sys/syscall.h>
static volatile int br2_game_tid = 0;
static uintptr_t br2_samples[8192];
static volatile unsigned br2_head = 0;
static void br2_prof_handler(int, siginfo_t*, void* uc) {
#if defined(__aarch64__)
  br2_samples[br2_head++ & 8191u] = (uintptr_t)((ucontext_t*)uc)->uc_mcontext.pc;
#else
  (void)uc;
#endif
}
struct br2_ent { uintptr_t key; unsigned n; char name[72]; };
static void* br2_prof_thread(void*) {
  int reports = 0;
  const pid_t pid = getpid();
  while (reports < 36) {
    unsigned t0 = br2_head;
    for (int i = 0; i < 5000; i++) {
      struct timespec ts = {0, 1000000}; nanosleep(&ts, nullptr);
      syscall(SYS_tgkill, pid, (pid_t)br2_game_tid, SIGPROF);
    }
    unsigned cnt = br2_head - t0; if (cnt > 8192) cnt = 8192;
    static br2_ent tab[256]; int nt = 0;
    for (unsigned i = 0; i < cnt; i++) {
      uintptr_t pc = br2_samples[(t0 + i) & 8191u];
      Dl_info di; memset(&di, 0, sizeof di);
      uintptr_t key = pc >> 12; const char* sn = nullptr; const char* fn = nullptr;
      if (dladdr((void*)pc, &di)) { if (di.dli_saddr) key = (uintptr_t)di.dli_saddr; sn = di.dli_sname; fn = di.dli_fname; }
      int f = -1;
      for (int j = 0; j < nt; j++) if (tab[j].key == key) { f = j; break; }
      if (f < 0 && nt < 256) {
        f = nt++; tab[f].key = key; tab[f].n = 0;
        const char* base = fn ? strrchr(fn, '/') : nullptr;
        base = base ? base + 1 : (fn ? fn : "?");
        snprintf(tab[f].name, sizeof tab[f].name, "%s@%s", sn ? sn : "?", base);
      }
      if (f >= 0) tab[f].n++;
    }
    char line[900]; int o = snprintf(line, sizeof line, "BR2PROF n=%u:", cnt);
    for (int r = 0; r < 8; r++) {
      int b = -1;
      for (int j = 0; j < nt; j++) if (tab[j].n && (b < 0 || tab[j].n > tab[b].n)) b = j;
      if (b < 0 || o > 780) break;
      o += snprintf(line + o, sizeof line - o, " %.0f%% %s |", cnt ? 100.0 * tab[b].n / cnt : 0.0, tab[b].name);
      tab[b].n = 0;
    }
    fprintf(stdout, "%s\n", line);
    reports++;
  }
  return nullptr;
}
static inline void br2_start_perf() {
  pthread_t t;
  if (pthread_create(&t, nullptr, br2_perf_thread, nullptr) == 0) pthread_detach(t);
#if defined(__aarch64__)
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
#endif
}
'''
    if h.count(old) == 1:
        h = h.replace(old, newcode, 1)
        open(ph, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(h)
        print('PROF: OK')
    else:
        print('PROF: ANCLA NO COINCIDE, no se modifico')

# --- diag: totales por biblioteca (BR2LIBS) y lotes de dibujado ---
ph = 'psxrecomp/runtime/src/android_stdio_log.h'
h = open(ph, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'BR2LIBS' in h:
    print('LIBS: ya parcheado')
else:
    cnts = {}
    def rep(name, old, new):
        global h
        cnts[name] = h.count(old)
        if cnts[name] == 1:
            h = h.replace(old, new, 1)
    rep('F', 'static void* br2_perf_thread(void*) {',
        '#include <stdint.h>\nextern "C" void gl_renderer_batch_diag(uint64_t out[8]);\nstatic void* br2_perf_thread(void*) {')
    rep('E', 'char line[512]; int o = snprintf(line, sizeof line, "BR2PERF");',
        'char line[1024]; int o = snprintf(line, sizeof line, "BR2PERF");')
    rep('D', 'fprintf(stdout, "%s\\n", line);\n    memcpy(prev, cur, sizeof(br2_ti) * n); np = n;',
        r'''{ uint64_t bd[8] = {0}; static uint64_t pbd[8]; gl_renderer_batch_diag(bd);
      o += snprintf(line + o, sizeof line - o, " | batches/s=%llu reasons:", (unsigned long long)((bd[0] - pbd[0]) / 2));
      for (int bi = 1; bi < 8; bi++) o += snprintf(line + o, sizeof line - o, " %llu", (unsigned long long)((bd[bi] - pbd[bi]) / 2));
      memcpy(pbd, bd, sizeof bd); }
    fprintf(stdout, "%s\n", line);
    memcpy(prev, cur, sizeof(br2_ti) * n); np = n;''')
    rep('A', 'static br2_ent tab[256]; int nt = 0;',
        'static br2_ent tab[256]; int nt = 0;\n    struct br2_lt { char n[32]; unsigned c; }; static br2_lt lt[16]; int nl = 0;')
    rep('B', 'int f = -1;\n      for (int j = 0; j < nt; j++)',
        r'''{ const char* lb = fn ? strrchr(fn, '/') : nullptr; lb = lb ? lb + 1 : (fn ? fn : "?");
        int li = -1; for (int j = 0; j < nl; j++) if (strncmp(lt[j].n, lb, 31) == 0) { li = j; break; }
        if (li < 0 && nl < 16) { li = nl++; snprintf(lt[li].n, sizeof lt[li].n, "%s", lb); lt[li].c = 0; }
        if (li >= 0) lt[li].c++; }
      int f = -1;
      for (int j = 0; j < nt; j++)''')
    rep('C', 'fprintf(stdout, "%s\\n", line);\n    reports++;',
        r'''fprintf(stdout, "%s\n", line);
    { char l2[400]; int o2 = snprintf(l2, sizeof l2, "BR2LIBS n=%u:", cnt);
      for (int j = 0; j < nl && o2 < 360; j++) o2 += snprintf(l2 + o2, sizeof l2 - o2, " %s=%.0f%%", lt[j].n, cnt ? 100.0 * lt[j].c / cnt : 0.0);
      fprintf(stdout, "%s\n", l2); }
    reports++;''')
    print('LIBS anclas:', cnts)
    if all(v == 1 for v in cnts.values()):
        open(ph, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(h)
        print('LIBS: OK')
    else:
        print('LIBS: ANCLAS NO COINCIDEN, no se modifico')

# --- diag: quien provoca cada vaciado del lote texturizado ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
ph = 'psxrecomp/runtime/src/android_stdio_log.h'
h = open(ph, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'br2_ftb' in s:
    print('FTB: ya parcheado')
else:
    s2, nrep = re.subn(r'\bflush_tex_batch\(\)', 'br2_ftb(__func__)', s)
    a1 = 'static int load_modern_gl(void) {'
    a2 = 'static void flush_tex_batch(void) {'
    h1 = 'extern "C" void gl_renderer_batch_diag(uint64_t out[8]);'
    h2 = 'memcpy(pbd, bd, sizeof bd); }'
    c = (s2.count(a1), s2.count(a2), h.count(h1), h.count(h2))
    print('FTB: reemplazos=%d anclas=%s' % (nrep, c))
    if nrep >= 10 and c == (1, 1, 1, 1):
        defs = r'''static uint64_t br2_ftb_cnt[64]; static const char* br2_ftb_name[64]; static int br2_ftb_n = 0;
static void br2_ftb(const char* who) {
  if (s_tb_n == 0) return;
  int k = -1;
  for (int i = 0; i < br2_ftb_n; i++) if (br2_ftb_name[i] == who) { k = i; break; }
  if (k < 0 && br2_ftb_n < 64) { k = br2_ftb_n++; br2_ftb_name[k] = who; br2_ftb_cnt[k] = 0; }
  if (k >= 0) br2_ftb_cnt[k]++;
  flush_tex_batch();
}
void gl_renderer_ftb_report(char* buf, int n) {
  static uint64_t prev[64];
  int o = 0; buf[0] = 0;
  for (int r = 0; r < 7; r++) {
    int b = -1; uint64_t bd = 0;
    for (int i = 0; i < br2_ftb_n; i++) { uint64_t d = br2_ftb_cnt[i] - prev[i]; if (d > bd) { bd = d; b = i; } }
    if (b < 0 || bd == 0 || o > n - 60) break;
    o += snprintf(buf + o, n - o, " %s=%llu", br2_ftb_name[b], (unsigned long long)(bd / 2));
    prev[b] = br2_ftb_cnt[b];
  }
  for (int i = 0; i < br2_ftb_n; i++) prev[i] = br2_ftb_cnt[i];
}
'''
        s2 = s2.replace(a1, 'static void br2_ftb(const char* who);\n' + a1, 1)
        s2 = s2.replace(a2, defs + a2, 1)
        h = h.replace(h1, h1 + '\nextern "C" void gl_renderer_ftb_report(char* buf, int n);', 1)
        h = h.replace(h2, '{ char fb[320]; gl_renderer_ftb_report(fb, (int)sizeof fb); o += snprintf(line + o, sizeof line - o, " | by:%s", fb); }\n      ' + h2, 1)
        open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s2)
        open(ph, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(h)
        print('FTB: OK')
    else:
        print('FTB: ANCLAS NO COINCIDEN, no se modifico')

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

# --- diag: tiempos por seccion dentro de flush_tex_batch (ftt) ---
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
ph = 'psxrecomp/runtime/src/android_stdio_log.h'
h = open(ph, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'BR2_LAP' in s:
    print('FTT: ya parcheado')
else:
    a_fn = 'static void flush_tex_batch(void) {'
    e1 = 'extern "C" void gl_renderer_ftb_report(char* buf, int n);'
    e2 = '" | by:%s", fb); }'
    e3 = 'char line[1024]; int o = snprintf(line, sizeof line, "BR2PERF");'
    cnt = {'FN': s.count(a_fn), 'E1': h.count(e1), 'E2': h.count(e2), 'E3': h.count(e3)}
    ok = all(v == 1 for v in cnt.values())
    body = None; nb = None
    if ok:
        i = s.find(a_fn); j = i; depth = 0; started = False
        while j < len(s):
            ch = s[j]
            if ch == '{':
                depth += 1; started = True
            elif ch == '}':
                depth -= 1
                if started and depth == 0:
                    break
            j += 1
        body = s[i:j + 1]
        nb = body
        subs = [
            ('S1', r'hr_begin\(1\);(\s*)p_glUseProgram\(s_tex_prog\);',
             lambda m: 'BR2_MARK(); hr_begin(1); BR2_LAP(0);' + m.group(1) + 'p_glUseProgram(s_tex_prog);'),
            ('S2', r'(p_glBindBuffer\(PSXGL_ARRAY_BUFFER,\s*s_tex_vbo\);)(\s*p_glBufferData\([^;]*?s_tb,\s*PSXGL_STREAM_DRAW\);)(\s*)tex_batch_draw_passes\(nverts,\s*semi\);',
             lambda m: 'BR2_LAP(1); ' + m.group(1) + m.group(2) + ' BR2_LAP(2);' + m.group(3) + 'tex_batch_draw_passes(nverts, semi); BR2_LAP(3);'),
            ('S3', r'hr_end\(\);(\s*)if \(--s_cw_flush_depth == 0\)',
             lambda m: 'BR2_LAP(4); hr_end(); BR2_LAP(5);' + m.group(1) + 'if (--s_cw_flush_depth == 0)'),
        ]
        for name, pat, f_ in subs:
            n = len(re.findall(pat, nb)); cnt[name] = n
            if n == 1:
                nb = re.sub(pat, f_, nb, count=1)
        ok = all(v == 1 for v in cnt.values())
    print('FTT anclas:', cnt)
    if ok:
        helper = r'''static double br2_acc[6]; static double br2_mark;
#define BR2_MARK() (br2_mark = cw_ms())
#define BR2_LAP(i) do { double n_ = cw_ms(); br2_acc[i] += n_ - br2_mark; br2_mark = n_; } while (0)
void gl_renderer_ftt_report(char* buf, int n) {
  static double prev[6];
  static const char* nm[6] = {"hr", "setup", "buf", "draw", "mirror", "end"};
  int o = 0; buf[0] = 0;
  for (int i = 0; i < 6 && o < n - 24; i++) {
    o += snprintf(buf + o, n - o, " %s=%.0f", nm[i], (br2_acc[i] - prev[i]) / 2.0);
    prev[i] = br2_acc[i];
  }
}
'''
        s = s.replace(body, helper + nb, 1)
        h = h.replace(e1, e1 + '\nextern "C" void gl_renderer_ftt_report(char* buf, int n);', 1)
        h = h.replace(e2, e2 + '\n      { char tb[160]; gl_renderer_ftt_report(tb, (int)sizeof tb); o += snprintf(line + o, sizeof line - o, " | ftt(ms/s):%s", tb); }', 1)
        h = h.replace(e3, 'char line[2048]; int o = snprintf(line, sizeof line, "BR2PERF");', 1)
        open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
        open(ph, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(h)
        print('FTT: OK')
    else:
        print('FTT: ANCLAS NO COINCIDEN, no se modifico')

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
