(function () {
  const splash = document.querySelector('[data-splash]');
  if (!splash) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const forceSplash = params.get('showSplash') === '1';
  const forceEntry = params.get('showEntry') === '1';
  const seenKey = 'aseer_splash_seen';
  const closeButton = splash.querySelector('[data-splash-close]');

  function hideSplash(delay) {
    window.setTimeout(function () {
      splash.classList.add('is-leaving');
      window.setTimeout(function () {
        splash.remove();
        document.documentElement.classList.remove('splash-lock');
        if (typeof window.aseerShowSmartEntry === 'function') {
          window.aseerShowSmartEntry();
        }
      }, 360);
    }, delay);
  }

  if (!forceSplash && (forceEntry || window.sessionStorage.getItem(seenKey) === '1')) {
    splash.remove();
    window.setTimeout(function () {
      if (typeof window.aseerShowSmartEntry === 'function') {
        window.aseerShowSmartEntry();
      }
    }, 60);
    return;
  }

  document.documentElement.classList.add('splash-lock');
  splash.classList.add('is-visible');

  if (forceSplash) {
    splash.dataset.autoClose = 'false';
    closeButton.hidden = false;
  } else {
    closeButton.hidden = true;
    window.sessionStorage.setItem(seenKey, '1');
    hideSplash(4000);
  }

  closeButton.addEventListener('click', function () {
    hideSplash(0);
  });
})();
