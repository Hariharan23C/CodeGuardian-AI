document.addEventListener("DOMContentLoaded", () => {
  const codeInput = document.getElementById("codeInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const errorMsg = document.getElementById("errorMsg");
  const results = document.getElementById("results");
  const levelBtns = document.querySelectorAll(".level-btn");

  let selectedLevel = "beginner";

  levelBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      levelBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedLevel = btn.dataset.level;
    });
  });

  analyzeBtn.addEventListener("click", async () => {
    const code = codeInput.value.trim();
    errorMsg.hidden = true;

    if (!code) {
      errorMsg.textContent = "Paste some code first.";
      errorMsg.hidden = false;
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing…";
    results.hidden = true;

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, level: selectedLevel }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Something went wrong.");
      }

      renderResults(data);
      results.hidden = false;
      results.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      errorMsg.textContent = err.message;
      errorMsg.hidden = false;
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze Code";
    }
  });

  function renderResults(data) {
    document.getElementById("langTag").textContent = data.language_detected || "code";
    document.getElementById("summaryText").textContent = data.overall_summary || "";

    // Line by line
    const lineList = document.getElementById("lineByLine");
    lineList.innerHTML = "";
    (data.line_by_line || []).forEach(item => {
      const div = document.createElement("div");
      div.className = "line-item";
      div.innerHTML = `
        <span class="line-num">Line ${escapeHtml(item.lines || "")}</span>
        <pre>${escapeHtml(item.code || "")}</pre>
        <div class="explanation">${escapeHtml(item.explanation || "")}</div>
      `;
      lineList.appendChild(div);
    });
    if (!lineList.children.length) {
      lineList.innerHTML = `<p class="no-issues">No breakdown returned.</p>`;
    }

    // Complexity
    const c = data.complexity || {};
    document.getElementById("timeComplexity").textContent = c.time || "—";
    document.getElementById("spaceComplexity").textContent = c.space || "—";
    document.getElementById("complexityExplanation").textContent = c.explanation || "";

    // Bugs
    const bugsList = document.getElementById("bugsList");
    bugsList.innerHTML = "";
    const bugs = data.bugs || [];
    if (bugs.length === 0) {
      bugsList.innerHTML = `<p class="no-issues">✅ No issues flagged.</p>`;
    } else {
      bugs.forEach(bug => {
        const div = document.createElement("div");
        div.className = `bug-item ${escapeHtml(bug.severity || "low")}`;
        div.innerHTML = `
          <div class="bug-head">${escapeHtml(bug.issue || "")} ${bug.line ? `(line ${escapeHtml(bug.line)})` : ""}</div>
          <div class="bug-fix">Fix: ${escapeHtml(bug.fix || "")}</div>
        `;
        bugsList.appendChild(div);
      });
    }

    // Suggestions
    const suggList = document.getElementById("suggestionsList");
    suggList.innerHTML = "";
    (data.suggestions || []).forEach(s => {
      const li = document.createElement("li");
      li.textContent = s;
      suggList.appendChild(li);
    });
    if (!suggList.children.length) {
      suggList.innerHTML = `<li class="no-issues">Nothing to suggest — looks solid.</li>`;
    }

    // Interview questions
    const interviewList = document.getElementById("interviewList");
    interviewList.innerHTML = "";
    (data.interview_questions || []).forEach(q => {
      const div = document.createElement("div");
      div.className = "interview-item";
      div.innerHTML = `
        <div class="q">${escapeHtml(q.question || "")}</div>
        <div class="hint">Hint: ${escapeHtml(q.hint || "")}</div>
      `;
      interviewList.appendChild(div);
    });

    // Flowchart
    renderFlowchart(data.flowchart_mermaid || "flowchart TD\nA[No flowchart returned]");
  }

  async function renderFlowchart(definition) {
    const box = document.getElementById("flowchartBox");
    box.removeAttribute("data-processed");
    box.innerHTML = definition;
    try {
      if (window.__mermaid) {
        const { svg } = await window.__mermaid.render("flowchartSvg-" + Date.now(), definition);
        box.innerHTML = svg;
      }
    } catch (e) {
      box.innerHTML = `<p class="no-issues" style="color:var(--muted)">Flowchart couldn't be rendered for this code.</p>`;
    }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  }
});
