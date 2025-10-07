#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DirNT loop-instrumentation pass for C sources (pycparser-based) with auto shims.

What this script does
---------------------
1) Sanitizes CVE-style placeholders:
   - drops lines that are only "..."
   - replaces "...;" with ";"
   - removes single-line "/* ... */"
2) Always runs a C preprocessor with:
   - -nostdinc
   - a temp overlay include dir containing shims (malloc.h, sys/cdefs.h, strings.h, etc.)
   - pycparser's fake libc include dir
   - a set of -D neutralizers for GNU/compiler extensions (__attribute__, typeof, __asm__, _Atomic, __int128, etc.)
3) Parses with pycparser and instruments each while/for/do-while loop by inserting at the
   start of the loop body:
        printf("DirNT State @ line<LINE>: <");
        printf("<var>=<fmt>,", (cast)<var>);
        ...
        printf(">\n");
   Variables chosen are those in-scope at that point that are modified in:
   - the loop condition (enabled by default, per your request),
   - for-loop iteration expression,
   - loop body.
   "Modified" = direct writes to an identifier (ID) via assignment/compound ops or ++/--.
   (We do not lift arr[i]=... to arr, or p->f=... to p, by default.)

Limitations
-----------
- Formatting/comments/macros are not preserved (code is regenerated).
- Heavy macros are preprocessed away.
- Complex types printed conservatively; pointers as %p.

Usage
-----
    pip install pycparser
    python3 dirnt_instrument.py input.c -o output.c
    python3 dirnt_instrument.py input.c --in-place
Options:
    --cpp-path {gcc|clang}
    --cpp-args  (override default preprocessor args)
