/* Works · the door and the words it answers to.
 *
 * The door stands in front of the hall when the address has no hash and this
 * browser has not chosen to skip it (the decision is made in <head> before the
 * first paint). At the door, a work's code (RRG) or number (01) opens it in a
 * new tab, WORKS or an empty word walks in, GITHUB opens the repositories.
 * In the hall, typing DOOR or 0 brings the door back, and a code or number
 * scrolls to its piece. #works, #rrg, #01 … skip the door; #door forces it.
 */
(function () {
  'use strict';

  var root = document.documentElement;
  var hall = document.getElementById('hall');
  var door = document.getElementById('door');
  var panel = door.querySelector('.door-panel');
  var form = document.getElementById('door-form');
  var input = document.getElementById('door-word');
  var field = form.querySelector('.field');
  var said = document.getElementById('door-said');
  var skip = document.getElementById('door-skip');
  var enter = document.getElementById('door-enter');
  var toDoor = document.getElementById('to-door');
  var data = JSON.parse(document.getElementById('works-data').textContent);
  var works = data.works;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var STORE = 'hub-door';

  function read(word) {
    var w = String(word || '').trim().toUpperCase().replace(/^#/, '');
    var i;
    if (w === '' || w === 'WORKS' || w === 'HALL') return { kind: 'enter' };
    if (w === 'GITHUB') return { kind: 'github' };
    if (w === 'DOOR' || /^0+$/.test(w)) return { kind: 'door' };
    if (/^\d{1,2}$/.test(w)) {
      var n = parseInt(w, 10);
      for (i = 0; i < works.length; i++) if (works[i].no === n) return { kind: 'work', work: works[i] };
    }
    for (i = 0; i < works.length; i++) {
      if (works[i].code.toUpperCase() === w || works[i].id.toUpperCase() === w) return { kind: 'work', work: works[i] };
    }
    return { kind: 'none', word: w };
  }

  function say(text, href, miss) {
    said.textContent = text;
    said.classList.toggle('miss', !!miss);
    if (href) {
      said.appendChild(document.createTextNode(' '));
      var a = document.createElement('a');
      a.href = href;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = 'Not opened? Open it here.';
      said.appendChild(a);
    }
  }

  function shake() {
    field.classList.remove('shake');
    void field.offsetWidth;
    field.classList.add('shake');
  }

  function clearHash() {
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }

  function openDoor() {
    root.classList.add('door-open');
    hall.setAttribute('aria-hidden', 'true');
    hall.inert = true;
    try { skip.checked = localStorage.getItem(STORE) === 'skip'; } catch (e) { /* storage unavailable */ }
    input.value = '';
    say('');
    panel.scrollTop = 0;
    clearHash();
    window.setTimeout(function () { input.focus(); }, 0);
  }

  function closeDoor() {
    root.classList.remove('door-open');
    hall.removeAttribute('aria-hidden');
    hall.inert = false;
    if (location.hash === '#door') clearHash();
    toDoor.focus({ preventScroll: true });
  }

  function locate(work) {
    var el = document.getElementById(work.id);
    if (!el) return;
    el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
    el.classList.add('is-found');
    window.setTimeout(function () { el.classList.remove('is-found'); }, 1800);
    var link = el.querySelector('.frame');
    if (link) link.focus({ preventScroll: true });
  }

  /* ---- at the door ---- */
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var r = read(input.value);
    if (r.kind === 'enter') { closeDoor(); return; }
    if (r.kind === 'door') { say('You are at the door. Give a word, or walk in.'); return; }
    if (r.kind === 'github') {
      window.open(data.github, '_blank', 'noopener');
      say('GitHub opens in a new tab.', data.github);
      input.value = '';
      return;
    }
    if (r.kind === 'work') {
      window.open(r.work.url, '_blank', 'noopener');
      say(r.work.title + ' opens in a new tab.', r.work.url);
      input.value = '';
      return;
    }
    say('No work answers to “' + r.word + '”. Try RRG, 01 or WORKS.', null, true);
    shake();
    input.select();
  });

  enter.addEventListener('click', closeDoor);
  toDoor.addEventListener('click', openDoor);

  skip.addEventListener('change', function () {
    try {
      if (skip.checked) localStorage.setItem(STORE, 'skip');
      else localStorage.removeItem(STORE);
    } catch (e) { /* storage unavailable */ }
  });

  door.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { e.preventDefault(); closeDoor(); }
  });

  /* ---- in the hall: words typed anywhere ---- */
  var buffer = '';
  var timer = null;
  document.addEventListener('keydown', function (e) {
    if (root.classList.contains('door-open')) return;
    if (e.metaKey || e.ctrlKey || e.altKey || e.isComposing) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (!/^[a-z0-9]$/i.test(e.key)) return;
    buffer = (buffer + e.key.toUpperCase()).slice(-8);
    window.clearTimeout(timer);
    timer = window.setTimeout(function () {
      var r = read(buffer);
      buffer = '';
      if (r.kind === 'door') openDoor();
      else if (r.kind === 'work') locate(r.work);
    }, 650);
  });

  /* ---- deep links ---- */
  function followHash() {
    var h = location.hash.slice(1);
    if (h.toLowerCase() === 'door') { openDoor(); return; }
    if (!h || h.toLowerCase() === 'works') return;
    var r = read(h);
    if (r.kind === 'work') window.setTimeout(function () { locate(r.work); }, 80);
  }
  window.addEventListener('hashchange', function () {
    if (root.classList.contains('door-open') && location.hash && location.hash !== '#door') closeDoor();
    followHash();
  });

  if (root.classList.contains('door-open')) openDoor();
  else followHash();
})();
