# SPDX-License-Identifier: GPL-2.0-only
#
# EA SPORTS UFC 3 PS4 Port - Link Modules Script with Legacy CPU Patch Injection
#
# Based on the Bloodborne PC Ivy Bridge patch by T0ug:
#   https://github.com/T0ug/bloodborne_pc_Ivy-Bridge
# and bloodborne_pc by Supermedo (deadinside28):
#   https://github.com/deadinside28/bloodborne_pc
#
# Adapted and developed for EA SPORTS UFC 3 (CUSA06534) by @deanzx06
# with AI-assisted engineering.

"""Link game executable and PRX modules into a single relocatable binary image."""
import collections
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

from cpu_compat import patch_image, patch_libc

DEFAULT_MODULES = (
    'libc.prx',
    'libSceFios2.prx',
)


def module(path):
    path = Path(path)
    data = path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    if data[:4] == b'\x7fELF':
        elf = bytearray(data)
    else:
        from prepare import parse_self, span, unpack
        segments = parse_self(data)[1]
        length = max((span(p) for p in segments), default=0)
        elf = bytearray(length)
        for segment in segments:
            p_offset, p_filesz, offset, filesz = segment[:4]
            elf[p_offset:p_offset + p_filesz] = unpack(data[offset:offset + filesz], p_filesz)
    e_phoff, e_shoff, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack_from('<QQHHHHI', elf, 0x20)
    e_shnum &= 0xffff
    e_shstrndx &= 0xffff
    ph = [dict(zip(('type', 'flags', 'offset', 'vaddr', 'paddr', 'filesz', 'memsz', 'align'),
                   struct.unpack_from('<IIQQQQQQ', elf, e_phoff + idx * e_phentsize)))
          for idx in range(e_phnum)]
    sh = [dict(zip(('name', 'type', 'flags', 'addr', 'offset', 'size', 'link', 'info', 'addralign', 'entsize'),
                   struct.unpack_from('<IIQQQQIIQQ', elf, e_shoff + idx * e_shentsize)))
          for idx in range(e_shnum)]
    strtab = elf[sh[e_shstrndx]['offset']:sh[e_shstrndx]['offset'] + sh[e_shstrndx]['size']]
    for s in sh:
        s['name'] = strtab[s['name']:strtab.find(b'\0', s['name'])].decode()
    symbols, relocs = [], []
    for s in sh:
        if s['type'] in (2, 11):  # SHT_SYMTAB, SHT_DYNSYM
            strtab = elf[sh[s['link']]['offset']:sh[s['link']]['offset'] + sh[s['link']]['size']]
            for idx in range(s['size'] // s['entsize']):
                st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from('<IBBHQQ', elf, s['offset'] + idx * s['entsize'])
                name = strtab[st_name:strtab.find(b'\0', st_name)].decode()
                symbols.append(dict(name=name, type=st_info & 0xf, binding=st_info >> 4,
                                    section=st_shndx, value=st_value, size=st_size))
        elif s['type'] == 4:  # SHT_RELA
            for idx in range(s['size'] // s['entsize']):
                r_offset, r_info, r_addend = struct.unpack_from('<QQq', elf, s['offset'] + idx * s['entsize'])
                relocs.append((r_offset, r_info & 0xffffffff, r_info >> 32, r_addend))
    return dict(file=path.name, elf=elf, ph=ph, sh=sh, symbols=symbols, relocs=relocs, sha256=sha256)


def canonical(name):
    return name.split('#')[0] if name else name


def link(game, out, module_names=DEFAULT_MODULES):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    game = Path(game)
    main = module(game / 'eboot.bin')
    table = []
    for mod_name in module_names:
        mod_path = game / 'sce_module' / mod_name
        if not mod_path.exists():
            mod_path = game / mod_name
        if mod_path.exists():
            table.append(module(mod_path))
        else:
            print(f"WARNING: Module '{mod_name}' not found; skipping.")

    libc = next((m for m in table if m['file'] == 'libc.prx'), None)
    if libc:
        patch_libc(libc, libc['elf'])

    from prepare import nid
    by_nid = collections.defaultdict(list)
    for m in table:
        for s in m['symbols']:
            if s['section'] and s['name']:
                parts = s['name'].split('#')
                if len(parts) == 3:
                    by_nid[(parts[0], parts[2])].append(parts[1])

    cursor = len(main['elf'])
    for m in table:
        cursor = (cursor + 0xffff) & ~0xffff
        m['base'] = cursor
        size = max((p['vaddr'] + p['memsz'] for p in m['ph'] if p['type'] == 1), default=0)
        cursor += size

    image = bytearray(cursor)
    image[:len(main['elf'])] = main['elf']
    segments = []
    for p in main['ph']:
        if p['type'] == 1:
            flags = (4 if p['flags'] & 4 else 0) | (2 if p['flags'] & 2 else 0) | (1 if p['flags'] & 1 else 0)
            segments.append((p['vaddr'], p['memsz'], flags))

    for m in table:
        for p in m['ph']:
            if p['type'] == 1:
                off = m['base'] + p['vaddr']
                image[off:off + p['filesz']] = m['elf'][p['offset']:p['offset'] + p['filesz']]
                flags = (4 if p['flags'] & 4 else 0) | (2 if p['flags'] & 2 else 0) | (1 if p['flags'] & 1 else 0)
                segments.append((off, p['memsz'], flags))

    relocs = []
    for r_offset, r_type, r_sym, r_addend in main['relocs']:
        relocs.append((r_offset, r_type, r_sym, r_addend))

    for m in table:
        for r_offset, r_type, r_sym, r_addend in m['relocs']:
            relocs.append((m['base'] + r_offset, r_type, r_sym, m['base'] + r_addend if r_type == 8 else r_addend))

    fs_patched = 0
    size = len(image)
    for p in segments:
        if p[2] & 1:  # executable segment
            vaddr, filesz = p[0], p[1]
            end = min(vaddr + filesz, size)
            off = vaddr
            while off < end - 8:
                if image[off:off+3] == b'\x64\x48\x8b' or image[off:off+3] == b'\x64\x4c\x8b':
                    image[off] = 0x65  # convert fs: to gs:
                    fs_patched += 1
                off += 1

    entry = next(p['vaddr'] for p in main['ph'] if p['type'] == 1 and p['flags'] & 1)
    flags = 0
    exports = {}
    for m in table:
        for s in m['symbols']:
            if s['section'] and s['name'] and s['binding'] in (1, 2):
                exports[s['name']] = m['base'] + s['value']

    names = [s['name'] for s in main['symbols'] if not s['section'] and s['name']]
    identities = {s['name']: idx for idx, s in enumerate(main['symbols']) if not s['section'] and s['name']}
    names = [canonical(name) for name in names]
    bindings, unresolved = [], []
    for identity, index in identities.items():
        found = exports.get(identity)
        if not found and identity and identity.count('#') == 2:
            parts = identity.split('#')
            candidates = by_nid.get((parts[0], parts[2]), [])
            if len(candidates) == 1:
                found = exports.get(f"{parts[0]}#{candidates[0]}#{parts[2]}")
        if found:
            bindings.append((index, found, 0))
        else:
            unresolved.append(names[index])

    main_tls = next((p for p in main['ph'] if p['type'] == 7), None)
    main_tls_values = (main_tls['vaddr'], main_tls['filesz'], main_tls['memsz'], main_tls['align']) if main_tls else (0, 0, 0, 0)

    procparam = next((p for p in main['ph'] if p['type'] == 0x61000001), None)
    procparam_vaddr = procparam['vaddr'] if procparam else 0

    image, segments, cpu_compat = patch_image(image, segments, main, table, relocs)
    FLAG_LEGACY_CPU_TRANSLATED = 2
    if cpu_compat.get('enabled') and cpu_compat.get('complete'):
        runtime_supports_flag = False
        if os.environ.get('BB_PROBE_LEGACY_FLAG') == '1':
            runtime_supports_flag = True
        else:
            scripts_dir = Path(__file__).resolve().parent
            candidates = [
                scripts_dir.parent / 'bin' / 'sacredfire-game.exe',
                scripts_dir.parent / 'bin' / 'sacredfire-game'
            ]
            found = False
            for candidate in candidates:
                if candidate.exists():
                    found = True
                    try:
                        bin_data = candidate.read_bytes()
                        if b"\x49\x83\xff\x02\x72" not in bin_data:
                            runtime_supports_flag = True
                    except Exception:
                        pass
                    break
            if not found:
                runtime_supports_flag = True
        if runtime_supports_flag:
            flags |= FLAG_LEGACY_CPU_TRANSLATED

    with (out / 'boot-linked.bin').open('wb') as f:
        f.write(struct.pack('<8s6Q', b'BBPROBE5', len(image), entry, len(segments), len(relocs), len(names), flags))
        f.write(struct.pack('<Q', procparam_vaddr))
        f.write(struct.pack('<4Q', *main_tls_values))
        f.write(struct.pack('<Q', len(table)))
        for t in table:
            tls = next((p for p in t['ph'] if p['type'] == 7), None)
            tls_values = (t['base'] + tls['vaddr'], tls['memsz'], tls['filesz']) if tls else (0, 0, 0)
            init_fn = next((s['value'] for s in t['symbols'] if s['name'] == '_init'), 0)
            f.write(struct.pack('<7Q', t['base'], len(t['elf']), t['base'] + init_fn if init_fn else 0,
                                tls_values[0], tls_values[1], tls_values[2], 0))
        f.write(struct.pack('<Q', len(bindings)))
        for binding in bindings:
            f.write(struct.pack('<3Q', *binding))
        for segment in segments:
            f.write(struct.pack('<3Q', *segment))
        for name in names:
            if len(name.encode()) >= 128:
                raise ValueError('name too long')
            f.write(name.encode().ljust(128, b'\0'))
        for relocation in relocs:
            f.write(struct.pack('<QQqq', *relocation))
        f.write(image)

    report = dict(modules=[{k: (hex(v) if k in ('base', 'init') else v) for k, v in t.items() if k in ('file', 'base', 'init')} for t in table],
                  bindings=len(bindings), imports=len(names), fs_loads_patched=fs_patched,
                  main_tls=dict(zip(('vaddr', 'filesz', 'memsz', 'align'), main_tls_values)),
                  unresolved_imports=unresolved, cpu_compat=cpu_compat)
    (out / 'link.json').write_text(json.dumps(report, indent=2) + '\n')

    if cpu_compat.get('enabled'):
        status = "complete" if cpu_compat.get('complete') else "partial"
        print(f"CPU compatibility ({status}): translated {cpu_compat['patched_sites']} instruction sites for legacy CPU; trampolines={cpu_compat['trampoline_bytes']} bytes")
    summary = ', '.join(f"{t['file']}@{t['base']:#x}" for t in table)
    print(f'Linked modules: {summary}; {len(bindings)} native bindings, {len(unresolved)} imports left to the host runtime, '
          f'fs->gs patched={fs_patched}')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('game', type=Path)
    p.add_argument('--out', type=Path, default=Path(__file__).resolve().parent.parent / 'out')
    p.add_argument('--modules', nargs='*', default=list(DEFAULT_MODULES))
    a = p.parse_args()
    link(a.game, a.out, a.modules)
