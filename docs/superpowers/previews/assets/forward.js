// A page at an old address forwards to the clean one, keeping its query and hash (D160, Q86). The target is the page's
// canonical link; a file, not inline code, because the site's CSP refuses inline scripts (spec seguranca-doacoes, section 8).
location.replace(document.querySelector('link[rel="canonical"]').getAttribute('href') + location.search + location.hash);
