"""The Apoie button and its modal (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23; D123, D124, D152, D155, D156). site_chrome.py adds
them to the three published pages only when the apoie switch of data/features.json is on for the build; off, the pages carry
none of this.

Every screen text below is the one the maintainer approved, word for word; the values still missing come from the data file
(support_data.py). The project e-mail never appears on the page (D124)."""
from html import escape

import support_data

# The button: a green pill, white "Apoie", a gold treasure chest with a small lock (no heart).
CHEST = ('<svg class="bi-chest" viewBox="0 0 24 24" aria-hidden="true">'
         '<path d="M3.6 10.4V8.6c0-2.3 1.9-4.1 4.2-4.1h8.4c2.3 0 4.2 1.8 4.2 4.1v1.8z" fill="#F9BE2A" stroke="#8A6A00" '
         'stroke-width="1.4" stroke-linejoin="round"/>'
         '<rect x="3.6" y="10.4" width="16.8" height="9.1" rx="1.6" fill="#F9BE2A" stroke="#8A6A00" stroke-width="1.4"/>'
         '<rect x="10.1" y="8.6" width="3.8" height="4.6" rx=".9" fill="#8A6A00"/>'
         '<circle cx="12" cy="10.5" r=".75" fill="#F9BE2A"/></svg>')
GITHUB = ('<svg class="bi-ap-mark" viewBox="0 0 16 16" aria-hidden="true"><path fill="#14202B" d="M8 0c4.42 0 8 3.58 8 8a8.013 '
          '8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 '
          '0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03'
          '-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-'
          '.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 '
          '1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"/></svg>')
COIN = ('<svg class="bi-ap-mark" viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="17" rx="8" ry="3.2" fill="#E9A912" '
        'stroke="#8A6A00" stroke-width="1.3"/><path d="M4 9v8M20 9v8" stroke="#8A6A00" stroke-width="1.3"/>'
        '<ellipse cx="12" cy="9" rx="8" ry="3.2" fill="#F9BE2A" stroke="#8A6A00" stroke-width="1.3"/>'
        '<ellipse cx="12" cy="9" rx="4.2" ry="1.5" fill="none" stroke="#8A6A00" stroke-width="1.1"/></svg>')
PIX = ('<svg class="bi-ap-mark" viewBox="0 0 28 28" aria-hidden="true"><rect width="28" height="28" rx="8" fill="#12803F"/>'
       '<text x="14" y="18.6" text-anchor="middle" font-family="Manrope,system-ui,sans-serif" font-weight="800" font-size="11" '
       'fill="#fff">R$</text></svg>')
CLOSE = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 3.5l9 9M12.5 3.5l-9 9" stroke="currentColor" '
         'stroke-width="1.9" stroke-linecap="round"/></svg>')
BACK = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.9" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')

LEAD = ("O Brasil-Imposto mostra, com dados oficiais e a fonte de cada número, para onde vai o imposto pago no Brasil. É "
        "apartidário e de código aberto. O seu apoio paga duas coisas, e nada além delas: a infraestrutura que mantém os dados "
        "corretos e no ar e o trabalho de quem desenvolve o projeto.")
MONEY_TITLE = "Para onde vai o dinheiro do apoio"
INFRA = ("O custo real de cada mês, que muda de um mês para outro, com a nota de cada gasto: hoje, as ferramentas de inteligência "
         "artificial usadas para coletar e conferir os dados; depois, servidor e banco de dados, quando o site precisar. O site é "
         "hospedado de graça no GitHub Pages. É a primeira coisa paga com o apoio.")
DEVELOPERS = ("Quem entrega trabalho aceito no repositório, inclusive a pessoa mantenedora. O que sobra de cada mês, depois da "
              "infraestrutura, é dividido entre quem contribuiu pelo peso de cada contribuição aceita (1, 2 ou 3, escrito no pull "
              "request antes do merge), e cada pagamento é publicado no livro-caixa.")
MONTH = ["Primeiro, a infraestrutura do mês, pelo custo real, que muda de um mês para outro.",
         "O resto vai para quem contribuiu, inclusive a pessoa mantenedora, dividido pelo peso de cada contribuição aceita no mês "
         "(1, 2 ou 3).",
         "Nas primeiras divisões, contam todas as contribuições aceitas desde o início do projeto, em 25/09/2026, de todas as "
         "pessoas, até esse saldo ser pago; depois, só as do mês.",
         "Num mês sem contribuição aceita, o resto fica guardado para os meses seguintes, e o saldo aparece no livro-caixa."]
