#!/usr/bin/env python3
"""Render index.html from works.json.

Run from anywhere:  python3 tools/build.py
The first work becomes the large piece, the next two the pair, the rest the
row of smaller frames. Codes and numbers in works.json are the words the door
and the hall answer to.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
         'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
         'nineteen', 'twenty']
FONTS = ('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:wght@500;600'
         '&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap')
ARROW = ('<svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M7 17L17 7"></path><path d="M8 7h9v9"></path></svg>')
LOCK = ('<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V7a4 4 0 0 1 8 0v4"></path></svg>')


def E(s):
    return html.escape(str(s), quote=True)


def word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def nice_date(iso):
    d = date.fromisoformat(iso)
    return '%d %s %d' % (d.day, d.strftime('%b'), d.year)


def meta(w):
    return '%s · %s · %s' % (E(w['platform']), E(' + '.join(w['tools'])), nice_date(w['date']))


def frame(w, eager=False):
    return ('<a class="frame" href="%s" target="_blank" rel="noopener">'
            '<img src="%s" alt="%s, front page" width="800" height="600" loading="%s" decoding="async"></a>'
            % (E(w['url']), E(w['shot']), E(w['title']), 'eager' if eager else 'lazy'))


def hero(w):
    return '\n'.join([
        '<article class="hero piece" id="%s">' % E(w['id']),
        frame(w, eager=True),
        '<div class="label">',
        '<span class="no-big">No. %02d</span>' % w['no'],
        '<h2>%s</h2>' % E(w['title']),
        '<p class="meta">%s</p>' % meta(w),
        '<p class="desc">%s</p>' % E(w['desc']),
        '<a class="open" href="%s" target="_blank" rel="noopener">Open the work%s</a>' % (E(w['url']), ARROW),
        '</div>',
        '</article>'])


def piece(w, with_desc, eager=False):
    parts = [
        '<article class="piece" id="%s">' % E(w['id']),
        frame(w, eager),
        '<div class="plabel">',
        '<span class="no">%02d</span>' % w['no'],
        '<h3>%s</h3>' % E(w['title']),
        '<p class="meta">%s</p>' % meta(w),
    ]
    if with_desc:
        parts.append('<p class="desc">%s</p>' % E(w['desc']))
    parts += ['</div>', '</article>']
    return '\n'.join(parts)


def key_row(no, code, name):
    return ('<div class="krow"><span class="kno">%s</span><span class="kcode">%s</span><span class="kname">%s</span></div>'
            % (no, E(code), E(name)))


def build():
    data = json.load(open(os.path.join(ROOT, 'works.json'), encoding='utf-8'))
    site, works, storage = data['site'], data['works'], data.get('storage', [])
    n, s = len(works), len(storage)
    year = site['updated'][:4]
    lede = '%s web pages and artifacts made with Claude and ChatGPT, on view in one dark room.' % word(n).capitalize()
    door_lede = '%s pages made with Claude and ChatGPT, kept in one dark room. Give the word, or walk straight in.' % word(n).capitalize()
    js_data = json.dumps({'github': site['github'],
                          'works': [{k: w[k] for k in ('id', 'no', 'code', 'title', 'url')} for w in works]},
                         ensure_ascii=False).replace('</', '<\\/')
    keys = [key_row('%02d' % w['no'], w['code'], w['short']) for w in works]
    keys += [key_row('', 'WORKS', 'The whole hall'), key_row('', 'GITHUB', 'The repositories')]
    stored = '\n'.join('<li>%s%s</li>' % (LOCK, E(x['title'])) for x in storage)

    page = '\n'.join([
        '<!doctype html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s · %s</title>' % (E(site['title']), E(site['owner'])),
        '<meta name="description" content="%s">' % E(lede),
        '<meta name="theme-color" content="#0F0F0E">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="%s · %s">' % (E(site['title']), E(site['owner'])),
        '<meta property="og:description" content="%s">' % E(lede),
        '<meta property="og:url" content="%s">' % E(site['url']),
        '<meta property="og:image" content="%sassets/og.jpg">' % E(site['url']),
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="%s">' % E(FONTS),
        '<link rel="stylesheet" href="assets/hub.css">',
        '<script>',
        '/* Decide before the first paint whether the door stands in front of the hall. */',
        '(function(){var h=location.hash.slice(1).toLowerCase(),skip=false;'
        'try{skip=localStorage.getItem("hub-door")==="skip";}catch(e){}'
        'if(h==="door"||(!h&&!skip))document.documentElement.classList.add("door-open");})();',
        '</script>',
        '<script src="assets/hub.js" defer></script>',
        '</head>',
        '<body>',
        '<div class="hall" id="hall">',
        '<div class="wrap">',
        '<header class="mast">',
        '<span>%s</span>' % E(site['owner'].upper()),
        '<span>PERMANENT COLLECTION · %s</span>' % year,
        '<nav aria-label="Site">',
        '<button type="button" class="link" id="to-door">DOOR</button>',
        '<a href="%s" target="_blank" rel="noopener">GITHUB%s</a>' % (E(site['github']), ARROW),
        '</nav>',
        '</header>',
        '<section class="intro" id="top">',
        '<p class="eyebrow">CLAUDE · CHATGPT</p>',
        '<h1>%s</h1>' % E(site['title']),
        '<p class="lede">%s</p>' % E(lede),
        '</section>',
        hero(works[0]),
        '<div class="pair">',
        '\n'.join(piece(w, True, eager=True) for w in works[1:3]),
        '</div>',
        '<div class="trip">',
        '\n'.join(piece(w, False) for w in works[3:]),
        '</div>',
        '<footer class="storage">',
        '<div class="storage-row">',
        '<div class="storage-head">',
        '<h2>In storage</h2>',
        '<p>%s works not yet on view.</p>' % word(s).capitalize(),
        '</div>',
        '<ul>',
        stored,
        '</ul>',
        '</div>',
        '<p class="hint">Type DOOR, or 0, anywhere in the hall to return to the entrance. A word such as RRG or 05 finds its piece.</p>',
        '</footer>',
        '</div>',
        '</div>',
        '<div class="door" id="door" role="dialog" aria-modal="true" aria-labelledby="door-title">',
        '<p class="door-behind">Behind this door: the hall itself, blurred until you walk in.</p>',
        '<section class="door-panel">',
        '<div class="door-mast">',
        '<span>%s · %s</span>' % (E(site['owner'].upper()), E(site['title'].upper())),
        '<span class="pill"><span class="dot" aria-hidden="true"></span>%d ON VIEW · %d IN STORAGE</span>' % (n, s),
        '</div>',
        '<div class="door-hero">',
        '<p class="eyebrow gold">AFTER HOURS</p>',
        '<h1 id="door-title">%s</h1>' % E(site['title']),
        '<span class="rule" aria-hidden="true"></span>',
        '<p class="lede">%s</p>' % E(door_lede),
        '</div>',
        '<form class="word" id="door-form" autocomplete="off">',
        '<label for="door-word">THE WORD</label>',
        '<div class="field">',
        '<span class="prompt" aria-hidden="true">&gt;</span>',
        '<input id="door-word" name="word" type="text" placeholder="RRG, 01, WORKS" autocapitalize="characters" autocorrect="off" spellcheck="false" enterkeyhint="go">',
        '<button type="submit" class="key">ENTER</button>',
        '</div>',
        '<p class="said" id="door-said" aria-live="polite"></p>',
        '</form>',
        '<div class="door-actions">',
        '<button type="button" class="enter" id="door-enter">ENTER THE GALLERY<span class="disc" aria-hidden="true">%s</span></button>' % ARROW,
        '<label class="skip"><input type="checkbox" id="door-skip">Skip this door next time on this browser</label>',
        '<p class="note">Deep links such as #works, #rrg or #01 walk past this door. In the hall, type DOOR or 0 to come back.</p>',
        '</div>',
        '<details class="field-key" open>',
        '<summary>FIELD KEY</summary>',
        '<div class="krows">',
        '\n'.join(keys),
        '</div>',
        '</details>',
        '</section>',
        '</div>',
        '<script type="application/json" id="works-data">%s</script>' % js_data,
        '</body>',
        '</html>',
        ''])
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    print('index.html: %d works, %d in storage' % (n, s))


if __name__ == '__main__':
    build()
