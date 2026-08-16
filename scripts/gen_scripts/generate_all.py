#!/usr/bin/env python3
"""AST-based master code generator for PokeLance sync/async dual-client support.

Reads scripts/gen_scripts/_registry.py (single source of truth) and generates:
  1. pokelance/cache/_async/manager.py   — AsyncCacheManager
  2. pokelance/cache/sync/manager.py    — SyncCacheManager
  3. pokelance/ext/_async/{name}.py      — async extensions
  4. pokelance/ext/sync/{name}.py       — sync extensions

Usage:
    $ python scripts/gen_scripts/generate_all.py                 # regenerate everything
    $ python scripts/gen_scripts/generate_all.py --cache-only    # only cache managers
    $ python scripts/gen_scripts/generate_all.py --ext-only      # only extensions
    $ python scripts/gen_scripts/generate_all.py --check         # CI: verify files are up-to-date
"""

from __future__ import annotations

import argparse
import ast
import inspect
import sys
from pathlib import Path

# Import the single source of truth
from _registry import EXTENSIONS, ExtensionSpec

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXT_DIR = PROJECT_ROOT / "pokelance" / "ext"
ASYNC_EXT_DIR = EXT_DIR / "_async"
SYNC_EXT_DIR = EXT_DIR / "sync"
ASYNC_CACHE_DIR = PROJECT_ROOT / "pokelance" / "cache" / "_async"
SYNC_CACHE_DIR = PROJECT_ROOT / "pokelance" / "cache" / "sync"

ASYNC_EXT_DIR.mkdir(parents=True, exist_ok=True)
SYNC_EXT_DIR.mkdir(parents=True, exist_ok=True)
ASYNC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
SYNC_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def format_docstring(doc: str, indent_spaces: int = 4) -> str:
    """Format docstring with proper indentation on multi-line text."""
    lines = doc.strip().split("\n")
    if len(lines) <= 1:
        return doc.strip()
    pad = " " * indent_spaces
    return lines[0] + "\n" + "\n".join((pad + line) if line.strip() else "" for line in lines[1:])


# ---------------------------------------------------------------------------
# AST Generation for Extensions
# ---------------------------------------------------------------------------