PIX_CARD = "Em reais, qualquer valor, com Pix ou cartão, pela vaquinha do Brasil-Imposto."
SPONSORS_CARD = "Em dólar, uma vez pela sua conta do GitHub."
CRYPTO_CARD = "Sete moedas: BTC, ETH, SOL, USDT, USDC, XRP e BNB. Cada endereço é público, com o link do explorador."
CRYPTO_CARD_SOON = "Sete moedas: BTC, ETH, SOL, USDT, USDC, XRP e BNB."
SOON = "Em breve"
OTHER_WAY = "Quer apoiar de outro jeito, ou falar com a gente? Escreva por aqui."
# "Quem recebe" gathers one part per open channel, in this order, joined by "; "
RECEIVES = {"pix": "o Pix e o cartão vão para a Vakinha, que repassa o valor à pessoa mantenedora; cada repasse é publicado no "
                   "livro-caixa do projeto",
            "sponsors": "o GitHub Sponsors paga ao {host}, organização sem fins lucrativos que guarda o dinheiro do projeto e publica "
                        "cada entrada e cada despesa",
            "crypto": "as carteiras de cripto são do projeto e ficam com a pessoa mantenedora"}
BEFORE = [("Quem recebe:", ""),   # filled from RECEIVES, only with a channel open
          ("O que o apoio compra:", " trabalho e infraestrutura. Junto com a doação, você pode pedir pelo \"Fale com a gente\" uma "
           "funcionalidade que ainda não existe; os pedidos entram no planejamento das próximas atualizações. Nenhum apoio muda um "
           "número: todo número vem da fonte oficial, e as regras de neutralidade valem para todos."),
          ("De quem não aceitamos:", " partido, candidato e ocupante de cargo eletivo. Toda fonte acima de 5% da receita do ano é "
           "publicada com o nome."),
          ("", "Tudo o que entra e tudo o que sai é publicado, mês a mês, no livro-caixa do projeto."),
          ("Em reais:", " doação em cripto ou em dólar entra no livro-caixa em reais, pela cotação do dia em que chegou."),
          ("Imposto de renda:", " a doação não é dedutível; o projeto não é uma entidade beneficente.")]
PIX_STEPS = ["Abra a vaquinha do Brasil-Imposto na Vakinha.", "Digite o valor que quiser.",
             "Pague com Pix, pelo app do seu banco, ou com cartão."]
PIX_FACTS = ("A Vakinha recebe a doação e repassa o valor ao projeto. Na tela do seu banco, o Pix aparece para {bank}. A Vakinha fica "
             "com 6,4% mais R$ 0,50 de cada doação, e cada repasse entra no livro-caixa do projeto, com o extrato da Vakinha.")
SPONSORS_STEPS = ["Abra a página do Brasil-Imposto no GitHub Sponsors.", "Escolha um valor, uma vez ou todo mês.",
                  "Pague com a forma de pagamento da sua conta do GitHub."]
SPONSORS_FACTS = ("Em dólar. O GitHub não cobra taxa de quem apoia por uma conta pessoal; o apoio feito por uma organização tem taxa "
                  "de até 6%. O dinheiro vai para o Open Source Collective, que fica com 10% para guardar e prestar contas do "
                  "dinheiro do projeto.")
PICK_NETWORK = "Escolha uma das redes acima ao enviar."
WARNING = ("Confira a rede antes de enviar. Uma moeda enviada por uma rede que não está na lista se perde, e o projeto não consegue "
           "devolver.")
CONTACT_ASK = ("O que você gostaria de ver no Brasil-Imposto? Conte para a gente. Lemos todas as mensagens e usamos as ideias para "
               "planejar as próximas atualizações.")
CONTACT_LGPD = "Seu nome e e-mail servem só para responder você."
CONTACT_SUBJECT = "Brasil-Imposto: mensagem pelo site"
CONTACT_FROM = "Site Brasil-Imposto"
SENDING = "Enviando..."
SENT = "Mensagem enviada. Respondemos pelo e-mail que você informou."
FAILED = "Não foi possível enviar agora. Tente de novo em alguns minutos."
REQUIRED = "Preencha este campo."
BAD_EMAIL = "Informe um e-mail válido."
MIN_SECONDS = 3   # a send faster than this after the view opens is dropped (D124)

