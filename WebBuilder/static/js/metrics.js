/* metrics.js — Sidebar navigation + Chart.js activity chart */

document.addEventListener('DOMContentLoaded', function () {

  // ── SIDEBAR NAVIGATION ──────────────────────────────────────
  document.querySelectorAll('.m-sidebar-item').forEach(function (item) {
    item.addEventListener('click', function () {
      document.querySelectorAll('.m-sidebar-item').forEach(function (i) { i.classList.remove('active'); });
      document.querySelectorAll('.m-panel').forEach(function (p) { p.classList.remove('active'); });
      item.classList.add('active');
      document.getElementById('m-panel-' + item.dataset.panel).classList.add('active');
      if (item.dataset.panel === 'actividad') drawChart();
    });
  });

  // ── CHART ───────────────────────────────────────────────────
  var chartDrawn = false;

  function drawChart() {
    if (chartDrawn) return;
    chartDrawn = true;

    var canvas = document.getElementById('m-activity-chart');
    if (!canvas) return;

    var labels   = JSON.parse(canvas.dataset.labels);
    var analyses = JSON.parse(canvas.dataset.analyses);
    var sites    = JSON.parse(canvas.dataset.sites);

    var ctx = canvas.getContext('2d');

    var gA = ctx.createLinearGradient(0, 0, 0, 240);
    gA.addColorStop(0, 'rgba(255,255,255,0.07)');
    gA.addColorStop(1, 'rgba(255,255,255,0)');

    var gB = ctx.createLinearGradient(0, 0, 0, 240);
    gB.addColorStop(0, 'rgba(255,255,255,0.03)');
    gB.addColorStop(1, 'rgba(255,255,255,0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Análisis',
            data: analyses,
            borderColor: 'rgba(255,255,255,0.65)',
            backgroundColor: gA,
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 4,
            pointHoverBackgroundColor: 'rgba(255,255,255,0.9)',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Sitios generados',
            data: sites,
            borderColor: 'rgba(255,255,255,0.22)',
            backgroundColor: gB,
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 4,
            pointHoverBackgroundColor: 'rgba(255,255,255,0.5)',
            tension: 0.4,
            fill: true,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a1a1c',
            borderColor: 'rgba(255,255,255,0.08)',
            borderWidth: 1,
            titleColor: 'rgba(255,255,255,0.35)',
            bodyColor: 'rgba(255,255,255,0.8)',
            titleFont: { family: 'Geist Mono', size: 10 },
            bodyFont: { family: 'Geist', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
            ticks: { color: 'rgba(255,255,255,0.18)', font: { family: 'Geist Mono', size: 10 }, maxTicksLimit: 8 },
            border: { display: false },
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
            ticks: { color: 'rgba(255,255,255,0.18)', font: { family: 'Geist Mono', size: 10 }, maxTicksLimit: 5 },
            border: { display: false },
          }
        }
      }
    });
  }

});