def generate_extension(spec: ExtensionSpec, is_async: bool, output_path: Path) -> str:
    """Generate a complete extension module using Python AST."""
    client_type = "PokeLanceAsyncClient" if is_async else "PokeLanceSyncClient"
    client_mod = "pokelance.client.async_client" if is_async else "pokelance.client.sync_client"
    base_ext_cls = "AsyncBaseExtension" if is_async else "SyncBaseExtension"
    base_ext_mod = "pokelance.ext._async._base" if is_async else "pokelance.ext.sync._base"
    cache_manager_mod = "pokelance.cache._async.manager" if is_async else "pokelance.cache.sync.manager"

    # Module imports
    body: list[ast.stmt] = [
        # from __future__ import annotations
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
    ]

    if is_async:
        # import asyncio
        body.append(ast.Import(names=[ast.alias(name="asyncio")]))

    body.extend(
        [
            # import typing as t
            ast.Import(names=[ast.alias(name="typing", asname="t")]),
            # from pokelance.ext.<_async/sync>._base import <AsyncBaseExtension / SyncBaseExtension>
            ast.ImportFrom(
                module=base_ext_mod,
                names=[ast.alias(name=base_ext_cls)],
                level=0,
            ),
            # from pokelance.endpoints import Endpoint
            ast.ImportFrom(
                module="pokelance.endpoints",
                names=[ast.alias(name="Endpoint")],
                level=0,
            ),
            # if t.TYPE_CHECKING: import models, cache aggregate, client and define _Base
            ast.If(
                test=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="TYPE_CHECKING", ctx=ast.Load()),
                body=[
                    ast.ImportFrom(
                        module="pokelance",
                        names=[ast.alias(name="models")],
                        level=0,
                    ),
                    ast.ImportFrom(
                        module=cache_manager_mod,
                        names=[ast.alias(name=spec.name, asname=f"{spec.name}Cache")],
                        level=0,
                    ),
                    ast.ImportFrom(
                        module=client_mod,
                        names=[ast.alias(name=client_type)],
                        level=0,
                    ),
                    ast.Assign(
                        targets=[ast.Name(id="_Base", ctx=ast.Store())],
                        value=ast.Subscript(
                            value=ast.Name(id=base_ext_cls, ctx=ast.Load()),
                            slice=ast.Name(id=f"{spec.name}Cache", ctx=ast.Load()),
                            ctx=ast.Load(),
                        ),
                    ),
                ],
                orelse=[
                    ast.Assign(
                        targets=[ast.Name(id="_Base", ctx=ast.Store())],
                        value=ast.Name(id=base_ext_cls, ctx=ast.Load()),
                    ),
                ],
            ),
            # __all__: tuple[str, ...] = ("setup", spec.name)
            ast.AnnAssign(
                target=ast.Name(id="__all__", ctx=ast.Store()),
                annotation=ast.Subscript(
                    value=ast.Name(id="tuple", ctx=ast.Load()),
                    slice=ast.Tuple(
                        elts=[ast.Name(id="str", ctx=ast.Load()), ast.Constant(value=...)],
                        ctx=ast.Load(),
                    ),
                    ctx=ast.Load(),
                ),
                value=ast.Tuple(
                    elts=[ast.Constant(value="setup"), ast.Constant(value=spec.name)],
                    ctx=ast.Load(),
                ),
                simple=1,
            ),
        ]
    )

    # Extension class docstring
    class_body: list[ast.stmt] = [
        # """Docstring"""
        ast.Expr(value=ast.Constant(value=format_docstring(spec.doc, 4))),
    ]

    # setup() method: pre-loads endpoint metadata into cache using map & zip/items
    routes_dict_keys: list[ast.expr] = []
    routes_dict_values: list[ast.expr] = []
    for cat in spec.categories:
        if cat.endpoint_list is not None:
            routes_dict_keys.append(ast.Constant(value=cat.name))
            routes_dict_values.append(
                ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="Endpoint", ctx=ast.Load()),
                        attr=cat.endpoint_list.__name__,
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=[],
                )
            )

    if routes_dict_keys:
        routes_assign = ast.Assign(
            targets=[ast.Name(id="routes", ctx=ast.Store())],
            value=ast.Dict(keys=routes_dict_keys, values=routes_dict_values),
        )
        if is_async:
            # results = await asyncio.gather(*(self._client.request(r) for r in routes.values()))
            gather_call = ast.Await(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="asyncio", ctx=ast.Load()),
                        attr="gather",
                        ctx=ast.Load(),
                    ),
                    args=[
                        ast.Starred(
                            value=ast.GeneratorExp(
                                elt=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Attribute(
                                            value=ast.Name(id="self", ctx=ast.Load()),
                                            attr="_client",
                                            ctx=ast.Load(),
                                        ),
                                        attr="request",
                                        ctx=ast.Load(),
                                    ),
                                    args=[ast.Name(id="r", ctx=ast.Load())],
                                    keywords=[],
                                ),
                                generators=[
                                    ast.comprehension(
                                        target=ast.Name(id="r", ctx=ast.Store()),
                                        iter=ast.Call(
                                            func=ast.Attribute(
                                                value=ast.Name(id="routes", ctx=ast.Load()),
                                                attr="values",
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
                            ctx=ast.Load(),
                        )
                    ],
                    keywords=[],
                )
            )
            results_assign = ast.Assign(
                targets=[ast.Name(id="results", ctx=ast.Store())],
                value=gather_call,
            )
            # for category, data in zip(routes.keys(), results):
            #     self._cache_manager.load_documents(spec.name, category, data["results"])
            loop = ast.For(
                target=ast.Tuple(
                    elts=[ast.Name(id="category", ctx=ast.Store()), ast.Name(id="data", ctx=ast.Store())],
                    ctx=ast.Store(),
                ),
                iter=ast.Call(
                    func=ast.Name(id="zip", ctx=ast.Load()),
                    args=[
                        ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="routes", ctx=ast.Load()), attr="keys", ctx=ast.Load()
                            ),
                            args=[],
                            keywords=[],
                        ),
                        ast.Name(id="results", ctx=ast.Load()),
                    ],
                    keywords=[],
                ),
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_manager", ctx=ast.Load()
                                ),
                                attr="load_documents",
                                ctx=ast.Load(),
                            ),
                            args=[
                                ast.Constant(value=spec.name),
                                ast.Name(id="category", ctx=ast.Load()),
                                ast.Subscript(
                                    value=ast.Name(id="data", ctx=ast.Load()),
                                    slice=ast.Constant(value="results"),
                                    ctx=ast.Load(),
                                ),
                            ],
                            keywords=[],
                        )
                    )
                ],
                orelse=[],
            )
            setup_stmts = [routes_assign, results_assign, loop]
        else:
            # for category, route in routes.items():
            #     data = self._client.request(route)
            #     self._cache_manager.load_documents(spec.name, category, data["results"])
            loop = ast.For(
                target=ast.Tuple(
                    elts=[ast.Name(id="category", ctx=ast.Store()), ast.Name(id="route", ctx=ast.Store())],
                    ctx=ast.Store(),
                ),
                iter=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="routes", ctx=ast.Load()), attr="items", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                ),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id="data", ctx=ast.Store())],
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()), attr="_client", ctx=ast.Load()
                                ),
                                attr="request",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Name(id="route", ctx=ast.Load())],
                            keywords=[],
                        ),
                    ),
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_manager", ctx=ast.Load()
                                ),
                                attr="load_documents",
                                ctx=ast.Load(),
                            ),
                            args=[
                                ast.Constant(value=spec.name),
                                ast.Name(id="category", ctx=ast.Load()),
                                ast.Subscript(
                                    value=ast.Name(id="data", ctx=ast.Load()),
                                    slice=ast.Constant(value="results"),
                                    ctx=ast.Load(),
                                ),
                            ],
                            keywords=[],
                        )
                    ),
                ],
                orelse=[],
            )
            setup_stmts = [routes_assign, loop]
    else:
        setup_stmts = []

    # Mark non-list categories as ready since they have no list-endpoint to load
    for cat in spec.categories:
        if cat.endpoint_list is None:
            setup_stmts.append(
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()),
                                    attr="_cache_group",
                                    ctx=ast.Load(),
                                ),
                                attr=cat.cache_attr,
                                ctx=ast.Load(),
                            ),
                            attr="set_ready",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    )
                )
            )

    if not setup_stmts:
        setup_stmts = [ast.Pass()]

    # Attach setup() to class
    if is_async:
        class_body.append(
            ast.AsyncFunctionDef(
                name="setup",
                args=ast.arguments(
                    posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                returns=ast.Constant(value=None),
                body=setup_stmts,
                decorator_list=[],
            )
        )
    else:
        class_body.append(
            ast.FunctionDef(
                name="setup",
                args=ast.arguments(
                    posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                returns=ast.Constant(value=None),
                body=setup_stmts,
                decorator_list=[],
            )
        )

    # Per-category get_* and fetch_* methods
    for cat in spec.categories:
        model_name = cat.model.__name__
        model_ref = ast.Attribute(value=ast.Name(id="models", ctx=ast.Load()), attr=model_name, ctx=ast.Load())

        # Inspect endpoint signature to determine parameter types
        sig = inspect.signature(cat.endpoint)
        params = list(sig.parameters.values())

        if len(params) == 0:
            # 0-argument endpoint (e.g. get_api_metadata)
            method_args = [ast.arg(arg="self")]
            route_call_args: list[ast.expr] = []
            has_validate = False
            get_doc_params = ""
            fetch_doc_params = ""
        else:
            p = params[0]
            is_id_only = cat.endpoint_key_is_id or p.annotation is int or p.name in ("id", "id_")
            param_name = "id" if is_id_only else "name"
            param_type_annot = (
                ast.Name(id="int", ctx=ast.Load())
                if is_id_only
                else ast.BinOp(
                    left=ast.Name(id="str", ctx=ast.Load()),
                    op=ast.BitOr(),
                    right=ast.Name(id="int", ctx=ast.Load()),
                )
            )
            method_args = [ast.arg(arg="self"), ast.arg(arg=param_name, annotation=param_type_annot)]
            route_call_args = [ast.Name(id=param_name, ctx=ast.Load())]
            has_validate = True
            doc_type_str = "int" if is_id_only else "str | int"
            doc_desc_str = "The resource id." if is_id_only else "The name or id."
            get_doc_params = f"Parameters\n----------\n{param_name} : {doc_type_str}\n    {doc_desc_str}\n\n"
            fetch_doc_params = f"Parameters\n----------\n{param_name} : {doc_type_str}\n    {doc_desc_str}\n\n"

        # Return type: models.Model | None or list[models.Model] | None
        ret_type_annot = ast.BinOp(
            left=(
                ast.Subscript(
                    value=ast.Name(id="list", ctx=ast.Load()),
                    slice=model_ref,
                    ctx=ast.Load(),
                )
                if cat.is_list
                else model_ref
            ),
            op=ast.BitOr(),
            right=ast.Constant(value=None),
        )

        get_doc_str = format_docstring(
            f"Gets a {cat.name.replace('_', ' ')} from the cache.\n\n"
            f"{get_doc_params}"
            f"Returns\n"
            f"-------\n"
            f"{'list[models.' + model_name + '] | None' if cat.is_list else 'models.' + model_name + ' | None'}\n"
            f"    The cached model or None.",
            8,
        )

        # Method body for get_<category>()
        get_body: list[ast.stmt] = [
            # Docstring
            ast.Expr(value=ast.Constant(value=get_doc_str)),
            # route = Endpoint.<endpoint_fn>(*args)
            ast.Assign(
                targets=[ast.Name(id="route", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="Endpoint", ctx=ast.Load()),
                        attr=cat.endpoint.__name__,
                        ctx=ast.Load(),
                    ),
                    args=route_call_args,
                    keywords=[],
                ),
            ),
        ]

        if has_validate:
            # self._validate_resource(self._cache_group.<attr>, <param>, route)
            get_body.append(
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()), attr="_validate_resource", ctx=ast.Load()
                        ),
                        args=[
                            ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_group", ctx=ast.Load()
                                ),
                                attr=cat.cache_attr,
                                ctx=ast.Load(),
                            ),
                            route_call_args[0],
                            ast.Name(id="route", ctx=ast.Load()),
                        ],
                        keywords=[],
                    )
                )
            )

        # return self._cache_group.<attr>.get(route, None)
        get_body.append(
            ast.Return(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_group", ctx=ast.Load()
                            ),
                            attr=cat.cache_attr,
                            ctx=ast.Load(),
                        ),
                        attr="get",
                        ctx=ast.Load(),
                    ),
                    args=[ast.Name(id="route", ctx=ast.Load()), ast.Constant(value=None)],
                    keywords=[],
                )
            )
        )

        class_body.append(
            ast.FunctionDef(
                name=f"get_{cat.name}",
                args=ast.arguments(
                    posonlyargs=[],
                    args=method_args,
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                returns=ret_type_annot,
                body=get_body,
                decorator_list=[],
            )
        )

        # Method body for fetch_<category>()
        fetch_ret_type_annot = (
            ast.Subscript(
                value=ast.Name(id="list", ctx=ast.Load()),
                slice=model_ref,
                ctx=ast.Load(),
            )
            if cat.is_list
            else model_ref
        )

        # (await) self._client.request(route)
        req_call = ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_client", ctx=ast.Load()),
                attr="request",
                ctx=ast.Load(),
            ),
            args=[ast.Name(id="route", ctx=ast.Load())],
            keywords=[],
        )
        fetch_data_expr = ast.Await(value=req_call) if is_async else req_call

        # self._cache_group.<attr>.from_payload(data)
        from_payload_call = ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(
                    value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_group", ctx=ast.Load()),
                    attr=cat.cache_attr,
                    ctx=ast.Load(),
                ),
                attr="from_payload",
                ctx=ast.Load(),
            ),
            args=[ast.Name(id="data", ctx=ast.Load())],
            keywords=[],
        )

        # self._cache_group.<attr>.setdefault(route, self._cache_group.<attr>.from_payload(data))
        setdefault_call = ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(
                    value=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_group", ctx=ast.Load()),
                    attr=cat.cache_attr,
                    ctx=ast.Load(),
                ),
                attr="setdefault",
                ctx=ast.Load(),
            ),
            args=[ast.Name(id="route", ctx=ast.Load()), from_payload_call],
            keywords=[],
        )

        fetch_doc_str = format_docstring(
            f"Fetches a {cat.name.replace('_', ' ')} from the API.\n\n"
            f"{fetch_doc_params}"
            f"Returns\n"
            f"-------\n"
            f"{'list[models.' + model_name + ']' if cat.is_list else 'models.' + model_name}\n"
            f"    The fetched model.",
            8,
        )

        fetch_body: list[ast.stmt] = [
            # Docstring
            ast.Expr(value=ast.Constant(value=fetch_doc_str)),
            # route = Endpoint.<endpoint_fn>(*args)
            ast.Assign(
                targets=[ast.Name(id="route", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="Endpoint", ctx=ast.Load()),
                        attr=cat.endpoint.__name__,
                        ctx=ast.Load(),
                    ),
                    args=route_call_args,
                    keywords=[],
                ),
            ),
        ]

        if has_validate:
            fetch_body.append(
                ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()), attr="_validate_resource", ctx=ast.Load()
                        ),
                        args=[
                            ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()), attr="_cache_group", ctx=ast.Load()
                                ),
                                attr=cat.cache_attr,
                                ctx=ast.Load(),
                            ),
                            route_call_args[0],
                            ast.Name(id="route", ctx=ast.Load()),
                        ],
                        keywords=[],
                    )
                )
            )

        # data = (await) self._client.request(route)
        fetch_body.append(
            ast.Assign(
                targets=[ast.Name(id="data", ctx=ast.Store())],
                value=fetch_data_expr,
            )
        )
        # return self._cache_group.<attr>.setdefault(route, self._cache_group.<attr>.from_payload(data))
        fetch_body.append(ast.Return(value=setdefault_call))

        if is_async:
            class_body.append(
                ast.AsyncFunctionDef(
                    name=f"fetch_{cat.name}",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=method_args,
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    returns=fetch_ret_type_annot,
                    body=fetch_body,
                    decorator_list=[],
                )
            )
        else:
            class_body.append(
                ast.FunctionDef(
                    name=f"fetch_{cat.name}",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=method_args,
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    returns=fetch_ret_type_annot,
                    body=fetch_body,
                    decorator_list=[],
                )
            )

    # Class definition: class <SpecName>(_Base):
    body.append(
        ast.ClassDef(
            name=spec.name,
            bases=[ast.Name(id="_Base", ctx=ast.Load())],
            keywords=[],
            body=class_body,
            decorator_list=[],
        )
    )

    # Module-level setup(lance) function: lance.add_extension(spec.module_name, <SpecName>(lance.http))
    module_setup_fn = ast.FunctionDef(
        name="setup",
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="lance", annotation=ast.Constant(value=client_type))],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        returns=ast.Constant(value=None),
        body=[
            ast.Expr(value=ast.Constant(value=format_docstring(f"Sets up the {spec.module_name} extension.", 4))),
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="lance", ctx=ast.Load()), attr="add_extension", ctx=ast.Load()
                    ),
                    args=[
                        ast.Constant(value=spec.module_name),
                        ast.Call(
                            func=ast.Name(id=spec.name, ctx=ast.Load()),
                            args=[
                                ast.Attribute(
                                    value=ast.Name(id="lance", ctx=ast.Load()),
                                    attr="http",
                                    ctx=ast.Load(),
                                )
                            ],
                            keywords=[],
                        ),
                    ],
                    keywords=[],
                )
            ),
        ],
        decorator_list=[],
    )
    body.append(module_setup_fn)

    # Fix AST locations and unparse into Python source code
    module = ast.Module(body=body, type_ignores=[])
    ast.fix_missing_locations(module)
    unparsed = ast.unparse(module)

    # Clean blank line before __all__
    unparsed = unparsed.replace("\n__all__", "\n\n__all__")

    header = (
        "# AUTO-GENERATED by scripts/gen_scripts/generate_all.py\n"
        "# DO NOT EDIT MANUALLY\n"
        "# Edit scripts/gen_scripts/_registry.py instead.\n\n"
    )
    formatted = header + unparsed + "\n"
    output_path.write_text(formatted, encoding="utf-8")
    return formatted


