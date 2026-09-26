// 92PKR Live Split-Screen AI Predictor & History Analyzer

let ratioChartInstance = null;
let freqChartInstance = null;
let soundEnabled = true;
let audioCtx = null;
let lastSignal = null;
let currentPeriod = 0;
let currentGameMode = "1m";
let targetEndTimeMs = 0;
let liveSyncInterval = null;
let countdownTimerInterval = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initDropZone();
  initIframeCheck();
  startLiveGameSync();
});

// Live Game Mode Switcher (1m, 30s, 3m, 5m)
function changeGameMode(mode) {
  currentGameMode = mode;
  showAlert(`Switched live tracking to ${mode.toUpperCase()}`, "success");
  syncLiveGame();
}

// Start Live Stream Polling & Real-Time Clock
function startLiveGameSync() {
  syncLiveGame();

  // Poll 92PKR server every 3.5 seconds
  if (liveSyncInterval) clearInterval(liveSyncInterval);
  liveSyncInterval = setInterval(syncLiveGame, 3500);

  // High-precision 1-second clock countdown
  if (countdownTimerInterval) clearInterval(countdownTimerInterval);
  countdownTimerInterval = setInterval(updateLiveClock, 1000);
}

// Query live 92PKR server
async function syncLiveGame() {
  try {
    const res = await fetch(`/api/live_sync?game=${encodeURIComponent(currentGameMode)}`);
    const data = await res.json();
    if (data.status === "success") {
      const info = data.issue_info || {};
      if (info.endTime && info.serviceTime) {
        const endMs = new Date(info.endTime.replace(/-/g, "/")).getTime();
        const srvMs = new Date(info.serviceTime.replace(/-/g, "/")).getTime();
        const diff = endMs - srvMs;
        targetEndTimeMs = Date.now() + Math.max(0, diff);
      }
      renderDashboard(data);
    }
  } catch (err) {
    console.warn("Live sync polling error:", err);
  }
}

// Real-time countdown clock
function updateLiveClock() {
  const clockEl = document.getElementById("liveCountdownClock");
  if (!clockEl || !targetEndTimeMs) return;

  const remainingMs = targetEndTimeMs - Date.now();
  const totalSec = Math.max(0, Math.floor(remainingMs / 1000));
  const mins = Math.floor(totalSec / 60);
  const secs = totalSec % 60;
  const timeStr = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  clockEl.innerText = timeStr;

  if (totalSec <= 5 && totalSec > 0) {
    clockEl.className = "font-mono text-base font-black text-rose-400 bg-rose-950/80 px-2.5 py-0.5 rounded-lg border border-rose-600 shadow animate-pulse";
    playBeep(440, 0.08); // countdown tick
  } else if (totalSec <= 10) {
    clockEl.className = "font-mono text-base font-black text-amber-400 bg-amber-950/80 px-2.5 py-0.5 rounded-lg border border-amber-600 shadow";
  } else {
    clockEl.className = "font-mono text-base font-black text-cyan-400 bg-slate-950 px-2.5 py-0.5 rounded-lg border border-cyan-800/60 shadow-sm";
  }

  // If clock just hit 0, trigger immediate sync to fetch the new winning draw
  if (totalSec === 0 && Math.random() < 0.3) {
    setTimeout(syncLiveGame, 1200);
  }
}


// View mode switcher: 'split' or 'full'
function switchView(mode) {
  const splitSec = document.getElementById("splitScreenSection");
  const fullSec = document.getElementById("fullAnalyticsSection");
  const btnSplit = document.getElementById("btnSplitView");
  const btnFull = document.getElementById("btnFullView");

  if (mode === "split") {
    splitSec.classList.remove("hidden");
    fullSec.classList.add("hidden");
    btnSplit.className = "px-3.5 py-1.5 rounded-lg bg-cyan-600 text-white shadow-md transition flex items-center space-x-1.5";
    btnFull.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center space-x-1.5";
  } else {
    splitSec.classList.add("hidden");
    fullSec.classList.remove("hidden");
    btnFull.className = "px-3.5 py-1.5 rounded-lg bg-cyan-600 text-white shadow-md transition flex items-center space-x-1.5";
    btnSplit.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center space-x-1.5";
  }
  if (window.lucide) lucide.createIcons();
}

