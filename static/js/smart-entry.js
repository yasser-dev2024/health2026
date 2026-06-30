(function () {
  const entry = document.querySelector('[data-smart-entry]');
  if (!entry) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const forceEntry = params.get('showEntry') === '1';
  const resetEntry = params.get('resetEntry') === '1';
  const hasQrEntry = params.has('qr');
  const doneKey = 'aseer_smart_entry_done_v20260630';
  const profileUrl = entry.dataset.profileUrl || '';
  const profile = {
    visitor_type: '',
    party_type: '',
    age_group: '',
    health_topic: '',
  };
  let saveTimer = null;
  const ageMessage = entry.querySelector('[data-age-message]');
  const resultTitle = entry.querySelector('[data-result-title]');
  const resultNotice = entry.querySelector('[data-result-notice]');
  const resultRoute = entry.querySelector('[data-result-route]');

  if (resetEntry) {
    window.sessionStorage.removeItem(doneKey);
  }

  function getCookie(name) {
    const parts = document.cookie ? document.cookie.split(';') : [];
    for (let index = 0; index < parts.length; index += 1) {
      const cookie = parts[index].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return '';
  }

  function saveProfile() {
    if (!profileUrl) {
      return;
    }
    const payload = new FormData();
    Object.keys(profile).forEach(function (key) {
      payload.append(key, profile[key] || '');
    });
    window.fetch(profileUrl, {
      method: 'POST',
      body: payload,
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': getCookie('csrftoken') || entry.dataset.csrfToken || '',
      },
    }).catch(function () {});
  }

  function queueSaveProfile() {
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(saveProfile, 120);
  }

  function showStep(name) {
    entry.querySelectorAll('[data-step]').forEach(function (step) {
      step.classList.toggle('is-active', step.dataset.step === name);
    });
  }

  function showEntry() {
    if (!forceEntry && !hasQrEntry && window.sessionStorage.getItem(doneKey) === '1') {
      return;
    }
    entry.hidden = false;
    entry.classList.add('is-visible');
    document.documentElement.classList.add('smart-entry-lock');
    showStep('age');
  }

  function closeEntry(markDone) {
    if (markDone !== false) {
      window.sessionStorage.setItem(doneKey, '1');
    }
    saveProfile();
    entry.classList.add('is-leaving');
    window.setTimeout(function () {
      entry.hidden = true;
      entry.classList.remove('is-visible', 'is-leaving');
      document.documentElement.classList.remove('smart-entry-lock');
    }, 260);
  }

  window.aseerShowSmartEntry = showEntry;

  if (forceEntry) {
    showEntry();
  }

  entry.addEventListener('click', function (event) {
    const target = event.target.closest('button, a');
    if (!target) {
      return;
    }

    if (target.matches('[data-age]')) {
      profile.age_group = target.dataset.age || '';
      queueSaveProfile();
      ageMessage.textContent = target.dataset.message || '';
      showStep('healthTopic');
      return;
    }

    if (target.matches('[data-visitor]')) {
      profile.visitor_type = target.dataset.visitor || '';
      queueSaveProfile();
      showStep('party');
      return;
    }

    if (target.matches('[data-party]')) {
      profile.party_type = target.dataset.party || '';
      queueSaveProfile();
      showStep('call937');
      return;
    }

    if (target.matches('[data-health-topic]')) {
      profile.health_topic = target.dataset.healthTopic || '';
      queueSaveProfile();
      showStep('visitor');
      return;
    }

    if (target.matches('[data-skip]')) {
      queueSaveProfile();
      showStep(target.dataset.skip);
      return;
    }

    if (target.matches('[data-next]')) {
      showStep(target.dataset.next);
      return;
    }

    if (target.matches('[data-trip]')) {
      resultTitle.textContent = target.dataset.title || target.textContent.trim();
      resultNotice.textContent = target.dataset.notice || '';
      resultRoute.href = target.dataset.route || '/';
      showStep('result');
      return;
    }

    if (target.matches('[data-smart-entry-close]')) {
      closeEntry(true);
      return;
    }

    if (target.matches('[data-finish], [data-result-route]')) {
      window.sessionStorage.setItem(doneKey, '1');
      saveProfile();
      document.documentElement.classList.remove('smart-entry-lock');
    }
  });
})();
