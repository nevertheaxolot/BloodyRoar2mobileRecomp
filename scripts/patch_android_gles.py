import re
p = 'psxrecomp/runtime/src/main.cpp'
s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
if 'SDL_GL_CONTEXT_PROFILE_ES' in s:
    print('GLES: ya parcheado')
else:
    def prof(m):
        i = m.group(1)
        return ('#ifdef __ANDROID__\n' + i + 'SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_ES);\n#else\n' + m.group(0) + '\n#endif')
    def minor(m):
        i = m.group(1)
        return ('#ifdef __ANDROID__\n' + i + 'SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 0);\n#else\n' + m.group(0) + '\n#endif')
    s, a = re.subn(r'([ \t]*)SDL_GL_SetAttribute\(SDL_GL_CONTEXT_PROFILE_MASK,\s*SDL_GL_CONTEXT_PROFILE_CORE\);', prof, s)
    s, b = re.subn(r'([ \t]*)SDL_GL_SetAttribute\(SDL_GL_CONTEXT_MINOR_VERSION,\s*3\);', minor, s)
    open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s)
    print('GLES parches aplicados: perfil=%d minor=%d' % (a, b))
