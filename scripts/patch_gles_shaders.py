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