// Toggle audio alerts
function toggleSound() {
  soundEnabled = !soundEnabled;
  const label = document.getElementById("soundLabel");
  const icon = document.getElementById("soundIcon");
  if (soundEnabled) {
    label.innerText = "Sound On";
    icon.classList.remove("text-slate-500");
    icon.classList.add("text-cyan-400");
    playBeep(600, 0.1);
  } else {
    label.innerText = "Sound Off";
    icon.classList.remove("text-cyan-400");
    icon.classList.add("text-slate-500");
  }
}

// Play notification chime using Web Audio API
function playBeep(freq = 587.33, duration = 0.15) {
  if (!soundEnabled) return;
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch (e) {
    console.log("Audio not allowed yet without user interaction");
  }
}

// 1-Click Quick Logger: user clicks a number (0-9) immediately after round finishes
async function quickLogNumber(num) {
  const size = num >= 5 ? "Big" : "Small";
  let color = "Red";
  if (num === 0 || num === 5) color = "Violet";
  else if ([1, 3, 7, 9].includes(num)) color = "Green";

  try {
    const res = await fetch("/api/record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ period: "auto", number: num, size, color })
    });
    const data = await res.json();
    if (data.status === "success") {
      playBeep(880, 0.2); // Success high beep
      showAlert(`Logged ${data.new_period || 'Draw'}: ${num} (${size})`, "success");
      renderDashboard(data);
    } else {
      showAlert(data.message || "Error logging draw", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Failed to record round", "danger");
  }
}

// Bulk ZIP / Multi-image Dataset Upload Handler
async function handleBulkUpload(e) {
  const files = e.target.files;
  if (!files || files.length === 0) return;

  showAlert(`Uploading & extracting ${files.length} file(s) into AI engine...`, "warning");

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    if (data.status === "success") {
      playBeep(950, 0.3);
      showAlert(data.message, "success");
      renderDashboard(data);
    } else {
      showAlert(data.message || "Could not extract dataset rows.", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Server error uploading dataset archive.", "danger");
  } finally {
    e.target.value = "";
  }
}


// Browser Frame Handlers
function loadGameFrame() {
  const input = document.getElementById("gameUrlInput").value.trim();
  const useProxy = document.getElementById("useProxyToggle").checked;
  const frame = document.getElementById("gameFrame");

  if (!input) return;
  let targetUrl = input;
  if (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
    targetUrl = "https://" + targetUrl;
  }

  if (useProxy) {
    frame.src = `/proxy?url=${encodeURIComponent(targetUrl)}`;
  } else {
    frame.src = targetUrl;
  }
}

function openExternalGame() {
  const url = document.getElementById("gameUrlInput").value.trim() || "https://92pkr.site";
  window.open(url, "92PKR_Live_Game", "width=480,height=800,scrollbars=yes,resizable=yes");
}

function initIframeCheck() {
  const frame = document.getElementById("gameFrame");
  const notice = document.getElementById("iframeOverlayNotice");
  frame.onerror = () => {
    notice.classList.remove("hidden");
  };
}

// Fetch dashboard data
async function fetchDashboardData() {
  try {
    const res = await fetch("/api/data");
    const data = await res.json();
    if (data.status === "success") {
      renderDashboard(data);
    }
  } catch (err) {
    console.error("Error fetching data:", err);
  }
}

// Render complete dashboard
function renderDashboard(data) {
  const history = data.history || [];
  const predData = data.prediction_data || {};
  const prediction = predData.prediction || null;
  const models = predData.models_breakdown || {};
  const stats = predData.stats_summary || {};

  // Track latest period
  if (history.length > 0) {
    const last = history[history.length - 1];
    const numPart = parseInt(String(last.period).replace(/\D/g, ""), 10);
    if (!isNaN(numPart)) currentPeriod = numPart;
    document.getElementById("liveLastRecorded").innerText = `${last.number} (${last.size})`;
  }

  // Header counts
  document.getElementById("headerRecordCount").innerText = history.length;

  // Split-screen live card elements
  const liveForecast = document.getElementById("liveForecastBadge");
  const liveTargetPeriod = document.getElementById("liveTargetPeriod");
  const liveConfPercent = document.getElementById("liveConfPercent");
  const liveConfBar = document.getElementById("liveConfBar");
  const liveTopNums = document.getElementById("liveTopNumbers");
  const liveTargetColor = document.getElementById("liveTargetColor");
  const liveRiskAdvice = document.getElementById("liveRiskAdvice");
  const liveRiskBadge = document.getElementById("liveRiskBadge");

  liveTargetPeriod.innerText = predData.next_period || "Next";

  if (prediction) {
    const outcome = prediction.outcome;
    liveForecast.innerText = outcome;
    liveForecast.className = "text-6xl font-black tracking-widest py-1 transition-all duration-300";

    if (outcome === "BIG") {
      liveForecast.classList.add("badge-big");
    } else if (outcome === "SMALL") {
      liveForecast.classList.add("badge-small");
    } else {
      liveForecast.classList.add("badge-neutral");
    }

    liveConfPercent.innerText = `${prediction.confidence}%`;
    liveConfBar.style.width = `${prediction.confidence}%`;

    // Dynamic Target Numbers & Probabilities
    const primary = prediction.primary_number;
    const probs = prediction.digit_probabilities || {};
    liveTopNums.innerHTML = (prediction.top_numbers || []).map((n, idx) => {
      const isPrimary = (n === primary);
      const prob = probs[String(n)] ? `${probs[String(n)]}%` : "";
      const cls = isPrimary
        ? "px-3 py-1 rounded-xl bg-amber-950 text-amber-300 border border-amber-500 shadow-lg font-black flex flex-col items-center"
        : (idx === 1
            ? "px-3 py-1 rounded-xl bg-slate-800 text-slate-200 border border-slate-600 shadow flex flex-col items-center"
            : "px-3 py-1 rounded-xl bg-cyan-950 text-cyan-300 border border-cyan-800 shadow flex flex-col items-center");
      return `
        <div class="${cls}" title="${isPrimary ? 'Primary Recommended Pick' : 'Alternate Cover Target'}">
          <span class="text-xl leading-tight">${n}${isPrimary ? '<span class=\"text-[11px] text-amber-400 ml-0.5\">★</span>' : ''}</span>
          <span class="text-[9px] ${isPrimary ? 'text-amber-400 font-bold' : 'text-slate-400'} leading-tight mt-0.5">${prob || (idx === 0 ? 'Pick' : 'Cover')}</span>
        </div>
      `;
    }).join(" ") || "-";

    const elDigitReason = document.getElementById("liveDigitReason");
    if (elDigitReason) {
      elDigitReason.innerText = prediction.digit_explanation || "Dynamic transitions updated";
      elDigitReason.title = prediction.digit_explanation || "";
    }

    const elColdAvoid = document.getElementById("liveColdAvoid");
    if (elColdAvoid && prediction.cold_avoid_numbers) {
      elColdAvoid.innerText = prediction.cold_avoid_numbers.length > 0 ? prediction.cold_avoid_numbers.join(", ") : "None";
    }

    // Color
    const color = prediction.predicted_color || "Red";
    let colorDot = "bg-rose-500";
    let colorText = "text-rose-400";
    if (color === "Green") {
      colorDot = "bg-emerald-500";
      colorText = "text-emerald-400";
    } else if (color === "Violet") {
      colorDot = "bg-purple-500";
      colorText = "text-purple-400";
    }
    liveTargetColor.innerHTML = `
      <span class="w-3.5 h-3.5 rounded-full ${colorDot} animate-pulse"></span>
      <span class="${colorText}">${color}</span>
    `;

    // Risk
    const risk = prediction.risk_advice || {};
    liveRiskBadge.innerText = risk.level || "Standard";
    liveRiskAdvice.innerText = risk.action || "Observe patterns.";

    // Play chime if outcome changed
    if (lastSignal && lastSignal !== outcome) {
      playBeep(700, 0.2);
    }
    lastSignal = outcome;
  }

  // Update AI Self-Training HUD
  const training = predData.training_info || {};
  const trainedSamplesBadge = document.getElementById("trainedSamplesBadge");
  if (trainedSamplesBadge && training.trained_samples !== undefined) {
    trainedSamplesBadge.innerText = `Trained: ${training.trained_samples} Draws`;
  }

  // Last verification outcome
  const lastVerifBox = document.getElementById("lastPredictionOutcome");
  const lastVerifText = document.getElementById("lastVerificationText");
  const lastEval = training.last_verification;
  if (lastVerifBox && lastVerifText) {
    if (lastEval && lastEval.hit !== null) {
      let digitBadge = "";
      if (lastEval.digit_hit === true) {
        digitBadge = ` | 🎯 Number [${lastEval.number}] HIT!`;
      } else if (lastEval.digit_hit === false) {
        digitBadge = ` | Num: [${lastEval.number}]`;
      }

      if (lastEval.hit === true) {
        lastVerifBox.className = "p-2.5 rounded-xl text-xs font-bold flex items-center justify-between bg-emerald-950/80 border border-emerald-500/60 text-emerald-300 shadow-sm";
        lastVerifText.innerText = `🏆 WIN: ${lastEval.predicted} (Came ${lastEval.number} ${lastEval.actual})${digitBadge}`;
      } else {
        lastVerifBox.className = "p-2.5 rounded-xl text-xs font-bold flex items-center justify-between bg-rose-950/80 border border-rose-500/60 text-rose-300 shadow-sm";
        lastVerifText.innerText = `❌ MISSED: ${lastEval.predicted} (Came ${lastEval.number} ${lastEval.actual})${digitBadge}`;
      }
    } else {
      lastVerifBox.className = "p-2.5 rounded-xl text-xs font-bold flex items-center justify-between bg-slate-900 border border-slate-800 text-slate-400";
      lastVerifText.innerText = "Synchronizing live verification...";
    }
  }

  // Recent prediction streak (W / L badges)
  const streakStrip = document.getElementById("predictionStreakStrip");
  const digitStreakStrip = document.getElementById("digitStreakStrip");
  const winRateText = document.getElementById("recentWinRateText");
  const recVerifs = training.recent_verifications || [];
  if (streakStrip) {
    if (recVerifs.length > 0) {
      streakStrip.innerHTML = recVerifs.map(v => {
        if (v.hit === true) {
          return `<span class="px-2 py-0.5 rounded font-mono font-black text-xs bg-emerald-950 text-emerald-300 border border-emerald-500/60" title="Period: ${v.period} | Result: ${v.number} ${v.actual}">W</span>`;
        } else if (v.hit === false) {
          return `<span class="px-2 py-0.5 rounded font-mono font-black text-xs bg-rose-950 text-rose-300 border border-rose-500/60" title="Period: ${v.period} | Result: ${v.number} ${v.actual}">L</span>`;
        }
        return "";
      }).join("");
    } else {
      streakStrip.innerHTML = `<span class="text-[11px] text-slate-500">Awaiting round verification...</span>`;
    }
  }

  // Target Number verification streak
  if (digitStreakStrip) {
    if (recVerifs.length > 0) {
      digitStreakStrip.innerHTML = recVerifs.map(v => {
        if (v.primary_hit === true) {
          return `<span class="px-1.5 py-0.5 rounded font-mono font-bold text-[10px] bg-amber-950 text-amber-300 border border-amber-500/60" title="★ Exact Primary Match: ${v.number}">★${v.number}</span>`;
        } else if (v.digit_hit === true) {
          return `<span class="px-1.5 py-0.5 rounded font-mono font-bold text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-500/60" title="Target Top-3 Match: ${v.number}">🎯${v.number}</span>`;
        } else if (v.digit_hit === false) {
          return `<span class="px-1.5 py-0.5 rounded font-mono font-normal text-[10px] bg-slate-900 text-slate-500 border border-slate-800" title="Missed target: Came ${v.number}">-${v.number}</span>`;
        }
        return "";
      }).join("");
    } else {
      digitStreakStrip.innerHTML = `<span class="text-[10px] text-slate-500">Tracking target numbers...</span>`;
    }
  }

  const accuracy = training.accuracy || {};
  if (winRateText) {
    const consAcc = accuracy.consensus || 50;
    winRateText.innerText = `${consAcc}% Win Rate`;
  }

  const elAccTargetNums = document.getElementById("accTargetNums");
  const elAccPrimaryNum = document.getElementById("accPrimaryNum");
  if (elAccTargetNums && accuracy.target_numbers !== undefined) {
    elAccTargetNums.innerText = `${accuracy.target_numbers}%`;
  }
  if (elAccPrimaryNum && accuracy.primary_target !== undefined) {
    elAccPrimaryNum.innerText = `${accuracy.primary_target}%`;
  }

  // Dynamic self-trained weights
  const weights = training.weights || {};
  const accuracy = training.accuracy || {};
  const elWeightM = document.getElementById("weightMarkov");
  const elWeightP = document.getElementById("weightPattern");
  const elWeightS = document.getElementById("weightStats");
  const elAccM = document.getElementById("accMarkov");
  const elAccP = document.getElementById("accPattern");
  const elAccS = document.getElementById("accStats");

  if (elWeightM && weights.markov !== undefined) {
    elWeightM.innerText = `${Math.round(weights.markov * 100)}%`;
    elAccM.innerText = `Acc: ${accuracy.markov || 50}%`;
  }
  if (elWeightP && weights.patterns !== undefined) {
    elWeightP.innerText = `${Math.round(weights.patterns * 100)}%`;
    elAccP.innerText = `Acc: ${accuracy.patterns || 50}%`;
  }
  if (elWeightS && weights.statistics !== undefined) {
    elWeightS.innerText = `${Math.round(weights.statistics * 100)}%`;
    elAccS.innerText = `Acc: ${accuracy.statistics || 50}%`;
  }

  // Empirical Calibration & Trap Radar rendering (learned from user verified notes)
  const calib = prediction ? (prediction.calibration || {}) : {};
  const tierStats = prediction ? (prediction.tier_stats || {}) : {};
  const tiers = tierStats.tiers || {};

  const elLiveCalib = document.getElementById("liveCalibBadge");
  const elCalibCount = document.getElementById("calibVerifiedCount");
  const elCalibZone = document.getElementById("calibZoneBadge");
  const elCalibRate = document.getElementById("calibWinRateText");
  const elCalibAlert = document.getElementById("calibAlertText");

  if (elLiveCalib && calib.zone) {
    if (calib.zone === "REVERSAL_TRAP") {
      elLiveCalib.className = "font-mono font-black text-rose-300 bg-rose-950/90 px-2.5 py-0.5 rounded border border-rose-500 shadow animate-pulse";
      elLiveCalib.innerText = `🚨 ${calib.calibrated_win_rate}% TRAP DETECTED`;
    } else if (calib.zone === "PRIME_WINDOW") {
      elLiveCalib.className = "font-mono font-black text-emerald-300 bg-emerald-950/90 px-2.5 py-0.5 rounded border border-emerald-500 shadow";
      elLiveCalib.innerText = `🏆 ${calib.calibrated_win_rate}% REAL WIN RATE (Prime)`;
    } else if (calib.zone === "EXHAUSTION_TRAP") {
      elLiveCalib.className = "font-mono font-black text-amber-300 bg-amber-950/90 px-2.5 py-0.5 rounded border border-amber-600 shadow";
      elLiveCalib.innerText = `⚠️ ${calib.calibrated_win_rate}% EXHAUSTION RISK`;
    } else if (calib.zone === "NEUTRAL_SKIP") {
      elLiveCalib.className = "font-mono font-black text-slate-300 bg-slate-900 px-2.5 py-0.5 rounded border border-slate-700 shadow";
      elLiveCalib.innerText = "⏸️ SKIP (Neutral / N)";
    } else {
      elLiveCalib.className = "font-mono font-black text-amber-300 bg-slate-900 px-2.5 py-0.5 rounded border border-amber-800/60";
      elLiveCalib.innerText = `${calib.calibrated_win_rate || 50}% (Coin-Flip)`;
    }
  }

  if (elCalibCount && tierStats.total_records) {
    elCalibCount.innerText = `${tierStats.total_records} Tests Analyzed`;
  }
  if (elCalibZone && calib.zone_name) {
    elCalibZone.innerText = calib.zone_name;
    elCalibZone.className = `px-2 py-0.5 rounded text-[10px] font-bold ${calib.zone === 'REVERSAL_TRAP' ? 'bg-rose-950 text-rose-300 border border-rose-600' : (calib.zone === 'PRIME_WINDOW' ? 'bg-emerald-950 text-emerald-300 border border-emerald-600' : 'bg-slate-800 text-slate-300')}`;
  }
  if (elCalibRate && calib.calibrated_win_rate !== undefined) {
    elCalibRate.innerText = `${calib.calibrated_win_rate}% Empirical Win Rate`;
  }
  if (elCalibAlert && calib.alert) {
    elCalibAlert.innerText = calib.alert;
  }

  // Update calibration mini-table cells
  if (tiers.coin_flip && document.getElementById("tierRateCoinFlip")) {
    document.getElementById("tierRateCoinFlip").innerText = `${tiers.coin_flip.win_rate}%`;
  }
  if (tiers.prime && document.getElementById("tierRatePrime")) {
    document.getElementById("tierRatePrime").innerText = `${tiers.prime.win_rate}%`;
  }
  if (tiers.exhaustion && document.getElementById("tierRateExhaust")) {
    document.getElementById("tierRateExhaust").innerText = `${tiers.exhaustion.win_rate}%`;
  }
  if (tiers.reversal_trap && document.getElementById("tierRateTrap")) {
    document.getElementById("tierRateTrap").innerText = `${tiers.reversal_trap.win_rate}%`;
  }


  // Sub-models breakdown (Full analytics mode)
  const markov = models.markov || {};
  const markovSignalEl = document.getElementById("markovSignal");
  if (markovSignalEl) {
    markovSignalEl.innerText = markov.signal ? `${markov.signal} (${markov.confidence}%)` : "--";
    setSignalColor(markovSignalEl, markov.signal);
    document.getElementById("markovExplanation").innerText = markov.explanation || "--";
  }

  const pattern = models.patterns || {};
  const patternEl = document.getElementById("patternName");
  if (patternEl) {
    patternEl.innerText = pattern.pattern_name || "--";
    document.getElementById("patternExplanation").innerText = pattern.explanation || "--";
  }

  const statMod = models.statistics || {};
  const statsSignalEl = document.getElementById("statsSignal");
  if (statsSignalEl) {
    statsSignalEl.innerText = statMod.signal ? `${statMod.signal} (${statMod.confidence}%)` : "--";
    setSignalColor(statsSignalEl, statMod.signal);
    document.getElementById("statsExplanation").innerText = statMod.explanation || "--";
  }

  // Render Mini Split Roadmap
  renderMiniRoadmap(history);

  // Render History Table
  renderHistoryTable(history);

  // Update Charts
  updateCharts(stats);

  if (window.lucide) lucide.createIcons();
}

function setSignalColor(el, signal) {
  el.className = "text-xs font-bold px-2 py-0.5 rounded font-mono";
  if (signal === "Big") {
    el.classList.add("bg-amber-950", "text-amber-400", "border", "border-amber-800/50");
  } else if (signal === "Small") {
    el.classList.add("bg-sky-950", "text-sky-400", "border", "border-sky-800/50");
  } else {
    el.classList.add("bg-slate-800", "text-slate-400");
  }
}

// Render Mini Split Roadmap
function renderMiniRoadmap(history) {
  const container = document.getElementById("splitRoadmap");
  if (!container) return;
  if (!history || history.length === 0) {
    container.innerHTML = `<span class="text-xs text-slate-500">No recent draws.</span>`;
    return;
  }
  const recent = history.slice(-16);
  container.innerHTML = recent.map(rec => {
    const isBig = rec.size === "Big";
    const border = isBig ? "border-big" : "border-small";
    let bg = "ball-red";
    if (rec.color === "Green") bg = "ball-green";
    else if (rec.color === "Violet") bg = "ball-violet";

    return `
      <div class="bead-item ${bg} ${border}" style="width: 32px; height: 32px; font-size: 10px;" title="${rec.period}: ${rec.number} (${rec.size})">
        <span>${rec.number}</span>
        <span class="bead-label">${isBig ? 'B' : 'S'}</span>
      </div>
    `;
  }).join("");
}

// Render History Table
function renderHistoryTable(history) {
  const tbody = document.getElementById("historyTableBody");
  if (!tbody) return;
  if (!history || history.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500">No records stored.</td></tr>`;
    return;
  }
  const reversed = [...history].reverse();
  tbody.innerHTML = reversed.map(rec => {
    const isBig = rec.size === "Big";
    const sizeBadge = isBig
      ? `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-950 text-amber-400">BIG</span>`
      : `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-sky-950 text-sky-400">SMALL</span>`;

    return `
      <tr class="hover:bg-slate-800/40">
        <td class="py-2 px-3 text-slate-300 font-semibold">${rec.period}</td>
        <td class="py-2 px-3 text-white font-bold">${rec.number}</td>
        <td class="py-2 px-3">${sizeBadge}</td>
        <td class="py-2 px-3">${rec.color}</td>
        <td class="py-2 px-3 text-right">
          <button onclick="deleteRecord('${rec.period}')" class="text-slate-500 hover:text-rose-400 transition">
            <i data-lucide="trash-2" class="w-3.5 h-3.5 inline"></i>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// Charts
function updateCharts(stats) {
  const bigCount = stats.big_count || 0;
  const smallCount = stats.small_count || 0;

  const ratioCanvas = document.getElementById("ratioMiniChart");
  if (ratioCanvas) {
    const ratioCtx = ratioCanvas.getContext("2d");
    if (ratioChartInstance) ratioChartInstance.destroy();
    ratioChartInstance = new Chart(ratioCtx, {
      type: "doughnut",
      data: {
        labels: ["Big", "Small"],
        datasets: [{
          data: [bigCount || 1, smallCount || 1],
          backgroundColor: ["#f59e0b", "#0ea5e9"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      }
    });
  }

  const freqCanvas = document.getElementById("numFreqChart");
  if (freqCanvas) {
    const freqCtx = freqCanvas.getContext("2d");
    const freqData = stats.number_frequencies || {};
    const labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    const values = labels.map(l => freqData[parseInt(l)] || 0);
    const colors = labels.map(l => {
      const n = parseInt(l);
      if (n === 0 || n === 5) return "#a855f7";
      if ([1, 3, 7, 9].includes(n)) return "#10b981";
      return "#f43f5e";
    });

    if (freqChartInstance) freqChartInstance.destroy();
    freqChartInstance = new Chart(freqCtx, {
      type: "bar",
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: colors, borderRadius: 4 }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: "#94a3b8" } },
          y: { beginAtZero: true, grid: { color: "#1e293b" }, ticks: { color: "#64748b", stepSize: 1 } }
        }
      }
    });
  }
}

// Delete Record
async function deleteRecord(period) {
  try {
    const res = await fetch("/api/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ period })
    });
    const data = await res.json();
    if (data.status === "success") {
      showAlert(`Record ${period} removed`, "success");
      renderDashboard(data);
    }
  } catch (err) {
    console.error(err);
  }
}

// Clear or Sample
async function loadSampleData() {
  const res = await fetch("/api/clear", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "sample" })
  });
  const data = await res.json();
  renderDashboard(data);
  showAlert("Sample draws loaded", "success");
}

async function clearAllData() {
  if (!confirm("Clear all historical records?")) return;
  const res = await fetch("/api/clear", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "empty" })
  });
  const data = await res.json();
  renderDashboard(data);
  showAlert("History cleared", "warning");
}

// Dropzone OCR
function initDropZone() {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("imageInput");
  if (!dropZone || !fileInput) return;

  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("border-cyan-400");
  });
  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("border-cyan-400");
  });
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("border-cyan-400");
    if (e.dataTransfer.files.length > 0) uploadImageFile(e.dataTransfer.files[0]);
  });
}

function handleFileSelect(e) {
  if (e.target.files.length > 0) uploadImageFile(e.target.files[0]);
}

async function uploadImageFile(file) {
  const statusEl = document.getElementById("uploadStatus");
  statusEl.className = "text-xs p-3 rounded-lg border bg-cyan-950 text-cyan-300 border-cyan-800 block";
  statusEl.innerHTML = `<span class="animate-pulse">Processing image with OCR...</span>`;

  const formData = new FormData();
  formData.append("image", file);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (data.status === "success") {
      statusEl.className = "text-xs p-3 rounded-lg border bg-emerald-950 text-emerald-300 border-emerald-800 block";
      statusEl.innerText = data.message;
      renderDashboard(data);
    } else {
      statusEl.className = "text-xs p-3 rounded-lg border bg-amber-950 text-amber-300 border-amber-800 block";
      statusEl.innerText = data.message || "Failed to parse.";
    }
  } catch (err) {
    statusEl.innerText = "Error uploading screenshot.";
  }
}

// Alert banner
function showAlert(message, type = "success") {
  const banner = document.getElementById("alertBanner");
  banner.className = "p-3 rounded-xl text-xs font-semibold flex items-center justify-between block transition";
  if (type === "success") {
    banner.classList.add("bg-emerald-950/90", "text-emerald-300", "border", "border-emerald-800");
  } else if (type === "warning") {
    banner.classList.add("bg-amber-950/90", "text-amber-300", "border", "border-amber-800");
  } else {
    banner.classList.add("bg-rose-950/90", "text-rose-300", "border", "border-rose-800");
  }
  banner.innerText = message;
  setTimeout(() => banner.classList.add("hidden"), 3500);
}

// Log new percentage calibration test from user
async function logCalibrationTest() {
  const pctInput = document.getElementById("quickCalibPct");
  const outcomeInput = document.getElementById("quickCalibOutcome");
  if (!pctInput || !outcomeInput) return;

  const val = parseFloat(pctInput.value);
  if (isNaN(val) || val < 50 || val > 100) {
    showAlert("Please enter a valid percentage between 50% and 100%", "warning");
    return;
  }

  const outcome = outcomeInput.value;
  try {
    const res = await fetch("/api/add_calibration", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        confidence: val,
        outcome: outcome,
        note: `User logged test: ${val}% -> ${outcome}`
      })
    });
    const data = await res.json();
    if (data.status === "success") {
      showAlert(`Recorded test: ${val}% -> ${outcome}`, "success");
      pctInput.value = "";
      syncLiveGame(); // re-evaluate and update dashboard
    } else {
      showAlert("Failed to save calibration test", "danger");
    }
  } catch (err) {
    console.error(err);
    showAlert("Server error saving test result", "danger");
  }
}

