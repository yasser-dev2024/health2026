(function () {
  const quizApp = document.querySelector('[data-hero-quiz-app]');

  if (quizApp) {
    const dataEl = document.getElementById('hero-question-data');
    const questions = dataEl ? JSON.parse(dataEl.textContent || '[]') : [];
    const introScreen = quizApp.querySelector('[data-hero-screen="intro"]');
    const quizScreen = quizApp.querySelector('[data-hero-screen="quiz"]');
    const contactScreen = quizApp.querySelector('[data-hero-screen="contact"]');
    const startButton = quizApp.querySelector('[data-hero-start]');
    const nextButton = quizApp.querySelector('[data-hero-next]');
    const backButton = quizApp.querySelector('[data-hero-back]');
    const progress = quizApp.querySelector('[data-hero-progress]');
    const percent = quizApp.querySelector('[data-hero-percent]');
    const stepLabel = quizApp.querySelector('[data-hero-step-label]');
    const questionNumber = quizApp.querySelector('[data-hero-question-number]');
    const questionText = quizApp.querySelector('[data-hero-question-text]');
    const optionsRoot = quizApp.querySelector('[data-hero-options]');
    const feedback = quizApp.querySelector('[data-hero-feedback]');
    const hiddenFields = quizApp.querySelector('[data-hero-hidden-fields]');
    const answers = new Array(questions.length).fill(null);
    let current = 0;
    let answered = false;

    function showScreen(screen) {
      [introScreen, quizScreen, contactScreen].forEach((item) => {
        const active = item === screen;
        item.hidden = !active;
        item.classList.toggle('is-active', active);
      });
      quizApp.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function optionLetter(index) {
      return ['أ', 'ب', 'ج', 'د'][index] || String(index + 1);
    }

    function updateProgress() {
      const value = questions.length ? Math.round((current / questions.length) * 100) : 0;
      if (progress) {
        progress.style.width = `${value}%`;
      }
      if (percent) {
        percent.textContent = `${value}%`;
      }
      if (stepLabel) {
        stepLabel.textContent = `السؤال ${Math.min(current + 1, questions.length)} من ${questions.length}`;
      }
    }

    function renderQuestion() {
      const question = questions[current];
      answered = answers[current] !== null;
      updateProgress();

      if (!question) {
        showContact();
        return;
      }

      questionNumber.textContent = `السؤال ${current + 1}`;
      questionText.textContent = question.question;
      feedback.hidden = true;
      feedback.textContent = '';
      optionsRoot.innerHTML = '';

      question.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'hero-live-option';
        button.type = 'button';
        button.innerHTML = `<span>${optionLetter(index)}</span><strong></strong><b>${option}</b>`;
        button.querySelector('strong').setAttribute('aria-hidden', 'true');
        button.addEventListener('click', () => selectAnswer(index));
        optionsRoot.appendChild(button);
      });

      if (answers[current] !== null) {
        applyAnswerState(answers[current]);
      } else {
        nextButton.disabled = true;
        nextButton.textContent = current === questions.length - 1 ? 'إكمال البيانات' : 'السؤال التالي';
      }
    }

    function applyAnswerState(selectedIndex) {
      const question = questions[current];
      const correctIndex = Number(question.correctIndex);
      const correct = selectedIndex === correctIndex;
      const buttons = Array.from(optionsRoot.querySelectorAll('.hero-live-option'));

      buttons.forEach((button, index) => {
        button.disabled = true;
        button.classList.toggle('is-correct', index === correctIndex);
        button.classList.toggle('is-wrong', index === selectedIndex && !correct);
        const marker = button.querySelector('strong');
        if (index === correctIndex) {
          marker.textContent = '✓';
        } else if (index === selectedIndex && !correct) {
          marker.textContent = '×';
        } else {
          marker.textContent = '';
        }
      });

      feedback.hidden = false;
      feedback.className = `hero-live-feedback ${correct ? 'is-correct' : 'is-wrong'}`;
      feedback.textContent = `${correct ? 'إجابة صحيحة' : 'إجابة غير صحيحة'}: ${question.tip || question.resultMessage || ''}`;
      nextButton.disabled = false;
      nextButton.textContent = current === questions.length - 1 ? 'إكمال البيانات' : 'السؤال التالي';
    }

    function selectAnswer(index) {
      if (answered) {
        return;
      }
      answers[current] = index;
      answered = true;
      applyAnswerState(index);
    }

    function showContact() {
      hiddenFields.innerHTML = '';
      questions.forEach((question, index) => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = `question_${question.id}`;
        input.value = answers[index] === null ? '' : String(answers[index]);
        hiddenFields.appendChild(input);
      });
      if (progress) {
        progress.style.width = '100%';
      }
      if (percent) {
        percent.textContent = '100%';
      }
      showScreen(contactScreen);
    }

    if (startButton) {
      startButton.addEventListener('click', () => {
        current = 0;
        renderQuestion();
        showScreen(quizScreen);
      });
    }

    if (nextButton) {
      nextButton.addEventListener('click', () => {
        if (!answered) {
          return;
        }
        if (current < questions.length - 1) {
          current += 1;
          renderQuestion();
          return;
        }
        showContact();
      });
    }

    if (backButton) {
      backButton.addEventListener('click', () => {
        current = Math.max(0, questions.length - 1);
        renderQuestion();
        showScreen(quizScreen);
      });
    }
  }

  const certificate = document.querySelector('[data-hero-certificate]');
  const downloadButton = document.querySelector('[data-download-certificate]');
  const shareButton = document.querySelector('[data-share-certificate]');

  function drawCertificate(callback) {
    if (!certificate) {
      callback(null);
      return;
    }

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth || 1536;
      canvas.height = img.naturalHeight || 1086;
      const ctx = canvas.getContext('2d');
      const name = certificate.dataset.name || 'بطل الصحة';
      const score = certificate.dataset.score || '0';
      const total = certificate.dataset.total || '0';
      const badge = certificate.dataset.badge || 'بطل الصحة';
      const date = certificate.dataset.date || new Date().toLocaleDateString('ar-SA');
      const centerX = canvas.width / 2;

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      ctx.direction = 'rtl';
      ctx.textAlign = 'center';
      ctx.fillStyle = '#123F6D';
      ctx.font = 'bold 48px Tahoma, Arial';
      ctx.fillText('شهادة شكر وتقدير', centerX, 330);
      ctx.fillStyle = '#D4AF37';
      ctx.font = 'bold 62px Tahoma, Arial';
      ctx.fillText('بطل الصحة في عسير', centerX, 420);
      ctx.fillStyle = '#4B5563';
      ctx.font = '28px Tahoma, Arial';
      ctx.fillText('تمنح هذه الشهادة إلى', centerX, 500);
      ctx.fillStyle = '#0F172A';
      ctx.font = 'bold 58px Tahoma, Arial';
      ctx.fillText(name, centerX, 585);
      ctx.fillStyle = '#334155';
      ctx.font = '27px Tahoma, Arial';
      ctx.fillText(`تقديرًا لمشاركته في تحدي بطل الصحة وتحقيقه ${score} من ${total} نقطة`, centerX, 650);
      ctx.fillStyle = '#15508A';
      ctx.font = 'bold 30px Tahoma, Arial';
      ctx.fillText(badge, centerX, 705);
      ctx.fillStyle = '#64748B';
      ctx.font = '24px Tahoma, Arial';
      ctx.fillText(date, centerX, 785);
      callback(canvas);
    };
    img.onerror = function () {
      callback(null);
    };
    img.src = certificate.dataset.templateUrl;
  }

  if (downloadButton) {
    downloadButton.addEventListener('click', () => {
      drawCertificate((canvas) => {
        if (!canvas) {
          return;
        }
        const link = document.createElement('a');
        link.download = 'health-hero-aseer-certificate.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
      });
    });
  }

  if (shareButton) {
    shareButton.addEventListener('click', async () => {
      const text = 'حصلت على شهادة بطل الصحة في عسير من تجمع عسير الصحي';
      if (navigator.share) {
        try {
          await navigator.share({ title: 'بطل الصحة في عسير', text, url: window.location.href });
          return;
        } catch (error) {
          return;
        }
      }
      window.location.href = `https://wa.me/?text=${encodeURIComponent(`${text} ${window.location.href}`)}`;
    });
  }
})();