# ---------------------------------------------------------------------------
# AST Generation for Cache Managers
# ---------------------------------------------------------------------------


def generate_cache_manager(is_async: bool, output_path: Path) -> str:
    """Generate the full cache manager file using Python AST and ast.unparse()."""
    base_cache_cls = "AsyncCache" if is_async else "SyncCache"
    base_agg_cls = "AsyncCacheGroup" if is_async else "SyncCacheGroup"
    manager_name = "AsyncCacheManager" if is_async else "SyncCacheManager"
    client_type = "PokeLanceAsyncClient" if is_async else "PokeLanceSyncClient"
    client_import_mod = "pokelance.client.async_client" if is_async else "pokelance.client.sync_client"
    base_cache_import_mod = "pokelance.cache._async.base" if is_async else "pokelance.cache.sync.base"

    # Module imports
    body: list[ast.stmt] = [
        # from __future__ import annotations
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
    ]

    if is_async:
        # import asyncio
        body.append(ast.Import(names=[ast.alias(name="asyncio")]))

    body.extend(
        [
            # import collections.abc as cabc
            ast.Import(names=[ast.alias(name="collections.abc", asname="cabc")]),
            # import typing as t
            ast.Import(names=[ast.alias(name="typing", asname="t")]),
            # import attrs
            ast.Import(names=[ast.alias(name="attrs")]),
            # from pokelance import models
            ast.ImportFrom(module="pokelance", names=[ast.alias(name="models")], level=0),
            # from pokelance.cache.<_async/sync>.base import <AsyncCache/SyncCache>, <AsyncCacheGroup/SyncCacheGroup>
            ast.ImportFrom(
                module=base_cache_import_mod,
                names=[ast.alias(name=base_cache_cls), ast.alias(name=base_agg_cls)],
                level=0,
            ),
            # from pokelance.cache._base import BaseCacheManager, CacheStats
            ast.ImportFrom(
                module="pokelance.cache._base",
                names=[ast.alias(name="BaseCacheManager"), ast.alias(name="CacheStats")],
                level=0,
            ),
            # from pokelance.endpoints import Route
            ast.ImportFrom(module="pokelance.endpoints", names=[ast.alias(name="Route")], level=0),
            # if t.TYPE_CHECKING: import client type and type _BaseCacheManager
            ast.If(
                test=ast.Attribute(value=ast.Name(id="t", ctx=ast.Load()), attr="TYPE_CHECKING", ctx=ast.Load()),
                body=[
                    ast.ImportFrom(module=client_import_mod, names=[ast.alias(name=client_type)], level=0),
                    ast.Assign(
                        targets=[ast.Name(id="_BaseCacheManager", ctx=ast.Store())],
                        value=ast.Subscript(
                            value=ast.Name(id="BaseCacheManager", ctx=ast.Load()),
                            slice=ast.Tuple(
                                elts=[
                                    ast.Name(id=client_type, ctx=ast.Load()),
                                    ast.Name(id=base_agg_cls, ctx=ast.Load()),
                                ],
                                ctx=ast.Load(),
                            ),
                            ctx=ast.Load(),
                        ),
                    ),
                ],
                orelse=[
                    ast.Assign(
                        targets=[ast.Name(id="_BaseCacheManager", ctx=ast.Store())],
                        value=ast.Name(id="BaseCacheManager", ctx=ast.Load()),
                    ),
                ],
            ),
            # __all__: tuple[str, ...] = (manager_name, base_agg_cls)
            ast.AnnAssign(
                target=ast.Name(id="__all__", ctx=ast.Store()),
                annotation=ast.Subscript(
                    value=ast.Name(id="tuple", ctx=ast.Load()),
                    slice=ast.Tuple(
                        elts=[ast.Name(id="str", ctx=ast.Load()), ast.Constant(value=...)],
                        ctx=ast.Load(),
                    ),
                    ctx=ast.Load(),
                ),
                value=ast.Tuple(
                    elts=[ast.Constant(value=manager_name), ast.Constant(value=base_agg_cls)],
                    ctx=ast.Load(),
                ),
                simple=1,
            ),
        ]
    )

    # @attrs.define(slots=True, kw_only=True) decorator
    attrs_define = ast.Call(
        func=ast.Attribute(value=ast.Name(id="attrs", ctx=ast.Load()), attr="define", ctx=ast.Load()),
        args=[],
        keywords=[
            ast.keyword(arg="slots", value=ast.Constant(value=True)),
            ast.keyword(arg="kw_only", value=ast.Constant(value=True)),
        ],
    )

    # Per-extension classes (Berry, Contest, Encounter, etc.) inheriting from AsyncCacheGroup / SyncCacheGroup
    for spec in EXTENSIONS:
        class_body: list[ast.stmt] = [
            # Docstring
            ast.Expr(value=ast.Constant(value=f"Cache aggregate for {spec.name.lower()} endpoints.")),
            # max_size: int = 100
            ast.AnnAssign(
                target=ast.Name(id="max_size", ctx=ast.Store()),
                annotation=ast.Name(id="int", ctx=ast.Load()),
                value=ast.Constant(value=100),
                simple=1,
            ),
        ]

        # Field declarations for each endpoint category
        for cat in spec.categories:
            model_name = cat.model.__name__
            # Type annotation: base_cache_cls[Route, models.Model] or base_cache_cls[Route, list[models.Model]]
            model_subscript = (
                ast.Subscript(
                    value=ast.Name(id="list", ctx=ast.Load()),
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

            # Keyword arguments for base cache instantiation
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

            # factory=lambda: base_cache_cls(model=..., name=...)
            factory_lambda = ast.Lambda(
                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=ast.Call(
                    func=ast.Name(id=base_cache_cls, ctx=ast.Load()),
                    args=[],
                    keywords=cache_call_keywords,
                ),
            )

            # <cat.cache_attr>: <field_annotation> = attrs.field(factory=lambda: ...)
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

        # Class definition: class <SpecName>(AsyncCacheGroup / SyncCacheGroup):
        body.append(
            ast.ClassDef(
                name=spec.name,
                bases=[ast.Name(id=base_agg_cls, ctx=ast.Load())],
                keywords=[],
                body=class_body,
                decorator_list=[attrs_define],
            )
        )

    # Top-level Manager Class
    manager_body: list[ast.stmt] = [
        # Docstring
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

    # Aggregate fields on top-level manager
    manager_body.extend(
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
        for spec in EXTENSIONS
    )

    # wait_until_ready for top-level manager
    if is_async:
        manager_body.append(
            ast.AsyncFunctionDef(
                name="wait_until_ready",
                args=ast.arguments(
                    posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                returns=ast.Constant(value=None),
                body=[
                    # Docstring
                    ast.Expr(value=ast.Constant(value="Wait for all sub-caches in all aggregates to be ready.")),
                    # tasks = [aggregate.wait_until_ready() for aggregate in self._walk_aggregates()]
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
        )
    else:
        manager_body.append(
            ast.FunctionDef(
                name="wait_until_ready",
                args=ast.arguments(
                    posonlyargs=[], args=[ast.arg(arg="self")], kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                returns=ast.Constant(value=None),
                body=[
                    # Docstring
                    ast.Expr(value=ast.Constant(value="Wait for all sub-caches in all aggregates to be ready.")),
                    # for aggregate in self._walk_aggregates(): aggregate.wait_until_ready()
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

    # Top-level Manager Class definition
    body.append(
        ast.ClassDef(
            name=manager_name,
            bases=[ast.Name(id="_BaseCacheManager", ctx=ast.Load())],
            keywords=[],
            body=manager_body,
            decorator_list=[attrs_define],
        )
    )

    # Fix AST locations and unparse into Python source code
    module = ast.Module(body=body, type_ignores=[])
    ast.fix_missing_locations(module)
    unparsed = ast.unparse(module)

    # Clean blank line before __all__
    unparsed = unparsed.replace("\n__all__", "\n\n__all__")

    header = (
        "# AUTO-GENERATED by scripts/gen_scripts/generate_all.py\n"
        "# DO NOT EDIT MANUALLY\n"
        "# Edit scripts/gen_scripts/_registry.py instead.\n\n"
    )
    formatted = header + unparsed + "\n"
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
    generate_ext = not args.cache_only
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

    # 2. Generate extensions
    if generate_ext:
        for spec in EXTENSIONS:
            if do_async:
                async_path = ASYNC_EXT_DIR / f"{spec.module_name}.py"
                async_content = generate_extension(spec, is_async=True, output_path=async_path)
                if args.check:
                    if async_path.read_text(encoding="utf-8") != async_content:
                        print(f"STALE: {async_path}", file=sys.stderr)
                        all_ok = False
                else:
                    print(f"Generated (AST): {async_path}")

            if do_sync:
                sync_path = SYNC_EXT_DIR / f"{spec.module_name}.py"
                sync_content = generate_extension(spec, is_async=False, output_path=sync_path)
                if args.check:
                    if sync_path.read_text(encoding="utf-8") != sync_content:
                        print(f"STALE: {sync_path}", file=sys.stderr)
                        all_ok = False
                else:
                    print(f"Generated (AST): {sync_path}")

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
