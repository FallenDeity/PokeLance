#!/usr/bin/env python3
"""AST-based master code generator for PokeLance sync/async dual-client support.

Reads scripts/gen_scripts/_registry.py (single source of truth) and generates:
  1. pokelance/cache/_async/manager.py   — AsyncCacheManager
  2. pokelance/cache/sync/manager.py    — SyncCacheManager
  3. pokelance/ext/{name}.py             — async extensions
  4. pokelance/ext/sync/{name}.py        — sync extensions

Usage:
    $ python scripts/gen_scripts/generate_all.py                 # regenerate everything
    $ python scripts/gen_scripts/generate_all.py --cache-only    # only cache managers
    $ python scripts/gen_scripts/generate_all.py --ext-only      # only extensions
    $ python scripts/gen_scripts/generate_all.py --check         # CI: verify files are up-to-date
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

# Import the single source of truth
from _registry import EXTENSIONS

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXT_DIR = PROJECT_ROOT / "pokelance" / "ext"
SYNC_EXT_DIR = EXT_DIR / "sync"
ASYNC_CACHE_DIR = PROJECT_ROOT / "pokelance" / "cache" / "_async"
SYNC_CACHE_DIR = PROJECT_ROOT / "pokelance" / "cache" / "sync"

SYNC_EXT_DIR.mkdir(parents=True, exist_ok=True)
ASYNC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
SYNC_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# AST Generation for Cache Managers
# ---------------------------------------------------------------------------

def generate_cache_manager(is_async: bool, output_path: Path) -> str:
    """Generate the full cache manager file using Python AST and ast.unparse()."""
    base_cache_cls = "AsyncBaseCache" if is_async else "SyncBaseCache"
    manager_name = "AsyncCacheManager" if is_async else "SyncCacheManager"
    client_type = "PokeLanceAsyncClient" if is_async else "PokeLanceSyncClient"
    client_import_mod = "pokelance.client.async_client" if is_async else "pokelance.client.sync_client"
    base_cache_import_mod = "pokelance.cache._async.base" if is_async else "pokelance.cache.sync.base"

    body: list[ast.stmt] = [
        # from __future__ import annotations
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
    ]

    if is_async:
        body.append(ast.Import(names=[ast.alias(name="asyncio")]))

    body.extend([
        ast.Import(names=[ast.alias(name="typing", asname="t")]),
        ast.Import(names=[ast.alias(name="attrs")]),
        ast.ImportFrom(module="pokelance", names=[ast.alias(name="models")], level=0),
        ast.ImportFrom(module="pokelance.cache._base", names=[ast.alias(name="Base")], level=0),
        ast.ImportFrom(module=base_cache_import_mod, names=[ast.alias(name=base_cache_cls)], level=0),
        ast.ImportFrom(module="pokelance.http.endpoints", names=[ast.alias(name="Route")], level=0),
        # if t.TYPE_CHECKING:
        ast.If(
            test=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="TYPE_CHECKING", ctx=ast.Load()),
            body=[
                ast.ImportFrom(module=client_import_mod, names=[ast.alias(name=client_type)], level=0),
            ],
            orelse=[],
        ),
        # __all__ = (...)
        ast.Assign(
            targets=[ast.Name(id="__all__", ctx=ast.Store())],
            value=ast.Tuple(
                elts=[ast.Constant(value=manager_name), ast.Constant(value="Base")],
                ctx=ast.Load(),
            ),
        ),
    ])

    attrs_define = ast.Call(
        func=ast.Attribute(value=ast.Name(id="attrs", ctx=ast.Load()), attr="define", ctx=ast.Load()),
        args=[],
        keywords=[
            ast.keyword(arg="slots", value=ast.Constant(value=True)),
            ast.keyword(arg="kw_only", value=ast.Constant(value=True)),
        ],
    )

    # Per-extension classes (Berry, Contest, etc.)
    for spec in EXTENSIONS:
        class_body: list[ast.stmt] = [
            ast.Expr(value=ast.Constant(value=f"Cache aggregate for {spec.name.lower()} endpoints.")),
            # max_size: int = 100
            ast.AnnAssign(
                target=ast.Name(id="max_size", ctx=ast.Store()),
                annotation=ast.Name(id="int", ctx=ast.Load()),
                value=ast.Constant(value=100),
                simple=1,
            ),
        ]

        for cat in spec.categories:
            model_name = cat.model.__name__
            # Type annotation: base_cache_cls[Route, models.Model] or base_cache_cls[Route, t.Sequence[models.Model]]
            model_subscript = (
                ast.Subscript(
                    value=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="Sequence", ctx=ast.Load()),
                    slice=ast.Attribute(value=ast.Name(id="models", ctx=ast.Load()), attr=model_name, ctx=ast.Load()),
                    ctx=ast.Load(),
                )
                if cat.is_list
                else ast.Attribute(value=ast.Name(id="models", ctx=ast.Load()), attr=model_name, ctx=ast.Load())
            )

            field_annotation = ast.Subscript(
                value=ast.Name(id=base_cache_cls, ctx=ast.Load()),
                slice=ast.Tuple(
                    elts=[
                        ast.Name(id="Route", ctx=ast.Load()),
                        model_subscript,
                    ],
                    ctx=ast.Load(),
                ),
                ctx=ast.Load(),
            )

            # factory=lambda: base_cache_cls(...)
            cache_call_keywords = [
                ast.keyword(
                    arg="model",
                    value=ast.Attribute(value=ast.Name(id="models", ctx=ast.Load()), attr=model_name, ctx=ast.Load()),
                ),
                ast.keyword(arg="name", value=ast.Constant(value=cat.cache_attr)),
            ]
            if cat.endpoint_key_is_id:
                cache_call_keywords.append(ast.keyword(arg="endpoint_key_is_id", value=ast.Constant(value=True)))
            if cat.url_suffix:
                cache_call_keywords.append(ast.keyword(arg="url_suffix", value=ast.Constant(value=cat.url_suffix)))
            if cat.is_list:
                cache_call_keywords.append(ast.keyword(arg="is_list", value=ast.Constant(value=True)))

            factory_lambda = ast.Lambda(
                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=ast.Call(
                    func=ast.Name(id=base_cache_cls, ctx=ast.Load()),
                    args=[],
                    keywords=cache_call_keywords,
                ),
            )

            class_body.append(
                ast.AnnAssign(
                    target=ast.Name(id=cat.cache_attr, ctx=ast.Store()),
                    annotation=field_annotation,
                    value=ast.Call(
                        func=ast.Attribute(value=ast.Name(id="attrs", ctx=ast.Load()), attr="field", ctx=ast.Load()),
                        args=[],
                        keywords=[ast.keyword(arg="factory", value=factory_lambda)],
                    ),
                    simple=1,
                )
            )

        # wait_until_ready method
        if is_async:
            wait_fn = ast.AsyncFunctionDef(
                name="wait_until_ready",
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg="self")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                returns=ast.Constant(value=None),
                body=[
                    ast.Expr(value=ast.Constant(value="Wait for all sub-caches in this aggregate to be ready.")),
                    # tasks = [cache.wait_until_ready() for cache in self._walk_caches()]
                    ast.Assign(
                        targets=[ast.Name(id="tasks", ctx=ast.Store())],
                        value=ast.ListComp(
                            elt=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="cache", ctx=ast.Load()),
                                    attr="wait_until_ready",
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                            generators=[
                                ast.comprehension(
                                    target=ast.Name(id="cache", ctx=ast.Store()),
                                    iter=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id="self", ctx=ast.Load()),
                                            attr="_walk_caches",
                                            ctx=ast.Load(),
                                        ),
                                        args=[],
                                        keywords=[],
                                    ),
                                    ifs=[],
                                    is_async=0,
                                )
                            ],
                        ),
                    ),
                    # await asyncio.gather(*tasks)
                    ast.Expr(
                        value=ast.Await(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="asyncio", ctx=ast.Load()),
                                    attr="gather",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Starred(value=ast.Name(id="tasks", ctx=ast.Load()), ctx=ast.Load())],
                                keywords=[],
                            )
                        )
                    ),
                ],
                decorator_list=[],
            )
        else:
            wait_fn = ast.FunctionDef(
                name="wait_until_ready",
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg="self")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                returns=ast.Constant(value=None),
                body=[
                    ast.Expr(value=ast.Constant(value="Wait for all sub-caches in this aggregate to be ready.")),
                    # for cache in self._walk_caches(): cache.wait_until_ready()
                    ast.For(
                        target=ast.Name(id="cache", ctx=ast.Store()),
                        iter=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="_walk_caches",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                        body=[
                            ast.Expr(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id="cache", ctx=ast.Load()),
                                        attr="wait_until_ready",
                                        ctx=ast.Load(),
                                    ),
                                    args=[],
                                    keywords=[],
                                )
                            )
                        ],
                        orelse=[],
                    ),
                ],
                decorator_list=[],
            )

        class_body.append(wait_fn)

        base_class_ref = ast.Subscript(
            value=ast.Name(id="Base", ctx=ast.Load()),
            slice=ast.Constant(value=client_type),
            ctx=ast.Load(),
        )

        body.append(
            ast.ClassDef(
                name=spec.name,
                bases=[base_class_ref],
                keywords=[],
                body=class_body,
                decorator_list=[attrs_define],
            )
        )

    # Top-level Manager Class
    manager_body: list[ast.stmt] = [
        ast.Expr(value=ast.Constant(value=f"Top-level {'async' if is_async else 'sync'} cache manager.")),
        # client: PokeLanceAsyncClient / PokeLanceSyncClient
        ast.AnnAssign(
            target=ast.Name(id="client", ctx=ast.Store()),
            annotation=ast.Constant(value=client_type),
            simple=1,
        ),
        # max_size: int = 100
        ast.AnnAssign(
            target=ast.Name(id="max_size", ctx=ast.Store()),
            annotation=ast.Name(id="int", ctx=ast.Load()),
            value=ast.Constant(value=100),
            simple=1,
        ),
    ]

    for spec in EXTENSIONS:
        manager_body.append(
            ast.AnnAssign(
                target=ast.Name(id=spec.name.lower(), ctx=ast.Store()),
                annotation=ast.Name(id=spec.name, ctx=ast.Load()),
                value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="attrs", ctx=ast.Load()), attr="field", ctx=ast.Load()),
                    args=[],
                    keywords=[ast.keyword(arg="factory", value=ast.Name(id=spec.name, ctx=ast.Load()))],
                ),
                simple=1,
            )
        )

    # if t.TYPE_CHECKING: __attrs_attrs__: t.Tuple[attrs.Attribute[t.Any], ...]
    manager_body.append(
        ast.If(
            test=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="TYPE_CHECKING", ctx=ast.Load()),
            body=[
                ast.AnnAssign(
                    target=ast.Name(id="__attrs_attrs__", ctx=ast.Store()),
                    annotation=ast.Subscript(
                        value=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="Tuple", ctx=ast.Load()),
                        slice=ast.Tuple(
                            elts=[
                                ast.Subscript(
                                    value=ast.Attribute(
                                        value=ast.Name(id="attrs", ctx=ast.Load()), attr="Attribute", ctx=ast.Load()
                                    ),
                                    slice=ast.Attribute(
                                        value=ast.Name(id="t", ctx=ast.Load()), attr="Any", ctx=ast.Load()
                                    ),
                                    ctx=ast.Load(),
                                ),
                                ast.Constant(value=Ellipsis),
                            ],
                            ctx=ast.Load(),
                        ),
                        ctx=ast.Load(),
                    ),
                    simple=1,
                )
            ],
            orelse=[],
        )
    )

    # _walk_aggregates
    manager_body.append(
        ast.FunctionDef(
            name="_walk_aggregates",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            returns=ast.Subscript(
                value=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="Iterator", ctx=ast.Load()),
                slice=ast.Subscript(
                    value=ast.Name(id="Base", ctx=ast.Load()),
                    slice=ast.Constant(value=client_type),
                    ctx=ast.Load(),
                ),
                ctx=ast.Load(),
            ),
            body=[
                ast.Expr(value=ast.Constant(value="Yield all child cache aggregates.")),
                ast.For(
                    target=ast.Name(id="obj", ctx=ast.Store()),
                    iter=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="__attrs_attrs__", ctx=ast.Load()),
                    body=[
                        ast.Assign(
                            targets=[ast.Name(id="val", ctx=ast.Store())],
                            value=ast.Call(
                                func=ast.Name(id="getattr", ctx=ast.Load()),
                                args=[
                                    ast.Name(id="self", ctx=ast.Load()),
                                    ast.Attribute(value=ast.Name(id="obj", ctx=ast.Load()), attr="name", ctx=ast.Load()),
                                ],
                                keywords=[],
                            ),
                        ),
                        ast.If(
                            test=ast.Call(
                                func=ast.Name(id="isinstance", ctx=ast.Load()),
                                args=[ast.Name(id="val", ctx=ast.Load()), ast.Name(id="Base", ctx=ast.Load())],
                                keywords=[],
                            ),
                            body=[
                                ast.Expr(value=ast.Yield(value=ast.Name(id="val", ctx=ast.Load())))
                            ],
                            orelse=[],
                        ),
                    ],
                    orelse=[],
                ),
            ],
            decorator_list=[],
        )
    )

    # __attrs_post_init__
    manager_body.append(
        ast.FunctionDef(
            name="__attrs_post_init__",
            args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]),
            returns=ast.Constant(value=None),
            body=[
                ast.For(
                    target=ast.Name(id="aggregate", ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_walk_aggregates", ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    ),
                    body=[
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(value=ast.Name(id="aggregate", ctx=ast.Load()), attr="set_size", ctx=ast.Load()),
                                args=[ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="max_size", ctx=ast.Load())],
                                keywords=[],
                            )
                        ),
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(value=ast.Name(id="aggregate", ctx=ast.Load()), attr="set_client", ctx=ast.Load()),
                                args=[ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="client", ctx=ast.Load())],
                                keywords=[],
                            )
                        ),
                    ],
                    orelse=[],
                )
            ],
            decorator_list=[],
        )
    )

    # set_size
    manager_body.append(
        ast.FunctionDef(
            name="set_size",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self"), ast.arg(arg="max_size", annotation=ast.Name(id="int", ctx=ast.Load()))],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[ast.Constant(value=100)],
            ),
            returns=ast.Constant(value=None),
            body=[
                ast.Assign(
                    targets=[ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="max_size", ctx=ast.Store())],
                    value=ast.Name(id="max_size", ctx=ast.Load()),
                ),
                ast.For(
                    target=ast.Name(id="aggregate", ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_walk_aggregates", ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    ),
                    body=[
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(value=ast.Name(id="aggregate", ctx=ast.Load()), attr="set_size", ctx=ast.Load()),
                                args=[ast.Name(id="max_size", ctx=ast.Load())],
                                keywords=[],
                            )
                        )
                    ],
                    orelse=[],
                ),
            ],
            decorator_list=[],
        )
    )

    # load_documents
    manager_body.append(
        ast.FunctionDef(
            name="load_documents",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(arg="category", annotation=ast.Name(id="str", ctx=ast.Load())),
                    ast.arg(arg="_type", annotation=ast.Name(id="str", ctx=ast.Load())),
                    ast.arg(
                        arg="data",
                        annotation=ast.Subscript(
                            value=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="List", ctx=ast.Load()),
                            slice=ast.Subscript(
                                value=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="Dict", ctx=ast.Load()),
                                slice=ast.Tuple(
                                    elts=[ast.Name(id="str", ctx=ast.Load()), ast.Name(id="str", ctx=ast.Load())],
                                    ctx=ast.Load(),
                                ),
                                ctx=ast.Load(),
                            ),
                            ctx=ast.Load(),
                        ),
                    ),
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            returns=ast.Constant(value=None),
            body=[
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id="getattr", ctx=ast.Load()),
                                args=[
                                    ast.Call(
                                        func=ast.Name(id="getattr", ctx=ast.Load()),
                                        args=[
                                            ast.Name(id="self", ctx=ast.Load()),
                                            ast.Call(
                                                func=ast.Attribute(
                                                    value=ast.Name(id="category", ctx=ast.Load()),
                                                    attr="lower",
                                                    ctx=ast.Load(),
                                                ),
                                                args=[],
                                                keywords=[],
                                            ),
                                        ],
                                        keywords=[],
                                    ),
                                    ast.Name(id="_type", ctx=ast.Load()),
                                ],
                                keywords=[],
                            ),
                            attr="load_documents",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Name(id="data", ctx=ast.Load())],
                        keywords=[],
                    )
                )
            ],
            decorator_list=[],
        )
    )

    # clear
    manager_body.append(
        ast.FunctionDef(
            name="clear",
            args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]),
            returns=ast.Constant(value=None),
            body=[
                ast.For(
                    target=ast.Name(id="aggregate", ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_walk_aggregates", ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    ),
                    body=[
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(value=ast.Name(id="aggregate", ctx=ast.Load()), attr="clear", ctx=ast.Load()),
                                args=[],
                                keywords=[],
                            )
                        )
                    ],
                    orelse=[],
                )
            ],
            decorator_list=[],
        )
    )

    # reset
    manager_body.append(
        ast.FunctionDef(
            name="reset",
            args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]),
            returns=ast.Constant(value=None),
            body=[
                ast.For(
                    target=ast.Name(id="aggregate", ctx=ast.Store()),
                    iter=ast.Call(
                        func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_walk_aggregates", ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    ),
                    body=[
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(value=ast.Name(id="aggregate", ctx=ast.Load()), attr="reset", ctx=ast.Load()),
                                args=[],
                                keywords=[],
                            )
                        )
                    ],
                    orelse=[],
                )
            ],
            decorator_list=[],
        )
    )

    # wait_until_ready
    if is_async:
        manager_body.append(
            ast.AsyncFunctionDef(
                name="wait_until_ready",
                args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]),
                returns=ast.Constant(value=None),
                body=[
                    ast.Expr(value=ast.Constant(value="Wait for all sub-caches in all aggregates to be ready.")),
                    ast.Assign(
                        targets=[ast.Name(id="tasks", ctx=ast.Store())],
                        value=ast.ListComp(
                            elt=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="aggregate", ctx=ast.Load()),
                                    attr="wait_until_ready",
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                            generators=[
                                ast.comprehension(
                                    target=ast.Name(id="aggregate", ctx=ast.Store()),
                                    iter=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id="self", ctx=ast.Load()),
                                            attr="_walk_aggregates",
                                            ctx=ast.Load(),
                                        ),
                                        args=[],
                                        keywords=[],
                                    ),
                                    ifs=[],
                                    is_async=0,
                                )
                            ],
                        ),
                    ),
                    ast.Expr(
                        value=ast.Await(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="asyncio", ctx=ast.Load()),
                                    attr="gather",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Starred(value=ast.Name(id="tasks", ctx=ast.Load()), ctx=ast.Load())],
                                keywords=[],
                            )
                        )
                    ),
                ],
                decorator_list=[],
            )
        )
    else:
        manager_body.append(
            ast.FunctionDef(
                name="wait_until_ready",
                args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]),
                returns=ast.Constant(value=None),
                body=[
                    ast.Expr(value=ast.Constant(value="Wait for all sub-caches in all aggregates to be ready.")),
                    ast.For(
                        target=ast.Name(id="aggregate", ctx=ast.Store()),
                        iter=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="_walk_aggregates",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                        body=[
                            ast.Expr(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id="aggregate", ctx=ast.Load()),
                                        attr="wait_until_ready",
                                        ctx=ast.Load(),
                                    ),
                                    args=[],
                                    keywords=[],
                                )
                            )
                        ],
                        orelse=[],
                    ),
                ],
                decorator_list=[],
            )
        )

    body.append(
        ast.ClassDef(
            name=manager_name,
            bases=[],
            keywords=[],
            body=manager_body,
            decorator_list=[attrs_define],
        )
    )

    module = ast.Module(body=body, type_ignores=[])
    ast.fix_missing_locations(module)
    unparsed = ast.unparse(module)

    # Format header and ensure 2 blank lines before each top-level class
    header = (
        "# AUTO-GENERATED by scripts/gen_scripts/generate_all.py\n"
        "# DO NOT EDIT MANUALLY\n"
        "# Edit scripts/gen_scripts/_registry.py instead.\n\n"
    )
    formatted = header + unparsed.replace("\n@attrs.define", "\n\n\n@attrs.define") + "\n"
    output_path.write_text(formatted, encoding="utf-8")
    return formatted


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PokeLance sync/async code using AST.")
    parser.add_argument("--check", action="store_true", help="Verify files are up-to-date")
    parser.add_argument("--cache-only", action="store_true", help="Only generate cache managers")
    parser.add_argument("--ext-only", action="store_true", help="Only generate extensions")
    parser.add_argument("--async-only", action="store_true", help="Only generate async targets")
    parser.add_argument("--sync-only", action="store_true", help="Only generate sync targets")
    args = parser.parse_args()

    generate_cache = not args.ext_only
    do_async = not args.sync_only
    do_sync = not args.async_only

    all_ok = True

    # 1. Generate cache managers
    if generate_cache:
        if do_async:
            async_manager_path = ASYNC_CACHE_DIR / "manager.py"
            async_manager_content = generate_cache_manager(is_async=True, output_path=async_manager_path)
            if args.check:
                if async_manager_path.read_text(encoding="utf-8") != async_manager_content:
                    print(f"STALE: {async_manager_path}", file=sys.stderr)
                    all_ok = False
            else:
                print(f"Generated (AST): {async_manager_path}")

        if do_sync:
            sync_manager_path = SYNC_CACHE_DIR / "manager.py"
            sync_manager_content = generate_cache_manager(is_async=False, output_path=sync_manager_path)
            if args.check:
                if sync_manager_path.read_text(encoding="utf-8") != sync_manager_content:
                    print(f"STALE: {sync_manager_path}", file=sys.stderr)
                    all_ok = False
            else:
                print(f"Generated (AST): {sync_manager_path}")

    if args.check:
        if all_ok:
            print("All generated files are up-to-date.")
            return 0
        else:
            print("Some generated files are stale. Run without --check to regenerate.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
