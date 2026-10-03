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
           'SDL_Joystick *j = SDL_JoystickOpen(i); const char *jn = SDL_JoystickNameForIndex(i); '
           'fprintf(stdout, "BR2IN joy[%d] name=%s guid=%s isGC=%d buttons=%d axes=%d hats=%d\\n", i, jn ? jn : "?", gs, (int)SDL_IsGameController(i), j ? SDL_JoystickNumButtons(j) : -1, j ? SDL_JoystickNumAxes(j) : -1, j ? SDL_JoystickNumHats(j) : -1); '
           'char *mp = SDL_GameControllerMappingForGUID(g); fprintf(stdout, "BR2IN joy[%d] mapping=%s\\n", i, mp ? mp : "(none)"); if (mp) SDL_free(mp); } } ')
    print('JOY anclas:', s.count(old))
    s = s.replace(old, new, 1)
    ax = 'else if (e->type == SDL_JOYHATMOTION)'
    axnew = 'else if (e->type == SDL_JOYAXISMOTION && (e->jaxis.value > 20000 || e->jaxis.value < -20000)) fprintf(stdout, "BR2IN axis %d value %d\\n", (int)e->jaxis.axis, (int)e->jaxis.value);\n    ' + ax
    print('AXIS anclas:', s.count(ax))
    s = s.replace(ax, axnew, 1)
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
