// Tema claro/oscuro: se aplica antes de pintar la página para evitar parpadeo.
(function () {
  var KEY = 'coti-theme';
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function systemTheme() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#0B1120' : '#4F46E5');
  }
  apply(stored() || systemTheme());

  window.toggleTheme = function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.classList.add('theme-anim');
    apply(next);
    try { localStorage.setItem(KEY, next); } catch (e) {}
    setTimeout(function () { document.documentElement.classList.remove('theme-anim'); }, 350);
  };

  // Si el usuario no eligió manualmente, seguir los cambios del sistema
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var onChange = function () { if (!stored()) apply(systemTheme()); };
    if (mq.addEventListener) mq.addEventListener('change', onChange); else if (mq.addListener) mq.addListener(onChange);
  }
})();