"""

import argparse
import os
import re
import sys
import tempfile
from typing import Dict, List, Optional, Set, Tuple

import pycparser
from pycparser import c_ast, parse_file
from pycparser.c_generator import CGenerator


# ===================== Sanitizer =====================

_SANITIZE_PATTERNS = [
    (re.compile(r'^\s*\.\.\.\s*$', re.MULTILINE), ''),      # drop lines that are only "..."
    (re.compile(r'\.\.\.\s*;'), ';'),                      # replace "...;" with ";"
    (re.compile(r'^\s*/\*\s*\.\.\.\s*\*/\s*$', re.MULTILINE), ''),  # drop "/* ... */" one-liners
]

def sanitize_to_temp(src_path: str) -> str:
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    for pat, repl in _SANITIZE_PATTERNS:
        code = pat.sub(repl, code)
    dname = os.path.dirname(os.path.abspath(src_path))
    fd, tmp = tempfile.mkstemp(prefix=os.path.splitext(os.path.basename(src_path))[0] + ".san_", suffix=".c", dir=dname)
    os.close(fd)
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(code)
    return tmp


# ===================== Type helpers =====================

def get_decl_base_type(decl: c_ast.Node) -> str:
    """
    Coarse type tag for printf mapping:
    'sint', 'uint', 'float', 'ldouble', 'bool', 'ptr', 'other'
    """
    t = decl.type
    is_ptr = False
    while True:
        if isinstance(t, c_ast.PtrDecl):
            is_ptr = True; t = t.type
        elif isinstance(t, c_ast.ArrayDecl):
            is_ptr = True; t = t.type
        elif isinstance(t, c_ast.TypeDecl):
            baset = t.type; break
        elif isinstance(t, c_ast.Typedef):
            return 'other'
        else:
            return 'other'

    names = getattr(baset, 'names', [])
    if is_ptr: return 'ptr'
    s = ' '.join(names).replace('_Bool', 'bool')
    if 'long double' in s: return 'ldouble'
    if 'double' in s or 'float' in s: return 'float'
    if 'bool' in s: return 'bool'
    if 'unsigned' in s: return 'uint'
    if any(tok in s for tok in ['char', 'short', 'int', 'long']): return 'sint'
    return 'other'

def printf_fmt_for_type_tag(tag: str) -> Tuple[str, Optional[List[str]]]:
    """Return (printf_format, cast_tokens_or_None)."""
    if tag == 'ptr':   return ("%p", ['void', '*'])
    if tag == 'uint':  return ("%llu", ['unsigned', 'long', 'long'])
    if tag == 'sint':  return ("%lld", ['long', 'long'])
    if tag in ('float', 'ldouble'): return ("%f", ['double'])  # cast to double
    if tag == 'bool':  return ("%d", ['int'])
    return ("%p", ['void', '*'])  # fallback


# ===================== Modified write detection =====================

ASSIGN_OPS = {'=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|='}

class LValueWriteCollector(c_ast.NodeVisitor):
    """Collect identifiers directly written via assignment or ++/--."""
    def __init__(self): self.written: Set[str] = set()
    def visit_Assignment(self, node: c_ast.Assignment):
        if node.op in ASSIGN_OPS and isinstance(node.lvalue, c_ast.ID):
            self.written.add(node.lvalue.name)
        self.generic_visit(node)
    def visit_UnaryOp(self, node: c_ast.UnaryOp):
        if node.op in ('p++', 'p--', '++', '--') and isinstance(node.expr, c_ast.ID):
            self.written.add(node.expr.name)
        self.generic_visit(node)


# ===================== Scope stack =====================

class ScopeStack:
    """Stack of name -> (Decl, type_tag) dicts."""
    def __init__(self): self.stack: List[Dict[str, Tuple[c_ast.Decl, str]]] = []
    def push(self): self.stack.append({})
    def pop(self): self.stack.pop()
    def declare(self, decl: c_ast.Decl):
        if decl.name:
            self.stack[-1][decl.name] = (decl, get_decl_base_type(decl))
    def lookup_all(self) -> Dict[str, Tuple[c_ast.Decl, str]]:
        merged: Dict[str, Tuple[c_ast.Decl, str]] = {}
        for frame in self.stack: merged.update(frame)
        return merged


# ===================== Instrumenter =====================

class Instrumenter(c_ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.generator = CGenerator()
        self.did_instrument_any = False
        self._file_scope: Dict[str, Tuple[c_ast.Decl, str]] = {}

    # ---- builders ----
    def _mk_printf_str_only(self, s: str) -> c_ast.FuncCall:
        return c_ast.FuncCall(name=c_ast.ID('printf'),
                              args=c_ast.ExprList([c_ast.Constant('string', f'"{s}"')]))
    def _mk_cast_typename(self, tokens: List[str]) -> c_ast.Typename:
        return c_ast.Typename(
            name=None, quals=[],
            type=c_ast.TypeDecl(declname=None, quals=[], type=c_ast.IdentifierType(tokens))
        )
    def _mk_printf_var(self, varname: str, fmt: str, cast_tokens: Optional[List[str]]) -> c_ast.FuncCall:
        expr: c_ast.Node = c_ast.ID(varname)
        if cast_tokens: expr = c_ast.Cast(to_type=self._mk_cast_typename(cast_tokens), expr=expr)
        return c_ast.FuncCall(
            name=c_ast.ID('printf'),
            args=c_ast.ExprList([
                c_ast.Constant('string', f'"{varname}={fmt},"'),
                expr
            ])
        )
    def _ensure_compound_body(self, stmt: c_ast.Node) -> c_ast.Compound:
        return stmt if isinstance(stmt, c_ast.Compound) else c_ast.Compound(block_items=[stmt])
    def _insert_instrumentation_at_top(self, body: c_ast.Compound, line_no: int, vars_and_tags: List[Tuple[str, str]]):
        prints: List[c_ast.FuncCall] = [self._mk_printf_str_only(f'DirNT State @ line{line_no}: <')]
        for vname, tag in sorted(vars_and_tags, key=lambda x: x[0]):
            fmt, cast_toks = printf_fmt_for_type_tag(tag)
            prints.append(self._mk_printf_var(vname, fmt, cast_toks))
        prints.append(self._mk_printf_str_only('>\\n'))
        body.block_items = (prints + (body.block_items or []))
        self.did_instrument_any = True

    # ---- visitors ----
    def visit_FileAST(self, node: c_ast.FileAST):
        # seed file-scope (globals)
        for ext in node.ext:
            if isinstance(ext, c_ast.Decl) and ext.name and not isinstance(ext.type, c_ast.FuncDecl):
                self._file_scope[ext.name] = (ext, get_decl_base_type(ext))
        for ext in node.ext:
            if isinstance(ext, c_ast.FuncDef):
                self.visit(ext)

    def visit_FuncDef(self, node: c_ast.FuncDef):
        self.scope = ScopeStack()
        self.scope.push()
        # copy globals into bottom frame
        for k, v in self._file_scope.items():
            self.scope.stack[-1][k] = v
        # params
        if node.decl and isinstance(node.decl.type, c_ast.FuncDecl):
            params = node.decl.type.args
            if params and params.params:
                for p in params.params:
                    if isinstance(p, c_ast.Decl): self.scope.declare(p)
        self._visit_block(node.body)

    def _visit_block(self, comp: c_ast.Compound):
        self.scope.push()
        if comp.block_items:
            new_items = []
            for item in comp.block_items:
                if isinstance(item, c_ast.Decl):
                    self.scope.declare(item); new_items.append(item)
                else:
                    instd = self._maybe_instrument_loop(item)
                    if instd is not None: new_items.append(instd)
                    else: self._generic_visit(item); new_items.append(item)
            comp.block_items = new_items
        self.scope.pop()

    def _generic_visit(self, node: c_ast.Node):
        if node is None: return
        if isinstance(node, c_ast.Compound): self._visit_block(node); return
        if isinstance(node, c_ast.If):
            if node.iftrue:
                (self._visit_block(node.iftrue) if isinstance(node.iftrue, c_ast.Compound) else self.visit(node.iftrue))
            if node.iffalse:
                (self._visit_block(node.iffalse) if isinstance(node.iffalse, c_ast.Compound) else self.visit(node.iffalse))
            return
        if isinstance(node, c_ast.Switch):
            if node.stmt:
                (self._visit_block(node.stmt) if isinstance(node.stmt, c_ast.Compound) else self.visit(node.stmt))
            return
        for _, child in node.children():
            if isinstance(child, c_ast.Compound): self._visit_block(child)
            else: self.visit(child)

    def _maybe_instrument_loop(self, node: c_ast.Node) -> Optional[c_ast.Node]:
        if isinstance(node, c_ast.While):   return self._instrument_while(node)
        if isinstance(node, c_ast.For):     return self._instrument_for(node)
        if isinstance(node, c_ast.DoWhile): return self._instrument_dowhile(node)
        return None

    def _collect_writes_in(self, n: Optional[c_ast.Node]) -> Set[str]:
        col = LValueWriteCollector()
        if n is not None: col.visit(n)
        return col.written

    def _current_in_scope(self) -> Dict[str, Tuple[c_ast.Decl, str]]:
        return self.scope.lookup_all()

    def _in_scope_plus_for_init(self, init: Optional[c_ast.Node]) -> Dict[str, Tuple[c_ast.Decl, str]]:
        scope_now = dict(self._current_in_scope())
        if isinstance(init, c_ast.DeclList):
            for d in init.decls:
                if isinstance(d, c_ast.Decl) and d.name:
                    scope_now[d.name] = (d, get_decl_base_type(d))
        elif isinstance(init, c_ast.Decl):
            if init.name:
                scope_now[init.name] = (init, get_decl_base_type(init))
        return scope_now

    def _instrument_while(self, node: c_ast.While) -> c_ast.While:
        body = self._ensure_compound_body(node.stmt)
        inscope = self._current_in_scope()
        written = self._collect_writes_in(node.cond) | self._collect_writes_in(body)
        vars_tags = [(n, inscope[n][1]) for n in written if n in inscope]
        line_no = node.coord.line if node.coord else 0
        self._insert_instrumentation_at_top(body, line_no, vars_tags)
        node.stmt = body
        return node

    def _instrument_for(self, node: c_ast.For) -> c_ast.For:
        body = self._ensure_compound_body(node.stmt)
        inscope = self._in_scope_plus_for_init(node.init)
        written = (self._collect_writes_in(node.init) |
                   self._collect_writes_in(node.cond) |
                   self._collect_writes_in(node.next) |
                   self._collect_writes_in(body))
        vars_tags = [(n, inscope[n][1]) for n in written if n in inscope]
        line_no = node.coord.line if node.coord else 0
        self._insert_instrumentation_at_top(body, line_no, vars_tags)
        node.stmt = body
        return node

    def _instrument_dowhile(self, node: c_ast.DoWhile) -> c_ast.DoWhile:
        body = self._ensure_compound_body(node.stmt)
        inscope = self._current_in_scope()
        written = self._collect_writes_in(body) | self._collect_writes_in(node.cond)
        vars_tags = [(n, inscope[n][1]) for n in written if n in inscope]
        line_no = node.coord.line if node.coord else 0
        self._insert_instrumentation_at_top(body, line_no, vars_tags)
        node.stmt = body
        return node


# ===================== Codegen preamble =====================

TEMPLATE_PREAMBLE = """#include <stdio.h>

