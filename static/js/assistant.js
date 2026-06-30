(function () {
  const faqs = Array.from(document.querySelectorAll('.assistant-faq'));
  if (!faqs.length) {
    return;
  }

  faqs.forEach((faq) => {
    faq.addEventListener('toggle', () => {
      if (!faq.open) {
        return;
      }
      faqs.forEach((item) => {
        if (item !== faq) {
          item.open = false;
        }
      });
    });
  });
})();
