const machineFilter = document.querySelector("#machine-filter");
if (machineFilter) {
  document.documentElement.classList.add("js");
  machineFilter.addEventListener("change", () => machineFilter.form.requestSubmit());
}