/* NOTE:
 * This file was generated by dirnt_instrument.py using pycparser.
 * Original comments/macros/formatting are not preserved.
 */
"""


# ===================== CPP args & shims =====================

def _fake_libc_include_path() -> str:
    return os.path.join(os.path.dirname(pycparser.__file__), 'utils', 'fake_libc_include')

def _write_shim(dirpath: str, relpath: str, content: str):
    full = os.path.join(dirpath, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

#---------------------------------------------------------------

# def create_overlay_shims() -> str:
#     """
#     Create a temporary include dir with minimal shims so -nostdinc works.
#     We provide stddef.h, stdlib.h, malloc.h and a few other common stubs
#     often referenced in CVE corpora. These are deliberately tiny—just
#     enough for pycparser to parse downstream code.
#     """
#     tdir = tempfile.TemporaryDirectory(prefix="dirnt_shims_")
#     d = tdir.name

#     # stddef.h (minimal)
#     _write_shim(d, "stddef.h", r"""#ifndef _STDDEF_H
# #define _STDDEF_H
# typedef unsigned long size_t;
# #ifndef NULL
# #define NULL ((void*)0)
# #endif
# #endif
# """)

#     # stdlib.h (minimal, depends on stddef.h)
#     _write_shim(d, "stdlib.h", r"""#ifndef _STDLIB_H
# #define _STDLIB_H
# #include <stddef.h>
# void *malloc(size_t);
# void free(void *);
# void *calloc(size_t, size_t);
# void *realloc(void *, size_t);
# void abort(void);
# void exit(int);
# int atoi(const char *);
# long strtol(const char *, char **, int);
# #endif
# """)

