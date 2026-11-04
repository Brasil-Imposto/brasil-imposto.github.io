"""The site's Content Security Policy, one meta for every page (spec seguranca-doacoes, section 8). D219: Uniswap's form, a list
of origins in a page tag and no inline code; style-src, img-src and form-action as Uniswap's apps/web/public/csp.json has them
(read 2026-11-03). Each CDN script is listed by its exact file, the way Uniswap scopes fonts.gstatic.com to one path."""
import features

SCRIPT_FILES = (
    "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js",                         # Como o dinheiro anda
    "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",               # Como o dinheiro anda
)
# a switch's outside scripts are listed only in the builds where the switch is on (data/features.json)
FEATURE_SCRIPTS = {"rede": ("https://cdn.jsdelivr.net/npm/3d-force-graph@1.80.0/dist/3d-force-graph.min.js",)}   # Início, staging
CONNECT = ("https://api.web3forms.com",)   # the contact form; phase 2 adds the public nodes of the donation check
DIRECTIVES = (
    ("default-src", ("'self'",)),
    ("script-src", ("'self'",) + SCRIPT_FILES),
    ("style-src", ("'self'", "'unsafe-inline'")),
    ("font-src", ("'self'",)),
    ("img-src", ("*", "blob:", "data:")),
    ("connect-src", ("'self'",) + CONNECT),
    ("object-src", ("'none'",)),
    ("base-uri", ("'none'",)),
    ("form-action", ("'none'",)),
)


def directives(profile="production"):
    extra = tuple(u for key, urls in FEATURE_SCRIPTS.items() if features.on(key, profile) for u in urls)
    return tuple((name, values + extra if name == "script-src" else values) for name, values in DIRECTIVES)


def meta(profile="production"):
    policy = "; ".join(f"{name} {' '.join(values)}" for name, values in directives(profile))
    return f'<meta http-equiv="Content-Security-Policy" content="{policy}">'


META = meta("production")
