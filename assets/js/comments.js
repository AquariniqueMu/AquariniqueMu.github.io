(() => {
  const el = document.querySelector('.giscus');
  if (!el) return;
  let loaded = false;
  const theme = () => document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  const load = () => {
    if (loaded) return;
    loaded = true;
    const s = document.createElement('script');
    s.src = 'https://giscus.app/client.js';
    const attrs = {repo:el.dataset.repo, 'repo-id':el.dataset.repoId, category:el.dataset.category, 'category-id':el.dataset.categoryId, mapping:'pathname', strict:'1', 'reactions-enabled':'1', 'emit-metadata':'0', 'input-position':'top', theme:theme(), lang:'en', loading:'lazy'};
    for (const [key,value] of Object.entries(attrs)) s.setAttribute('data-' + key, value);
    s.crossOrigin = 'anonymous'; s.async = true; el.appendChild(s);
  };
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {if (entries.some(e => e.isIntersecting)) {load();observer.disconnect();}}, {rootMargin:'300px'});
    observer.observe(el);
  } else load();
  new MutationObserver(() => {const frame = el.querySelector('iframe.giscus-frame'); if(frame) frame.contentWindow.postMessage({giscus:{setConfig:{theme:theme()}}},'https://giscus.app');}).observe(document.documentElement,{attributes:true,attributeFilter:['class']});
})();
