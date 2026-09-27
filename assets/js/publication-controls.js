document.addEventListener("DOMContentLoaded", () => {
  const overview = document.querySelector(".publication-overview");
  if (!overview) return;
  const buttons = [...overview.querySelectorAll(".publication-filter")];
  const entries = [...document.querySelectorAll(".publications ol.bibliography > li")];
  const search = document.getElementById("bibsearch");
  const status = document.querySelector(".publication-filter-status");
  let category = "all";

  const applyFilters = () => {
    const query = ((search && search.value) || "").trim().toLocaleLowerCase();
    let count = 0;
    entries.forEach((entry) => {
      const categoryBadge = entry.querySelector("[data-publication-category]");
      const type = categoryBadge && categoryBadge.dataset.publicationCategory;
      const visible = (category === "all" || category === type) && entry.textContent.toLocaleLowerCase().includes(query);
      entry.classList.toggle("unloaded", !visible);
      if (visible) count += 1;
    });
    document.querySelectorAll(".publications ol.bibliography").forEach((list) => {
      list.classList.toggle("unloaded", ![...list.children].some((item) => !item.classList.contains("unloaded")));
    });
    document.querySelectorAll(".publications h2.bibliography, .publications h3.bibliography").forEach((heading) => {
      let next = heading.nextElementSibling;
      let visible = false;
      while (next && !/^H[23]$/.test(next.tagName)) {
        if (next.matches("ol.bibliography") && !next.classList.contains("unloaded")) visible = true;
        next = next.nextElementSibling;
      }
      heading.classList.toggle("unloaded", !visible);
    });
    buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.category === category)));
    status.textContent = status.dataset.lang === "ja" ? `${count}件を表示` : `${count} publications shown`;
    status.classList.toggle("sr-only", count !== 0);
  };

  buttons.forEach((button) => button.addEventListener("click", () => {
    category = button.dataset.category;
    applyFilters();
  }));
  if (search) search.addEventListener("input", applyFilters);
  const readHash = () => {
    let hash;
    try { hash = decodeURIComponent(window.location.hash.slice(1)); } catch (error) { return; }
    if (search && !document.getElementById(hash)) search.value = hash;
    applyFilters();
  };
  window.addEventListener("hashchange", readHash);
  readHash();
});