#     # malloc.h (uses our local stddef.h)
#     _write_shim(d, "malloc.h", r"""#ifndef _MALLOC_H
# #define _MALLOC_H
# #include <stddef.h>
# void *malloc(size_t);
# void free(void *);
# void *calloc(size_t, size_t);
# void *realloc(void *, size_t);
# #endif
# """)

#     # sys/cdefs.h (empty)
#     _write_shim(d, "sys/cdefs.h", r"""#ifndef _SYS_CDEFS_H
# #define _SYS_CDEFS_H
# #endif
# """)

#     # strings.h -> include string.h (fake libc has string.h)
#     _write_shim(d, "strings.h", r"""#ifndef _STRINGS_H
# #define _STRINGS_H
# #include <string.h>
# #endif
# """)

#     # linux/types.h (minimal typedefs occasionally needed)
#     _write_shim(d, "linux/types.h", r"""#ifndef _LINUX_TYPES_H
# #define _LINUX_TYPES_H
# typedef unsigned char u8;
# typedef unsigned short u16;
# typedef unsigned int u32;
# typedef unsigned long long u64;
# #endif
# """)

#     # Keep the TemporaryDirectory alive
#     global _TMP_SHIMS
#     _TMP_SHIMS = tdir
#     return d


def create_overlay_shims() -> str:
    """
    Create a temporary include dir with minimal shims so -nostdinc works.
    Adds stddef.h, stdlib.h, stdio.h, malloc.h, assert.h, sys/cdefs.h,
    strings.h, linux/types.h, sys/types.h, inttypes.h, unistd.h.
    """
    tdir = tempfile.TemporaryDirectory(prefix="dirnt_shims_")
    d = tdir.name

    # stddef.h (minimal)
    _write_shim(d, "stddef.h", r"""#ifndef _STDDEF_H
#define _STDDEF_H
typedef unsigned long size_t;
#ifndef NULL
#define NULL ((void*)0)
#endif
#endif
""")

    # stdlib.h (minimal)
    _write_shim(d, "stdlib.h", r"""#ifndef _STDLIB_H
#define _STDLIB_H
#include <stddef.h>
void *malloc(size_t);
void free(void *);
void *calloc(size_t, size_t);
void *realloc(void *, size_t);
void abort(void);
void exit(int);
int atoi(const char *);
long strtol(const char *, char **, int);
#endif
""")

    # stdio.h (minimal — enough for pycparser & our printf calls)
    _write_shim(d, "stdio.h", r"""#ifndef _STDIO_H
#define _STDIO_H
#include <stddef.h>
typedef struct __dirnt_FILE { int __dummy; } FILE;
int printf(const char *, ...);
int fprintf(FILE *, const char *, ...);
int sprintf(char *, const char *, ...);
#endif
""")

    # malloc.h
    _write_shim(d, "malloc.h", r"""#ifndef _MALLOC_H
#define _MALLOC_H
#include <stddef.h>
void *malloc(size_t);
void free(void *);
void *calloc(size_t, size_t);
void *realloc(void *, size_t);
#endif
""")

    # assert.h (no-op)
    _write_shim(d, "assert.h", r"""#ifndef _ASSERT_H
#define _ASSERT_H
#define assert(x) ((void)0)
#endif
""")

    # sys/cdefs.h (empty)
    _write_shim(d, "sys/cdefs.h", r"""#ifndef _SYS_CDEFS_H
#define _SYS_CDEFS_H
#endif
""")

    # strings.h -> include string.h (fake libc has string.h)
    _write_shim(d, "strings.h", r"""#ifndef _STRINGS_H
#define _STRINGS_H
#include <string.h>
#endif
""")

    # linux/types.h (minimal typedefs)
    _write_shim(d, "linux/types.h", r"""#ifndef _LINUX_TYPES_H
#define _LINUX_TYPES_H
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
#endif
""")

    # sys/types.h (very small set)
    _write_shim(d, "sys/types.h", r"""#ifndef _SYS_TYPES_H
#define _SYS_TYPES_H
typedef unsigned long off_t;
typedef unsigned int  uid_t;
typedef unsigned int  gid_t;
typedef unsigned long size_t;
typedef long          ssize_t;
#endif
""")

    # inttypes.h (print macros minimal)
    _write_shim(d, "inttypes.h", r"""#ifndef _INTTYPES_H
#define _INTTYPES_H
#define PRId64 "lld"
#define PRIu64 "llu"
#endif
""")

    # unistd.h (tiny)
    _write_shim(d, "unistd.h", r"""#ifndef _UNISTD_H
#define _UNISTD_H
typedef long ssize_t;
int close(int);
#endif
""")

    # keep temp dir alive
    global _TMP_SHIMS
    _TMP_SHIMS = tdir
    return d



