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
