// Keep the research-theme links in sync with the visible section.
document.addEventListener("DOMContentLoaded", () => {
  const links = [...document.querySelectorAll(".research-theme-nav a[href^='#']")];
  const sections = links.map(link => document.getElementById(link.hash.slice(1)));
  if (!links.length || sections.some(section => !section)) return;
  let scheduled = false;
  const update = () => {
    let index = 0;
    sections.forEach((section, i) => { if (section.getBoundingClientRect().top <= 150) index = i; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 8) index = links.length - 1;
    links.forEach((link, i) => {
      if (i === index) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
    scheduled = false;
  };
  const schedule = () => { if (!scheduled) { scheduled = true; requestAnimationFrame(update); } };
  window.addEventListener("scroll", schedule, {passive: true});
  window.addEventListener("resize", schedule);
  window.addEventListener("hashchange", schedule);
  update();
});