BUTTON = (f'<button type="button" class="bi-apoie-btn" aria-haspopup="dialog" aria-expanded="false" aria-controls="bi-apoie">'
          f'{CHEST}<span>Apoie</span></button>')


def _row(group, network, standard):
    name = network["name"] + (f" ({standard})" if standard else "")
    a = group["address"]
    url = network["explorer_url"].replace("{address}", a)
    return (f'<div class="bi-ap-net"><div class="bi-ap-net-name">{escape(name)}</div><code>{escape(a)}</code>'
            f'<div class="bi-ap-net-act"><button type="button" class="bi-ap-copy" data-copy="{escape(a)}">Copiar</button>'
            f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(network["explorer"])}</a></div></div>')


def _nowrap(text):
    """Escaped text in which "Brasil-Imposto" never breaks at its hyphen."""
    return escape(text).replace("Brasil-Imposto", '<span class="bi-ap-nw">Brasil-Imposto</span>')


def _card(icon, title, text, button, go, is_live):
    """A way to support. While its channel is on "soon" the card says "Em breve" and has nothing to click."""
    if not is_live:
        return (f'<div class="bi-ap-card bi-ap-soon">{icon}<h4>{escape(title)} <span class="bi-ap-tag">{SOON}</span></h4>'
                f'<p>{_nowrap(text)}</p></div>')
    return (f'<div class="bi-ap-card">{icon}<h4>{escape(title)}</h4><p>{_nowrap(text)}</p>'
            f'<button type="button" class="bi-ap-cta" data-go="{go}">{escape(button)}</button></div>')


def _field(name, label, control):
    return (f'<div class="bi-ap-field"><label for="bi-ap-{name}">{label}</label>{control}'
            f'<p class="bi-ap-err" id="bi-ap-{name}-err" hidden></p></div>')


def _receives(data):
    """The "Quem recebe" line: one part per open channel, in the order Pix, Sponsors, crypto, joined by "; "."""
    parts = []
    for channel in support_data.CHANNELS:
        if not support_data.live(data, channel):
            continue
        host = data["sponsors"]["fiscal_host"]
        link = (f'<a href="{escape(host["url"])}" target="_blank" rel="noopener">{escape(host["name"])}</a>' if host.get("url")
                else escape(host["name"]))
        parts.append(escape(RECEIVES[channel]).replace("{host}", link))
    return "; ".join(parts) + "." if parts else ""


