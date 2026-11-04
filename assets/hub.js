/* Works · the door and the words it answers to.
 *
 * The door is the hall with the lights out: the works hang on a dark wall and
 * one light drifts round them. It stands in front of the hall when the address
 * has no hash and this browser has not chosen to skip it (decided in <head>
 * before the first paint).
 *
 * Tonight's challenge changes every day (Korea time). Any work's code (RRG) or
 * number (01) is a countersign: the light goes to that work and it opens in a
 * new tab. WORKS, an empty answer or Esc turns the lights on and walks into the
 * hall; GITHUB opens the repositories. In the hall, typing DOOR or 0 turns the
 * lights out again, and a code or number scrolls to its piece. #works, #rrg,
 * #01 … skip the door; #door forces it.
 */
(function () {
  'use strict';

  var root = document.documentElement;
  var hall = document.getElementById('hall');
  var door = document.getElementById('door');
  var form = document.getElementById('door-form');
  var input = document.getElementById('door-word');
  var answer = form.querySelector('.answer');
  var mirror = document.getElementById('mirror');
  var said = document.getElementById('door-said');
  var skip = document.getElementById('door-skip');
  var enterButton = document.getElementById('door-enter');
  var toDoor = document.getElementById('to-door');
  var beam = document.getElementById('beam');
  var data = JSON.parse(document.getElementById('works-data').textContent);
  var works = data.works;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(pointer: fine)').matches;
  var STORE = 'hub-door';

  /* ---- words ---- */
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

  /* ---- tonight's challenge: one word a day, Korea time ---- */
  function seoulToday() {
    var now = new Date();
    var label = {};
    var num = {};
    new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Seoul', weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
      .formatToParts(now).forEach(function (p) { label[p.type] = p.value; });
    new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit' })
      .formatToParts(now).forEach(function (p) { num[p.type] = p.value; });
    return {
      label: [label.weekday, label.day, label.month, label.year].join(' ').toUpperCase(),
      day: Date.UTC(+num.year, +num.month - 1, +num.day) / 864e5
    };
  }

  function setChallenge() {
    try {
      var t = seoulToday();
      var e = data.epoch.split('-');
      var first = Date.UTC(+e[0], +e[1] - 1, +e[2]) / 864e5;
      var list = data.challenges;
      var i = (((t.day - first) % list.length) + list.length) % list.length;
      document.getElementById('challenge').textContent = list[i];
      document.getElementById('door-date').textContent = t.label;
    } catch (err) { /* keep the word printed at build time */ }
  }

  /* ---- the light ---- */
  var pos = null;
  var goal = null;
  var mode = 'orbit';
  var holdUntil = 0;
  var startedAt = performance.now();
  var raf = 0;

  function orbitPoint(now) {
    var w = window.innerWidth;
    var h = window.innerHeight;
    var a = ((now - startedAt) / 16000) * Math.PI * 2;
    return { x: w / 2 + Math.min(w * 0.36, 520) * Math.cos(a), y: h / 2 + Math.min(h * 0.3, 300) * Math.sin(a) };
  }

  function place(p) {
    beam.style.transform = 'translate3d(' + (p.x - window.innerWidth / 2).toFixed(1) + 'px,' +
      (p.y - window.innerHeight / 2).toFixed(1) + 'px,0)';
  }

  function frame(now) {
    raf = 0;
    if (!root.classList.contains('door-open') || document.hidden) return;
    if (mode !== 'orbit' && now > holdUntil) mode = 'orbit';
    var g = mode === 'orbit' ? orbitPoint(now) : goal;
    if (!pos) pos = { x: g.x, y: g.y };
    var k = mode === 'orbit' ? 0.035 : 0.12;
    pos.x += (g.x - pos.x) * k;
    pos.y += (g.y - pos.y) * k;
    place(pos);
    raf = window.requestAnimationFrame(frame);
  }

  function run() {
    if (reduceMotion) {
      if (!pos) pos = orbitPoint(startedAt);
      place(pos);
      return;
    }
    if (!raf) raf = window.requestAnimationFrame(frame);
  }

  function aim(p, ms) {
    goal = p;
    mode = 'aim';
    holdUntil = performance.now() + ms;
    if (reduceMotion) { pos = { x: p.x, y: p.y }; place(pos); } else run();
  }

  function aimAt(work) {
    var el = door.querySelector('.hang[data-id="' + work.id + '"]');
    if (!el) return;
    var r = el.getBoundingClientRect();
    aim({ x: r.left + r.width / 2, y: r.top + r.height / 2 }, 2600);
  }

  if (finePointer && !reduceMotion) {
    door.addEventListener('pointermove', function (e) {
      if (e.pointerType === 'mouse') aim({ x: e.clientX, y: e.clientY }, 2200);
    });
  }
  document.addEventListener('visibilitychange', function () { if (!document.hidden) run(); });

  /* ---- the answer line ---- */
  var typingTimer = 0;
  function sync() { mirror.textContent = input.value.toUpperCase(); }
  input.addEventListener('input', function () {
    sync();
    answer.classList.add('typing');
    window.clearTimeout(typingTimer);
    typingTimer = window.setTimeout(function () { answer.classList.remove('typing'); }, 700);
  });

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
    answer.classList.remove('shake');
    void answer.offsetWidth;
    answer.classList.add('shake');
  }

  function clearInput() { input.value = ''; sync(); }

  function clearHash() {
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }

  /* ---- lights out, lights on ---- */
  var leaving = 0;

  function openDoor(animate) {
    window.clearTimeout(leaving);
    leaving = 0;
    door.classList.remove('leaving');
    if (animate && !reduceMotion) door.classList.add('lights-on');
    root.classList.add('door-open');
    hall.setAttribute('aria-hidden', 'true');
    hall.inert = true;
    try { skip.checked = localStorage.getItem(STORE) === 'skip'; } catch (e) { /* storage unavailable */ }
    clearInput();
    say('');
    clearHash();
    setChallenge();
    run();
    if (animate && !reduceMotion) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () { door.classList.remove('lights-on'); });
      });
    }
    window.setTimeout(function () { input.focus({ preventScroll: true }); }, 0);
  }

  function finish() {
    leaving = 0;
    root.classList.remove('door-open');
    door.classList.remove('lights-on', 'leaving');
    hall.removeAttribute('aria-hidden');
    hall.inert = false;
    if (location.hash === '#door') clearHash();
    toDoor.focus({ preventScroll: true });
  }

  function enterHall() {
    if (!root.classList.contains('door-open') || leaving) return;
    input.blur();
    if (reduceMotion) { finish(); return; }
    door.classList.add('lights-on');
    leaving = window.setTimeout(function () {
      door.classList.add('leaving');
      leaving = window.setTimeout(finish, 380);
    }, 680);
  }

  /* ---- answering at the door ---- */
  function answerWith(word) {
    var r = read(word);
    if (r.kind === 'enter') { enterHall(); return; }
    if (r.kind === 'door') { say('You are at the door. Answer with a work’s word, or WORKS.'); return; }
    if (r.kind === 'github') {
      window.open(data.github, '_blank', 'noopener');
      say('GitHub opens in a new tab.', data.github);
      clearInput();
      return;
    }
    if (r.kind === 'work') {
      window.open(r.work.url, '_blank', 'noopener');
      aimAt(r.work);
      say(r.work.title + ' opens in a new tab.', r.work.url);
      clearInput();
      return;
    }
    say('That is not the word. Try a work’s word, such as RRG, or WORKS.', null, true);
    shake();
    input.select();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    answerWith(input.value);
  });
  Array.prototype.forEach.call(door.querySelectorAll('.code'), function (b) {
    b.addEventListener('click', function () { answerWith(b.getAttribute('data-word')); });
  });
  enterButton.addEventListener('click', enterHall);
  toDoor.addEventListener('click', function () { openDoor(true); });
  skip.addEventListener('change', function () {
    try {
      if (skip.checked) localStorage.setItem(STORE, 'skip');
      else localStorage.removeItem(STORE);
    } catch (e) { /* storage unavailable */ }
  });
  door.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { e.preventDefault(); enterHall(); }
  });

  /* ---- in the hall: words typed anywhere ---- */
  function locate(work) {
    var el = document.getElementById(work.id);
    if (!el) return;
    el.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
    el.classList.add('is-found');
    window.setTimeout(function () { el.classList.remove('is-found'); }, 1800);
    var link = el.querySelector('.frame');
    if (link) link.focus({ preventScroll: true });
  }

  var buffer = '';
  var timer = 0;
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
      if (r.kind === 'door') openDoor(true);
      else if (r.kind === 'work') locate(r.work);
    }, 650);
  });

  /* ---- deep links ---- */
  function followHash() {
    var h = location.hash.slice(1);
    if (h.toLowerCase() === 'door') { openDoor(true); return; }
    if (!h || h.toLowerCase() === 'works') return;
    var r = read(h);
    if (r.kind === 'work') window.setTimeout(function () { locate(r.work); }, 80);
  }
  window.addEventListener('hashchange', function () {
    if (root.classList.contains('door-open') && location.hash && location.hash !== '#door') finish();
    followHash();
  });

  setChallenge();
  if (root.classList.contains('door-open')) openDoor(false);
  else followHash();
})();
