// Show spinner on any form submit
document.querySelectorAll("form.pdf-form").forEach(form => {
  form.addEventListener("submit", () => {
    document.getElementById("spinner").classList.add("active");
  });
});

// Marker page: toggle watermark vs page-number options
const markerMode = document.getElementById("markerMode");
if (markerMode) {
  markerMode.addEventListener("change", () => {
    const isPageNum = markerMode.value === "page-numbers";
    document.getElementById("textOptions").style.display    = isPageNum ? "none" : "";
    document.getElementById("pageNumOptions").style.display = isPageNum ? "" : "none";
  });
}

// Merge/Split page: toggle split options and file hint
const actionRadios = document.querySelectorAll("input[name='action']");
if (actionRadios.length) {
  function toggleSplitOptions() {
    const isSplit = document.getElementById("actionSplit").checked;
    document.getElementById("splitOptions").style.display = isSplit ? "" : "none";
    document.getElementById("fileHint").textContent = isSplit
      ? "For split: upload the single PDF you want to split."
      : "For merge: upload all PDFs to combine. They will be merged in filename order.";
  }
  actionRadios.forEach(r => r.addEventListener("change", toggleSplitOptions));
}