def modal(data, keyless=False):
    """The modal's markup: the main view, the contact view, and the view of each payment channel that is live. A value still
    null leaves its sentence out (production never shows a missing value). keyless (the staging build) draws the contact form
    without an access key: a send then shows the error line and makes no request."""
    pix_live, sponsors_live, crypto_live = (support_data.live(data, c) for c in support_data.CHANNELS)
    form_key = data["contact_form"].get("access_key")
    contact = bool(form_key) or keyless
    receives = _receives(data)
    before = []
    for k, v in BEFORE:
        if k == "Quem recebe:":
            if receives:   # comes back when a channel goes live
                before.append(f"<li><b>{escape(k)}</b> {receives}</li>")
            continue
        before.append(f"<li><b>{escape(k)}</b>{escape(v)}</li>" if k else f"<li>{escape(v)}</li>")
    box = ('<div class="bi-ap-box"><h4>Como cada mês é dividido</h4><ol>' + "".join(f"<li>{escape(x)}</li>" for x in MONTH)
           + '</ol></div>')
    main = ('<section class="bi-ap-view" data-view="main">'
            '<div class="bi-ap-head"><img src="assets/brand/brasil-imposto-logo.svg" alt="">'
            '<h2 id="bi-ap-title" tabindex="-1">Apoie o Brasil-Imposto</h2></div>'
            f'<p class="bi-ap-lead">{escape(LEAD)}</p>'
            f'<h3>{escape(MONEY_TITLE)}</h3><div class="bi-ap-bar" aria-hidden="true"><i></i><i></i></div>'
            '<div class="bi-ap-cols">'
            f'<div class="bi-ap-col bi-ap-b"><h4>1. Infraestrutura</h4><p>{escape(INFRA)}</p></div>'
            f'<div class="bi-ap-col bi-ap-g"><h4>2. Desenvolvedores</h4><p>{escape(DEVELOPERS)}</p></div></div>'
            '<h3>Como apoiar</h3><div class="bi-ap-cards">'
            + _card(PIX, "Pix", PIX_CARD, "Apoiar com Pix", "pix", pix_live)
            + _card(GITHUB, "GitHub Sponsors", SPONSORS_CARD, "Apoiar pelo GitHub Sponsors", "sponsors", sponsors_live)
            + _card(COIN, "Cripto", CRYPTO_CARD if crypto_live else CRYPTO_CARD_SOON, "Apoiar com cripto", "crypto", crypto_live)
            + '</div>'
            + (f'<div class="bi-ap-other"><p>{escape(OTHER_WAY)}</p>'
               '<button type="button" class="bi-ap-cta" data-go="contact">Fale com a gente</button></div>' if contact else "")
            + box + f'<h3>Antes de apoiar</h3><ul class="bi-ap-list">{"".join(before)}</ul></section>')
    pix = ('<section class="bi-ap-view" data-view="pix" hidden><h2 tabindex="-1">Apoiar com Pix</h2>'
           '<ol class="bi-ap-steps">' + "".join(f"<li>{escape(x)}</li>" for x in PIX_STEPS) + '</ol>'
           f'<p class="bi-ap-facts">{escape(PIX_FACTS).replace("{bank}", escape(data["pix"]["bank_screen_name"] or ""))}</p>'
           f'<a class="bi-ap-cta" href="{escape(data["pix"]["campaign_url"] or "")}" target="_blank" rel="noopener">'
           'Abrir a vaquinha</a></section>') if pix_live else ""
    sponsors = ('<section class="bi-ap-view" data-view="sponsors" hidden><h2 tabindex="-1">Apoiar pelo GitHub Sponsors</h2>'
                '<ol class="bi-ap-steps">' + "".join(f"<li>{escape(x)}</li>" for x in SPONSORS_STEPS) + '</ol>'
                f'<p class="bi-ap-facts">{escape(SPONSORS_FACTS)}</p>'
                f'<a class="bi-ap-cta" href="{escape(data["sponsors"]["sponsors_url"] or "")}" target="_blank" rel="noopener">'
                'Abrir o GitHub Sponsors</a></section>') if sponsors_live else ""
    crypto = ""
    if crypto_live:
        coins = "".join(f'<button type="button" class="bi-ap-coinbtn" data-coin-btn="{c}" aria-pressed="false">{c}</button>'
                        for c in support_data.COINS)
        panels = ""
        for c in support_data.COINS:
            rows = support_data.networks_of(data, c)
            panels += (f'<div class="bi-ap-coin" data-coin="{c}" hidden>' + "".join(_row(*r) for r in rows)
                       + (f'<p class="bi-ap-pick">{escape(PICK_NETWORK)}</p>' if len(rows) > 1 else "") + '</div>')
        crypto = ('<section class="bi-ap-view" data-view="crypto" hidden><h2 tabindex="-1">Apoiar com cripto</h2>'
                  f'<div class="bi-ap-coins">{coins}</div>{panels}<p class="bi-ap-warn">{escape(WARNING)}</p></section>')
    # D124: name, e-mail and message, sent by fetch as JSON to Web3Forms with its public access key, so no e-mail address is
    # ever in the page; a honeypot (botcheck) and a minimum time before sending keep robots out.
    form = ""
    if contact:
        form = ('<section class="bi-ap-view" data-view="contact" hidden><h2 tabindex="-1">Fale com a gente</h2>'
                f'<p>{escape(CONTACT_ASK)}</p>'
                f'<form class="bi-ap-form" novalidate data-endpoint="{support_data.WEB3FORMS}" data-key="{escape(form_key or "")}" '
                f'data-subject="{escape(CONTACT_SUBJECT)}" data-from-name="{escape(CONTACT_FROM)}" '
                f'data-min-ms="{MIN_SECONDS * 1000}" data-sending="{escape(SENDING)}" data-required="{escape(REQUIRED)}" '
                f'data-bad-email="{escape(BAD_EMAIL)}">'
                + _field("name", "Nome", '<input id="bi-ap-name" name="name" autocomplete="name" required aria-describedby="bi-ap-name-err">')
                + _field("email", "E-mail", '<input id="bi-ap-email" name="email" type="email" autocomplete="email" required '
                         'aria-describedby="bi-ap-email-err">')
                + _field("message", "Mensagem", '<textarea id="bi-ap-message" name="message" rows="5" required '
                         'aria-describedby="bi-ap-message-err"></textarea>')
                + '<div class="bi-ap-hp" aria-hidden="true"><input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></div>'
                f'<p class="bi-ap-lgpd">{escape(CONTACT_LGPD)}</p>'
                f'<p class="bi-ap-fail" role="alert" hidden>{escape(FAILED)}</p>'
                '<button type="submit" class="bi-ap-cta">Enviar</button></form>'
                f'<p class="bi-ap-sent" role="status" tabindex="-1" hidden>{escape(SENT)}</p></section>')
    return ('<div class="bi-apoie" id="bi-apoie" role="dialog" aria-modal="true" aria-labelledby="bi-ap-title" hidden>'
            '<div class="bi-ap-backdrop"></div><div class="bi-ap-panel">'
            f'<div class="bi-ap-top"><button type="button" class="bi-ap-back" hidden>{BACK}<span>Voltar</span></button>'
            f'<button type="button" class="bi-ap-x" aria-label="Fechar">{CLOSE}</button></div>'
            f'<div class="bi-ap-body">{main}{pix}{sponsors}{crypto}{form}</div></div></div>')