#---------------------------------------------------------------

def build_default_cpp_args(overlay_dir: str, fake_libc_dir: str) -> List[str]:
    return [
        "-E", "-P",
        "-nostdinc",
        f"-I{overlay_dir}",
        f"-I{fake_libc_dir}",
        # Neutralizers / stubs:
        "-D__attribute__(x)=", "-D__attribute__=", "-D__extension__=",
        "-D__inline=inline", "-D__inline__=inline",
        "-D__restrict=", "-D__restrict__=",
        "-D__asm__(x)=", "-D__asm__=",
        "-Dtypeof(x)=", "-D__typeof__(x)=",
        "-D__volatile__=", "-D_Noreturn=",
        "-D__declspec(x)=", "-D__cdecl=", "-D__stdcall=", "-D__fastcall=",
        "-D_Atomic(x)=x",
        "-D__int128=long long",
        "-D__gnuc_va_list=void*",
        "-D__builtin_va_list=void*",
        "-D__builtin_va_start(a,b)=",
        "-D__builtin_va_end(a)=",
        "-D__aligned__(x)=",
        "-D__alignof__(x)=8",
    ]


# ===================== Main =====================

def main():
    ap = argparse.ArgumentParser(description="DirNT loop instrumentation for C sources (pycparser-based) with auto shims.")
    ap.add_argument("input", help="Input C file")
    ap.add_argument("-o", "--output", help="Output file (default: stdout)")
    ap.add_argument("--in-place", action="store_true", help="Edit the input file in place")
    ap.add_argument("--cpp-path", default="gcc", help="C preprocessor (gcc or clang)")
    ap.add_argument("--cpp-args", nargs="*", default=None,
                    help="Extra/override CPP args. Example: -E -P -nostdinc -I. -DMYDEF=1")
    args = ap.parse_args()

    if args.in_place and args.output:
        print("Choose either --in-place or -o, not both.", file=sys.stderr)
        sys.exit(2)

    sanitized_path = sanitize_to_temp(args.input)

    # Create overlay shims and get fake libc path
    overlay_dir = create_overlay_shims()
    fake_dir = _fake_libc_include_path()

    default_cpp_args = build_default_cpp_args(overlay_dir, fake_dir)
    cpp_args = default_cpp_args if args.cpp_args is None else args.cpp_args

    try:
        ast = parse_file(sanitized_path, use_cpp=True, cpp_path=args.cpp_path, cpp_args=cpp_args)
    except Exception as e:
        print(f"[error] Failed to parse {args.input}: {e}", file=sys.stderr)
        print("[hint] You can pass custom --cpp-args to add -I<dirs> or -D tokens if something else appears.", file=sys.stderr)
        try: os.remove(sanitized_path)
        except Exception: pass
        sys.exit(1)

    inst = Instrumenter()
    inst.visit(ast)

    gen = CGenerator()
    out = TEMPLATE_PREAMBLE + gen.visit(ast) + "\n"

    try:
        if args.in_place:
            with open(args.input, "w", encoding="utf-8") as f: f.write(out)
        elif args.output:
            with open(args.output, "w", encoding="utf-8") as f: f.write(out)
        else:
            sys.stdout.write(out)
    finally:
        try: os.remove(sanitized_path)
        except Exception: pass

if __name__ == "__main__":
    main()

