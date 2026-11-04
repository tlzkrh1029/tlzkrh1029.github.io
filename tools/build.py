#!/usr/bin/env python3
"""Render index.html from works.json.

Run from anywhere:  python3 tools/build.py
The first nine works hang on the wall (slots p1 to p9 in assets/hub.css). The
door is the same wall with the lights out, and the hall is the wall lit, with
the wall texts below it. Codes and numbers in works.json are the words the
door and the hall answer to.
"""
import hashlib
import html
import json
import os
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
         'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
         'nineteen', 'twenty']
FONTS = ('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,wght@0,500;0,600;1,500'
         '&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap')
ARROW = ('<svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M7 17L17 7"></path><path d="M8 7h9v9"></path></svg>')
DOWN = ('<svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 5v14"></path><path d="M6 13l6 6 6-6"></path></svg>')
LOCK = ('<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V7a4 4 0 0 1 8 0v4"></path></svg>')
HANG_SLOTS = 9
SEOUL = timezone(timedelta(hours=9))


def stamp(rel):
    """Add a short content hash to an asset path, so a fresh page never pairs with a stale cached file."""
    with open(os.path.join(ROOT, rel), 'rb') as f:
        return '%s?v=%s' % (rel, hashlib.sha1(f.read()).hexdigest()[:8])


def E(s):
    return html.escape(str(s), quote=True)


def word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def nice_date(iso):
    d = date.fromisoformat(iso)
    return '%d %s %d' % (d.day, d.strftime('%b'), d.year)


def meta(w):
    return '%s · %s · %s' % (E(w['platform']), E(' + '.join(w['tools'])), nice_date(w['date']))


def hang(w, i):
    """One frame on the wall, with its brass plate (number and word; the short title joins on hover)."""
    return ('<a class="hang p%d" id="hang-%s" data-id="%s" href="%s" target="_blank" rel="noopener" '
            'aria-label="%02d %s, opens in a new tab">'
            '<img src="%s" alt="" width="800" height="600" decoding="async"%s>'
            '<span class="tag" aria-hidden="true"><span class="tno">%02d</span><span class="tcode">%s</span>'
            '<span class="ttitle">%s</span>%s</span></a>'
            % (i + 1, E(w['id']), E(w['id']), E(w['url']), w['no'], E(w['title']), E(w['shot']),
               ' fetchpriority="high"' if i == 0 else '', w['no'], E(w['code']), E(w['short']), ARROW))


def wall_text(w):
    """The work's entry in the wall texts below the wall."""
    return '\n'.join([
        '<li class="text" id="text-%s">' % E(w['id']),
        '<span class="tno">%02d</span>' % w['no'],
        '<h3>%s</h3>' % E(w['title']),
        '<p class="meta">%s</p>' % meta(w),
        '<p class="desc">%s</p>' % E(w['desc']),
        '<p class="links"><a class="open" href="%s" target="_blank" rel="noopener">Open the work%s</a>'
        '<span class="word">%s</span></p>' % (E(w['url']), ARROW, E(w['code'])),
        '</li>'])


def challenge_today(site):
    """Tonight's challenge word as of build time (the page recomputes it daily)."""
    today = datetime.now(SEOUL).date()
    words = site['challenges']
    i = (today - date.fromisoformat(site['challenge_epoch'])).days % len(words)
    return words[i], ('%s %d %s %d' % (today.strftime('%a'), today.day, today.strftime('%b'), today.year)).upper()