CSS = """<style id="bi-apoie-css">
/* The Apoie button and its modal (spec apoie): present only when data/support.json has enabled true. */
.bi-end { display: flex; align-items: center; gap: 18px; }
.bi-apoie-btn { display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px 0 10px; border: 0; border-radius: 99px; background: #12803F; color: #fff; font: 800 13px Manrope, system-ui, sans-serif; cursor: pointer; white-space: nowrap; }
.bi-apoie-btn:hover { background: #0E6A33; }
.bi-apoie-btn:focus-visible, .bi-apoie button:focus-visible, .bi-apoie a:focus-visible { outline: 2px solid #1F5FAF; outline-offset: 2px; }
.bi-chest { width: 20px; height: 20px; flex: none; }
.bi-apoie { position: fixed; inset: 0; z-index: 1100; display: flex; align-items: flex-start; justify-content: center; padding: 24px 16px; box-sizing: border-box; font-family: Manrope, system-ui, sans-serif; color: #14202B; }
/* a display rule on a class beats the hidden attribute, so every hidden part of the modal is hidden here on purpose */
.bi-apoie[hidden], .bi-apoie [hidden] { display: none !important; }
.bi-ap-backdrop { position: absolute; inset: 0; background: rgba(20,32,43,.55); }
.bi-ap-panel { position: relative; box-sizing: border-box; width: 100%; max-width: 760px; max-height: calc(100vh - 48px); max-height: calc(100dvh - 48px); overflow-y: auto; overflow-x: hidden; overscroll-behavior: contain; background: #fff; border-radius: 18px; box-shadow: 0 24px 60px rgba(20,32,43,.28); }
/* the bar takes no height: its two buttons float over the panel and stay in place while it scrolls */
.bi-ap-top { position: sticky; top: 0; z-index: 2; height: 0; }
.bi-ap-x { position: absolute; top: 12px; right: 12px; display: inline-flex; align-items: center; justify-content: center; width: 38px; height: 38px; border: 1px solid #E3E7EC; border-radius: 99px; background: #fff; box-shadow: 0 2px 8px rgba(20,32,43,.12); color: #14202B; cursor: pointer; }
.bi-ap-x svg { width: 15px; height: 15px; }
.bi-ap-back { position: absolute; top: 12px; left: 14px; display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 12px 0 8px; border: 1px solid #E3E7EC; border-radius: 99px; background: #fff; color: #14202B; font: 700 13px Manrope, system-ui, sans-serif; cursor: pointer; }
.bi-ap-back svg { width: 14px; height: 14px; }
.bi-ap-body { padding: 22px 28px 28px; }
.bi-ap-view:not([data-view="main"]) { padding-top: 40px; }
.bi-ap-body h2 { margin: 0; font-size: 24px; letter-spacing: -.015em; line-height: 1.2; }
.bi-ap-body h2:focus { outline: none; }
.bi-ap-body h2 + p { margin-top: 10px; }
.bi-ap-body h3 { margin: 26px 0 10px; font-size: 16px; }
.bi-ap-body h4 { margin: 0 0 6px; font-size: 14px; }
.bi-ap-body p, .bi-ap-body li { font-size: 14px; line-height: 1.55; color: #33404C; }
.bi-ap-body p { margin: 0 0 10px; }
.bi-ap-head { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; padding-right: 48px; }
.bi-ap-head img { width: 42px; height: 42px; flex: none; }
.bi-ap-bar { display: flex; gap: 3px; height: 6px; margin: 0 0 12px; }
.bi-ap-bar i { flex: 1; border-radius: 99px; background: #1F5FAF; }
.bi-ap-bar i + i { background: #12803F; }
.bi-ap-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 22px; }
.bi-ap-col h4::before { content: ""; display: inline-block; width: 10px; height: 10px; margin-right: 7px; border-radius: 3px; background: #12803F; vertical-align: -1px; }
.bi-ap-b h4::before { background: #1F5FAF; }
.bi-ap-box { margin: 16px 0 10px; padding: 14px 16px; border: 1px solid #E3E7EC; border-radius: 12px; background: #F6F8FA; }
.bi-ap-box ol, .bi-ap-steps { margin: 0; padding-left: 20px; }
.bi-ap-box li + li, .bi-ap-steps li + li { margin-top: 4px; }
.bi-ap-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.bi-ap-nw { white-space: nowrap; }
.bi-ap-other + .bi-ap-box, .bi-ap-cards + .bi-ap-box { margin-top: 22px; }
.bi-ap-card { display: flex; flex-direction: column; align-items: flex-start; padding: 16px; border: 1px solid #E3E7EC; border-radius: 14px; }
/* the title and its "Em breve" tag share a row that wraps: in a narrow column the tag drops under the title, aligned with it */
.bi-ap-card h4 { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; }
.bi-ap-card .bi-ap-tag { margin-left: 0; }
.bi-ap-card p { flex: 1; }
.bi-ap-mark { width: 28px; height: 28px; margin-bottom: 8px; }
.bi-ap-cta { display: inline-flex; align-items: center; justify-content: center; min-height: 40px; padding: 0 16px; border: 0; border-radius: 99px; background: #12803F; color: #fff; font: 800 13.5px Manrope, system-ui, sans-serif; text-decoration: none; cursor: pointer; text-align: center; }
.bi-ap-cta:hover { background: #0E6A33; }
.bi-ap-cta[disabled] { background: #A8B3BD; cursor: not-allowed; }
.bi-ap-list { margin: 0; padding-left: 18px; }
.bi-ap-list li + li { margin-top: 6px; }
.bi-ap-list a, .bi-ap-net-act a { color: #1F5FAF; font-weight: 700; }
.bi-ap-talk { margin-top: 18px !important; }
.bi-ap-linkbtn { padding: 0; border: 0; background: none; color: #1F5FAF; font: 800 14px Manrope, system-ui, sans-serif; text-decoration: underline; text-underline-offset: 3px; cursor: pointer; }
.bi-ap-steps { margin: 16px 0 12px; }
.bi-ap-facts { margin: 0 0 16px !important; padding: 12px 14px; border-radius: 12px; background: #F6F8FA; }
.bi-ap-coins { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 14px; }
.bi-ap-coinbtn { min-width: 64px; height: 38px; padding: 0 12px; border: 1px solid #D5DBE1; border-radius: 99px; background: #fff; color: #14202B; font: 800 13px "JetBrains Mono", ui-monospace, monospace; cursor: pointer; }
.bi-ap-coinbtn[aria-pressed="true"] { border-color: #12803F; background: #12803F; color: #fff; }
.bi-ap-coin { margin-bottom: 12px; }
.bi-ap-net { padding: 12px 0; border-top: 1px solid #E3E7EC; }
.bi-ap-net:last-of-type { border-bottom: 1px solid #E3E7EC; }
.bi-ap-net-name { font-weight: 800; font-size: 14px; }
.bi-ap-net code { display: block; margin: 6px 0 8px; padding: 8px 10px; border-radius: 8px; background: #F6F8FA; font: 600 12.5px "JetBrains Mono", ui-monospace, monospace; overflow-wrap: anywhere; word-break: break-all; color: #14202B; }
.bi-ap-net-act { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; font-size: 13.5px; }
.bi-ap-copy { height: 32px; padding: 0 14px; border: 1px solid #12803F; border-radius: 99px; background: #fff; color: #12803F; font: 800 13px Manrope, system-ui, sans-serif; cursor: pointer; }
.bi-ap-copy.done { background: #12803F; color: #fff; }
.bi-ap-pick { margin-top: 10px !important; font-size: 13px !important; }
.bi-ap-warn { margin: 6px 0 10px !important; padding: 12px 14px; border-left: 4px solid #C8102E; border-radius: 8px; background: #FDF1F2; color: #6B0F1A !important; }
.bi-ap-form { display: grid; gap: 12px; margin-top: 14px; }
.bi-ap-hp label { display: grid; }
.bi-ap-form input, .bi-ap-form textarea { box-sizing: border-box; width: 100%; padding: 10px 12px; border: 1px solid #C9D1D9; border-radius: 10px; font: 500 14px Manrope, system-ui, sans-serif; color: #14202B; }
.bi-ap-hp { position: absolute !important; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
.bi-ap-tag { display: inline-block; margin-left: 6px; padding: 2px 8px; border-radius: 99px; background: #FFF4D6; color: #7A5A00; font: 800 11px Manrope, system-ui, sans-serif; letter-spacing: .02em; vertical-align: 1px; white-space: nowrap; }
.bi-ap-soon { background: #FAFBFC; }
.bi-ap-other { display: flex; align-items: center; justify-content: space-between; gap: 12px 18px; flex-wrap: wrap; margin: 14px 0 4px; padding: 14px 16px; border-radius: 14px; background: #EAF5EE; border: 1px solid #BFE0CB; }
.bi-ap-other p { margin: 0 !important; flex: 1 1 260px; font-weight: 700; color: #14202B !important; }
.bi-ap-field { display: grid; gap: 5px; }
.bi-ap-field label { font-weight: 700; font-size: 13.5px; }
.bi-ap-err { margin: 0 !important; font-size: 12.5px !important; font-weight: 700; color: #B3261E !important; }
.bi-ap-form [aria-invalid="true"] { border-color: #B3261E; }
.bi-ap-fail { margin: 0 !important; padding: 10px 12px; border-radius: 10px; background: #FDF1F2; color: #6B0F1A !important; font-weight: 700; }
.bi-ap-sent { margin-top: 14px !important; padding: 14px 16px; border-radius: 12px; background: #EAF5EE; color: #0E5A2C !important; font-weight: 700; }
.bi-ap-sent:focus { outline: none; }
.bi-ap-lgpd { font-size: 12.5px !important; color: #5B6773 !important; margin: 0 !important; }
.bi-ap-form .bi-ap-cta { justify-self: start; }
@media (max-width: 820px) {
  .bi-end { gap: 8px; }
  .bi-ap-cards { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .bi-apoie { padding: 8px; }
  .bi-ap-panel { max-height: calc(100vh - 16px); max-height: calc(100dvh - 16px); border-radius: 14px; }
  .bi-ap-body { padding: 18px 16px 22px; }
  .bi-ap-cols { grid-template-columns: 1fr; }
  .bi-ap-cols { gap: 12px; }
  .bi-ap-body h2 { font-size: 21px; }
}
/* up to 380 px the Menu button shows only its icon (its name stays for screen readers), so the header fits at 320 px */
@media (max-width: 380px) {
  .bi-header { padding: 0 10px; gap: 8px; }
  .bi-end { gap: 6px; }
  .bi-menu-btn { padding: 0 10px; }
  .bi-menu-btn span { position: absolute; width: 1px; height: 1px; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  .bi-apoie-btn { padding: 0 12px 0 9px; }
}
</style>"""

