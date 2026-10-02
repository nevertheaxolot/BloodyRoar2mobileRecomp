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