def build():
    data = json.load(open(os.path.join(ROOT, 'works.json'), encoding='utf-8'))
    site, works, storage = data['site'], data['works'], data.get('storage', [])
    n, s = len(works), len(storage)
    year = site['updated'][:4]
    lede = '%s web pages and artifacts made with Claude and ChatGPT, hung on one wall.' % word(n).capitalize()
    js_data = json.dumps({'github': site['github'],
                          'epoch': site['challenge_epoch'],
                          'challenges': site['challenges'],
                          'works': [{k: w[k] for k in ('id', 'no', 'code', 'title', 'url')} for w in works]},
                         ensure_ascii=False).replace('</', '<\\/')
    stored = '\n'.join('<li>%s%s</li>' % (LOCK, E(x['title'])) for x in storage)
    tonight, today_label = challenge_today(site)
    hangs = '\n'.join(hang(w, i) for i, w in enumerate(works[:HANG_SLOTS]))
    texts = '\n'.join(wall_text(w) for w in works)
    codes = '\n<span aria-hidden="true">·</span>\n'.join(
        '<button type="button" class="code" data-word="%s">%s</button>' % (E(w['code']), E(w['code'])) for w in works)

    page = '\n'.join([
        '<!doctype html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s · %s</title>' % (E(site['title']), E(site['owner'])),
        '<meta name="description" content="%s">' % E(lede),
        '<meta name="theme-color" content="#0B0B0A">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="%s · %s">' % (E(site['title']), E(site['owner'])),
        '<meta property="og:description" content="%s">' % E(lede),
        '<meta property="og:url" content="%s">' % E(site['url']),
        '<meta property="og:image" content="%s%s">' % (E(site['url']), stamp('assets/og.jpg')),
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="%s">' % E(FONTS),
        '<link rel="stylesheet" href="%s">' % stamp('assets/hub.css'),
        '<script>',
        '/* Decide before the first paint whether the door stands in front of the hall. */',
        '(function(){var h=location.hash.slice(1).toLowerCase(),skip=false;'
        'try{skip=localStorage.getItem("hub-door")==="skip";}catch(e){}'
        'if(h==="door"||(!h&&!skip))document.documentElement.classList.add("door-open");})();',
        '</script>',
        '<script src="%s" defer></script>' % stamp('assets/hub.js'),
        '</head>',
        '<body>',
        '<div class="hall" id="hall">',
        '<section class="wall" id="wall" aria-labelledby="wall-title">',
        '<header class="wall-edge wall-top mast">',
        '<span>%s</span>' % E(site['owner'].upper()),
        '<span class="mast-mid">PERMANENT COLLECTION · %s</span>' % year,
        '<nav aria-label="Site">',
        '<button type="button" class="link" id="to-door">DOOR</button>',
        '<a href="%s" target="_blank" rel="noopener">GITHUB%s</a>' % (E(site['github']), ARROW),
        '</nav>',
        '</header>',
        '<div class="wall-title">',
        '<p class="eyebrow">CLAUDE · CHATGPT</p>',
        '<h1 id="wall-title">%s</h1>' % E(site['title']),
        '<p class="lede">%s</p>' % E(lede),
        '</div>',
        '<div class="hangs">',
        hangs,
        '</div>',
        '<div class="wall-pool" aria-hidden="true"></div>',
        '<footer class="wall-edge wall-bottom">',
        '<a href="#texts">WALL TEXTS%s</a>' % DOWN,
        '</footer>',
        '</section>',
        '<div class="wrap">',
        '<section class="texts" id="texts" aria-labelledby="texts-title">',
        '<header class="texts-head">',
        '<p class="eyebrow">WALL TEXTS</p>',
        '<h2 id="texts-title">As they hang</h2>',
        '<p class="texts-note">The number and the word on each label match the wall. Type a work’s word, such as RRG, anywhere in the hall to find it.</p>',
        '</header>',
        '<ol class="text-list">',
        texts,
        '</ol>',
        '</section>',
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
        '<div class="door" id="door" role="dialog" aria-modal="true" aria-label="%s, the door">' % E(site['title']),
        '<div class="door-dark" aria-hidden="true"><div class="beam" id="beam"></div></div>',
        '<div class="door-pool" aria-hidden="true"></div>',
        '<header class="door-edge door-top">',
        '<span>%s · %s</span>' % (E(site['owner'].upper()), E(site['title'].upper())),
        '<span>SENTRY POST · <span id="door-date">%s</span></span>' % E(today_label),
        '</header>',
        '<main class="door-stage">',
        '<div class="stage">',
        '<span class="lamp" aria-hidden="true"></span>',
        '<p class="door-eyebrow">TONIGHT’S CHALLENGE</p>',
        '<h1 class="challenge"><span id="challenge">%s</span>?</h1>' % E(tonight),
        '<form class="answer-form" id="door-form" autocomplete="off">',
        '<label for="door-word">YOUR COUNTERSIGN</label>',
        '<div class="answer">',
        '<input id="door-word" name="word" type="text" maxlength="12" autocapitalize="characters" autocorrect="off" spellcheck="false" enterkeyhint="go">',
        '<span class="mirror" aria-hidden="true"><span id="mirror"></span><span class="caret"></span></span>',
        '</div>',
        '<p class="said" id="door-said" aria-live="polite"></p>',
        '</form>',
        '<p class="door-lede">Answer with a work’s word and the light goes to it. Answer <button type="button" class="inline" id="door-enter">WORKS</button> and the lights come on.</p>',
        '<p class="codes">',
        codes,
        '</p>',
        '<label class="skip"><input type="checkbox" id="door-skip">Skip this door next time on this browser</label>',
        '</div>',
        '</main>',
        '<footer class="door-edge door-bottom">',
        '<span>A NEW CHALLENGE EVERY NIGHT</span>',
        '<span>%d ON VIEW · %d IN STORAGE</span>' % (min(n, HANG_SLOTS), s),
        '</footer>',
        '</div>',
        '<script type="application/json" id="works-data">%s</script>' % js_data,
        '</body>',
        '</html>',
        ''])
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    print('index.html: %d works, %d in storage, tonight %s' % (n, s, tonight))


if __name__ == '__main__':
    build()