# The modal's code. site_chrome.py puts it inside the chrome's own <script id="bi-chrome-js">, the one script the map loader on
# Início runs at once (map_loader.py), so the button works while the map data loads.
SCRIPT = """// The Apoie modal: opens from the header button, one view at a time, closes with the X, Escape or a click outside, and gives the
// focus back to the button.
(function () {
  const root = document.getElementById('bi-apoie'), opener = document.querySelector('.bi-apoie-btn');
  if (!root || !opener) return;
  const panel = root.querySelector('.bi-ap-panel'), back = root.querySelector('.bi-ap-back');
  const views = [...root.querySelectorAll('[data-view]')];
  const show = (name) => {
    views.forEach((v) => { v.hidden = v.dataset.view !== name; });
    back.hidden = name === 'main'; panel.scrollTop = 0;
    const h = root.querySelector(`[data-view="${name}"] h2`); if (h) h.focus({ preventScroll: true });
  };
  const open = () => {
    root.hidden = false; document.documentElement.classList.add('bi-locked'); opener.setAttribute('aria-expanded', 'true'); show('main');
  };
  const close = () => {
    if (root.hidden) return;
    root.hidden = true; document.documentElement.classList.remove('bi-locked'); opener.setAttribute('aria-expanded', 'false'); opener.focus();
  };
  opener.addEventListener('click', open);
  root.querySelector('.bi-ap-x').addEventListener('click', close);
  root.querySelector('.bi-ap-backdrop').addEventListener('click', close);
  back.addEventListener('click', () => show('main'));
  root.addEventListener('click', (e) => { const go = e.target.closest('[data-go]'); if (go) show(go.dataset.go); });
  document.addEventListener('keydown', (e) => {
    if (root.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab') return;  // the focus stays inside the modal
    const f = [...root.querySelectorAll('button, a[href], input, textarea')].filter((x) => !x.disabled && x.getClientRects().length && x.tabIndex >= 0);
    if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  });
  root.querySelectorAll('[data-coin-btn]').forEach((b) => b.addEventListener('click', () => {
    const c = b.dataset.coinBtn;
    root.querySelectorAll('[data-coin-btn]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    root.querySelectorAll('.bi-ap-coin').forEach((p) => { p.hidden = p.dataset.coin !== c; });
  }));
  root.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const text = b.dataset.copy; if (!text) return;
    try { await navigator.clipboard.writeText(text); } catch (_) {
      const r = document.createRange(); r.selectNodeContents(b.closest('.bi-ap-net').querySelector('code'));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand('copy');
    }
    b.classList.add('done'); setTimeout(() => b.classList.remove('done'), 1800);
  }));
  // The contact form (D124): checked here, then sent as JSON to Web3Forms. A checked honeypot or a send faster than the minimum
  // time after the view opens is dropped without a request.
  const form = root.querySelector('.bi-ap-form');
  if (form) {
    const sent = root.querySelector('.bi-ap-sent'), fail = form.querySelector('.bi-ap-fail'), send = form.querySelector('[type="submit"]');
    const label = send.textContent, minMs = Number(form.dataset.minMs), f = form.elements;
    let openedAt = 0;
    const setError = (name, text) => {
      const p = form.querySelector(`#bi-ap-${name}-err`); p.textContent = text || ''; p.hidden = !text;
      if (text) f[name].setAttribute('aria-invalid', 'true'); else f[name].removeAttribute('aria-invalid');
    };
    const reset = () => {
      openedAt = Date.now(); form.hidden = false; sent.hidden = true; fail.hidden = true;
      ['name', 'email', 'message'].forEach((n) => setError(n, ''));
    };
    const done = () => { form.reset(); form.hidden = true; sent.hidden = false; sent.focus({ preventScroll: true }); };
    root.addEventListener('click', (e) => { const go = e.target.closest('[data-go="contact"]'); if (go) reset(); });
    form.addEventListener('submit', (e) => {
      e.preventDefault(); fail.hidden = true;
      const v = { name: f.name.value.trim(), email: f.email.value.trim(), message: f.message.value.trim() };
      const bad = {
        name: v.name ? '' : form.dataset.required,
        email: !v.email ? form.dataset.required : (/^[^@ ]+@[^@ ]+[.][^@ ]{2,}$/.test(v.email) ? '' : form.dataset.badEmail),
        message: v.message ? '' : form.dataset.required,
      };
      Object.entries(bad).forEach(([n, t]) => setError(n, t));
      const first = Object.keys(bad).find((n) => bad[n]);
      if (first) { f[first].focus(); return; }
      if (f.botcheck.checked || Date.now() - openedAt < minMs) { done(); return; }
      send.disabled = true; send.textContent = form.dataset.sending;
      fetch(form.dataset.endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ access_key: form.dataset.key, ...v, subject: form.dataset.subject, from_name: form.dataset.fromName, botcheck: false }),
      }).then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
        .then((j) => { if (j && j.success === true) done(); else throw new Error('not sent'); })
        .catch(() => { fail.hidden = false; })
        .finally(() => { send.disabled = false; send.textContent = label; });
    });
  }
})();
"""


# The staging build draws the contact form even without the access key (spec staging, section 2): there a send shows the error
# line and makes no request. The line goes only into the staging script, and the comment above keeps its wording, so the
# production pages stay byte for byte what main publishes (PR #52).
KEYLESS_ANCHOR = "      if (f.botcheck.checked || Date.now() - openedAt < minMs) { done(); return; }\n"
if SCRIPT.count(KEYLESS_ANCHOR) != 1:
    raise SystemExit("apoie: the contact form's send changed; place the staging line again")
STAGING_SCRIPT = SCRIPT.replace(KEYLESS_ANCHOR, KEYLESS_ANCHOR + "      if (!form.dataset.key) { fail.hidden = false; return; }   // staging without the access key: nothing is sent\n")
