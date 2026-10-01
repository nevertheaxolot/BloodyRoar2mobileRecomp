p = 'psxrecomp/runtime/src/gpu_gl_renderer.c'
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read().replace('\ufeff', '')
if 'BR2_GLSL_VER' in s:
    print('GLSL: ya parcheado')
else:
    n = s.count('"#version 330\\n"')
    s = s.replace('"#version 330\\n"', 'BR2_GLSL_VER')
    hdr = ('#ifdef __ANDROID__\n'
           '#define BR2_GLSL_VER "#version 300 es\\n" "precision highp float;\\n" "precision highp int;\\n" "precision highp sampler2D;\\n" "precision highp usampler2D;\\n" "precision highp isampler2D;\\n"\n'
           '#else\n'
           '#define BR2_GLSL_VER "#version 330\\n"\n'
           '#endif\n')
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(hdr + s)
    print('GLSL reemplazos:', n)
