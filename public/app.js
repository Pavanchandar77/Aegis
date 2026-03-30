/* ═══════════════════════════════════════════════════════════════
   AEGIS UI — Dashboard controller, animations, demo mode
   Depends on engine.js (loaded first)
   ═══════════════════════════════════════════════════════════════ */

const AEGIS = {
  prices: new PriceEngine(),
  agents: [new MomentumAgent(), new MeanRevAgent(), new ConservativeAgent()],
  risk: new RiskEngine(),
  reputation: new ReputationSystem(),
  erc: new ERC8004Registry(),
  decisions: [],
  running: false,
  demoRunning: false,
  priceInterval: null,
  agentTimers: {},
  startTime: Date.now(),
  totalCapitalProtected: 0,

  // ── Initialize ──
  init() {
    this.agents.forEach(a => this.erc.registerAgent(a));
    this.renderAgentCards();
    this.updatePriceTickers();
    this.updateMetricsBar();
    this.renderERC();
    this.drawGauge(0);
    this.startPriceTicker();
  },

  // ── Price Ticker (always runs) ──
  startPriceTicker() {
    if (this.priceInterval) return;
    this.priceInterval = setInterval(() => {
      this.prices.tick();
      this.updatePriceTickers();
      this.updateMetricsBar();
    }, 5000);
  },

  // ── Simulation Control ──
  toggleSimulation() {
    if (this.running) this.stopSimulation();
    else this.startSimulation();
  },
  startSimulation() {
    this.running = true;
    document.getElementById('btnSimLabel').textContent = 'STOP';
    document.getElementById('feedEmpty').style.display = 'none';
    this.agents.forEach(a => {
      this._scheduleAgent(a);
    });
  },
  stopSimulation() {
    this.running = false;
    this.demoRunning = false;
    document.getElementById('btnSimLabel').textContent = 'START';
    document.getElementById('btnDemo').classList.remove('running');
    document.getElementById('btnDemo').innerHTML = '<span class="btn-icon">🚀</span> DEMO MODE';
    Object.values(this.agentTimers).forEach(t => clearTimeout(t));
    this.agentTimers = {};
  },
  _scheduleAgent(agent) {
    if (!this.running) return;
    const delay = agent.nextTradeIn;
    this.agentTimers[agent.id] = setTimeout(() => {
      this._agentTick(agent);
      agent.nextTradeIn = agent._randInterval();
      this._scheduleAgent(agent);
    }, delay);
  },
  _agentTick(agent) {
    agent.checkUnsuspend();
    if (agent.isSuspended()) { this.renderAgentCards(); return; }
    const proposal = agent.generateProposal(this.prices);
    if (!proposal) return;
    this.processProposal(proposal, agent);
  },

  // ── Core Processing ──
  processProposal(proposal, agent) {
    const result = this.risk.evaluate(proposal, agent, this.prices);
    const wouldProfit = Math.random() > 0.45;
    this.reputation.updateTrust(agent, result.decision, wouldProfit);
    this.erc.addArtifact(proposal, result);
    this.erc.updateReputation(agent.id, agent.trust);
    if (result.decision !== 'APPROVE') {
      this.totalCapitalProtected += result.capitalPreserved;
    }
    const entry = { proposal, result, agent: agent.id, agentName: agent.name, timestamp: Date.now() };
    this.decisions.unshift(entry);
    if (this.decisions.length > 50) this.decisions.pop();
    this._handleDecisionUI(entry);
    this.renderAgentCards();
    this.updateMetricsBar();
    this.renderRiskComponents(result);
    this.drawGauge(result.riskScore);
    this.renderERC();
    this.renderArtifacts();
  },

  // ── Decision UI Effects ──
  _handleDecisionUI(entry) {
    const { result, proposal } = entry;
    this.renderTradeFeed();
    if (result.decision === 'APPROVE') {
      SFX.approve();
      document.body.classList.add('flash-green');
      setTimeout(() => document.body.classList.remove('flash-green'), 600);
      this._showToast(`✓ Approved — executing ${proposal.action} ${proposal.asset}`, proposal.size + '% position');
    } else if (result.decision === 'REDUCE') {
      SFX.reduce();
      this._showToast(`⚠ Reduced — ${proposal.asset} ${proposal.action}`, `Size cut to ${result.reducedSize}%`);
      this.updateWhatIf(result, proposal);
    } else if (result.decision === 'BLOCK') {
      SFX.block();
      document.body.classList.add('flash-red');
      setTimeout(() => document.body.classList.remove('flash-red'), 1000);
      this._showBlockOverlay(result);
      this.updateWhatIf(result, proposal);
    } else if (result.decision === 'HARD_BLOCK') {
      SFX.hardBlock();
      document.body.classList.add('shake');
      setTimeout(() => document.body.classList.remove('shake'), 500);
      document.body.classList.add('flash-red');
      setTimeout(() => document.body.classList.remove('flash-red'), 1000);
      this._showBlockOverlay(result, true);
      this._showHardBlockBanner(entry);
      this.updateWhatIf(result, proposal);
    }
  },

  _showBlockOverlay(result, isHard = false) {
    const ov = document.getElementById('blockOverlay');
    document.getElementById('overlayTitle').textContent = isHard ? '🚨 AGENT SUSPENDED' : '⛔ TRADE BLOCKED';
    document.getElementById('overlayTitle').style.color = isHard ? 'var(--hardblock)' : 'var(--block)';
    document.getElementById('overlayRisk').textContent = result.riskScore.toFixed(2);
    document.getElementById('overlayCapital').textContent = '$' + result.capitalPreserved.toLocaleString();
    ov.style.display = 'flex';
    setTimeout(() => { ov.classList.add('hiding'); setTimeout(() => { ov.style.display = 'none'; ov.classList.remove('hiding'); }, 400); }, 3000);
  },

  _showHardBlockBanner(entry) {
    const agent = this.agents.find(a => a.id === entry.agent);
    const banner = document.getElementById('hardblockBanner');
    document.getElementById('hbText').textContent = `${agent.name.toUpperCase()} SUSPENDED`;
    document.getElementById('hbReason').textContent = 'Reason: ' + entry.result.explanation;
    banner.style.display = 'flex';
    const updateTimer = () => {
      const rem = agent.getSuspendRemaining();
      if (rem <= 0) { banner.style.display = 'none'; return; }
      const min = Math.floor(rem / 60000);
      const sec = Math.floor((rem % 60000) / 1000);
      document.getElementById('hbTimer').textContent = `${min}:${sec.toString().padStart(2, '0')}`;
      requestAnimationFrame(updateTimer);
    };
    updateTimer();
  },

  _showToast(text, detail) {
    const c = document.getElementById('toastContainer');
    const t = document.createElement('div');
    t.className = 'approve-toast';
    t.innerHTML = `<span class="toast-icon">✓</span><div><div class="toast-text">${text}</div><div class="toast-detail">${detail}</div></div>`;
    c.appendChild(t);
    setTimeout(() => { t.classList.add('exiting'); setTimeout(() => t.remove(), 300); }, 2500);
  },

  // ── Render Functions ──
  fmt(n, d=2) { return Number(n).toLocaleString('en-US', {minimumFractionDigits:d, maximumFractionDigits:d}); },

  updatePriceTickers() {
    ['BTC', 'ETH', 'SOL'].forEach(sym => {
      const key = sym + '/USD';
      const a = this.prices.assets[key];
      document.getElementById('ticker'+sym+'Price').textContent = '$' + this.fmt(a.price);
      const pct = a.history.length > 1 ? ((a.price - a.history[a.history.length-2]) / a.history[a.history.length-2] * 100) : 0;
      const el = document.getElementById('ticker'+sym+'Change');
      el.textContent = (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%';
      el.className = 'ticker-change ' + (pct >= 0 ? 'up' : 'down');
    });
  },

  updateMetricsBar() {
    document.getElementById('metCapitalProtected').textContent = '$' + this.fmt(this.totalCapitalProtected, 0);
    const app = this.agents.reduce((s,a) => s+a.approved, 0);
    const red = this.agents.reduce((s,a) => s+a.reduced, 0);
    const blk = this.agents.reduce((s,a) => s+a.blocked, 0);
    document.getElementById('metTrades').innerHTML = `<span style="color:var(--approve)">${app}</span> / <span style="color:var(--reduce)">${red}</span> / <span style="color:var(--block)">${blk}</span>`;
    // System risk level
    const avgVol = ['BTC/USD','ETH/USD','SOL/USD'].reduce((s,k) => s + this.prices.getVolatility(k), 0) / 3;
    let level = 'low', color = 'low';
    if (avgVol > 0.04) { level = 'CRITICAL'; color = 'critical'; }
    else if (avgVol > 0.025) { level = 'HIGH'; color = 'high'; }
    else if (avgVol > 0.012) { level = 'MEDIUM'; color = 'medium'; }
    else { level = 'LOW'; color = 'low'; }
    document.getElementById('metRiskLevel').innerHTML = `<span class="risk-level-badge ${color}">${level}</span>`;
    // Drawdown
    const maxDd = Math.max(...['BTC/USD','ETH/USD','SOL/USD'].map(k => this.prices.getDrawdown(k)));
    const ddEl = document.getElementById('metDrawdown');
    ddEl.textContent = (maxDd * 100).toFixed(1) + '%';
    ddEl.className = 'metric-value ' + (maxDd > 0.1 ? 'red' : maxDd > 0.05 ? 'amber' : 'green');
    // Uptime
    const elapsed = Date.now() - this.startTime;
    const hrs = Math.floor(elapsed / 3600000);
    const mins = Math.floor((elapsed % 3600000) / 60000);
    document.getElementById('metUptime').textContent = `${hrs}h ${mins}m`;
    // Active agents
    const active = this.agents.filter(a => a.status !== 'SUSPENDED').length;
    const aaEl = document.getElementById('metActiveAgents');
    aaEl.textContent = `${active}/3`;
    aaEl.className = 'metric-value ' + (active < 3 ? 'red' : 'green');
  },

  renderAgentCards() {
    const grid = document.getElementById('agentsGrid');
    grid.innerHTML = this.agents.map(a => {
      const tc = a.trust >= 80 ? 'var(--approve)' : a.trust >= 60 ? 'var(--reduce)' : a.trust >= 40 ? 'var(--block)' : 'var(--suspended)';
      const statusCls = a.status === 'ACTIVE' ? 'active' : a.status === 'RESTRICTED' ? 'restricted' : 'suspended-badge';
      const cardCls = a.status === 'SUSPENDED' ? 'suspended' : a.status === 'RESTRICTED' ? 'restricted' : '';
      let suspensionHTML = '';
      if (a.status === 'SUSPENDED') {
        const rem = a.getSuspendRemaining();
        const min = Math.floor(rem / 60000);
        const sec = Math.floor((rem % 60000) / 1000);
        const pct = Math.max(0, rem / 300000 * 100);
        suspensionHTML = `<div class="suspension-timer"><div class="countdown">${min}:${sec.toString().padStart(2,'0')}</div><div class="countdown-label">Resuming in</div><div class="suspension-bar"><div class="suspension-bar-fill" style="width:${pct}%"></div></div></div>`;
      }
      return `<div class="agent-card ${cardCls}">
        <div class="agent-card-header">
          <div><div class="agent-name">🤖 ${a.name}</div><div class="agent-type">${a.type}</div></div>
          <span class="agent-status ${statusCls}">${a.status}</span>
        </div>
        <div class="trust-score">
          <div class="trust-score-value" style="color:${tc}">${a.trust}</div>
          <div class="trust-score-label">Trust Score</div>
          <div class="trust-bar"><div class="trust-fill" style="width:${a.trust}%;background:${tc}"></div></div>
        </div>
        <div class="agent-stats">
          <div class="agent-stat"><div class="agent-stat-val" style="color:var(--text)">${a.totalProposed}</div><div class="agent-stat-label">Proposed</div></div>
          <div class="agent-stat"><div class="agent-stat-val" style="color:var(--approve)">${a.approved}</div><div class="agent-stat-label">Approved</div></div>
          <div class="agent-stat"><div class="agent-stat-val" style="color:var(--block)">${a.blocked}</div><div class="agent-stat-label">Blocked</div></div>
          <div class="agent-stat"><div class="agent-stat-val" style="color:${a.pnl >= 0 ? 'var(--approve)' : 'var(--block)'}">${a.pnl >= 0 ? '+' : ''}$${Math.abs(a.pnl).toFixed(0)}</div><div class="agent-stat-label">PnL</div></div>
        </div>
        ${suspensionHTML}
      </div>`;
    }).join('');
  },

  renderTradeFeed() {
    const feed = document.getElementById('tradeFeed');
    document.getElementById('feedEmpty').style.display = 'none';
    const existing = feed.querySelectorAll('.trade-entry');
    // Only render last 15
    const toRender = this.decisions.slice(0, 15);
    feed.innerHTML = toRender.map(d => {
      const cls = d.result.decision.toLowerCase().replace('hard_block', 'hardblock');
      const decColor = d.result.decision === 'APPROVE' ? 'var(--approve)' : d.result.decision === 'REDUCE' ? 'var(--reduce)' : 'var(--block)';
      const riskColor = d.result.riskScore > 0.6 ? 'var(--block)' : d.result.riskScore > 0.3 ? 'var(--reduce)' : 'var(--approve)';
      let extra = '';
      if (d.result.decision === 'BLOCK' || d.result.decision === 'HARD_BLOCK') {
        extra = `<div class="trade-reason">⛔ ${d.result.explanation}</div><div class="trade-capital">🛡️ Capital preserved: $${d.result.capitalPreserved.toLocaleString()}</div>`;
      }
      return `<div class="trade-entry ${cls}">
        <div class="trade-entry-header">
          <span class="trade-decision" style="color:${decColor}">${d.result.decision === 'HARD_BLOCK' ? '🚨 HARD BLOCK' : d.result.decision === 'BLOCK' ? '🚫 BLOCKED' : d.result.decision === 'REDUCE' ? '⚠️ REDUCED' : '✅ APPROVED'}</span>
          <span class="trade-risk" style="color:${riskColor}">RISK: ${(d.result.riskScore*100).toFixed(0)}</span>
        </div>
        <div class="trade-detail">${d.agentName} → ${d.proposal.action} ${d.proposal.asset} @ $${this.fmt(this.prices.getPrice(d.proposal.asset))} · ${d.proposal.size}% · ${d.proposal.leverage}x</div>
        ${extra}
      </div>`;
    }).join('');
  },

  updateWhatIf(result, proposal) {
    const c = document.getElementById('whatIfContent');
    const price = this.prices.getPrice(proposal.asset);
    const posDollars = result.positionDollars;
    const profitPct = (result.potentialProfit / posDollars * 100).toFixed(1);
    const lossPct = (result.worstCase / posDollars * 100).toFixed(1);
    const probProfit = Math.max(20, Math.min(75, 50 - result.riskScore * 40)).toFixed(0);
    c.innerHTML = `<div class="whatif-grid">
      <div class="whatif-card whatif-allowed">
        <div class="whatif-title" style="color:var(--block)">⚠️ IF ALLOWED</div>
        <div class="whatif-row"><span class="whatif-label">Potential Profit</span><span class="whatif-val" style="color:var(--approve)">+$${result.potentialProfit.toLocaleString()}</span></div>
        <div class="whatif-row"><span class="whatif-label">Worst-Case Loss</span><span class="whatif-val" style="color:var(--block)">-$${result.worstCase.toLocaleString()}</span></div>
        <div class="whatif-row"><span class="whatif-label">Profit Probability</span><span class="whatif-val" style="color:var(--text-muted)">${probProfit}%</span></div>
        <div class="whatif-row"><span class="whatif-label">Risk/Reward</span><span class="whatif-val" style="color:var(--reduce)">${(result.worstCase / Math.max(result.potentialProfit,1)).toFixed(1)}:1</span></div>
      </div>
      <div class="whatif-card whatif-blocked">
        <div class="whatif-title" style="color:var(--approve)">🛡️ IF BLOCKED</div>
        <div class="whatif-row"><span class="whatif-label">Capital Preserved</span><span class="whatif-val" style="color:var(--approve)">$${result.capitalPreserved.toLocaleString()}</span></div>
        <div class="whatif-row"><span class="whatif-label">Loss Avoided</span><span class="whatif-val" style="color:var(--approve)">$${result.worstCase.toLocaleString()}</span></div>
        <div class="whatif-row"><span class="whatif-label">Drawdown Prevented</span><span class="whatif-val" style="color:var(--accent)">${lossPct}%</span></div>
      </div>
    </div>`;
  },

  renderRiskComponents(result) {
    const c = document.getElementById('riskComponents');
    const comps = [
      { label: 'Position Risk', val: result.components.position_risk, weight: '30%' },
      { label: 'Leverage Risk', val: result.components.leverage_risk, weight: '25%' },
      { label: 'Volatility Risk', val: result.components.volatility_risk, weight: '25%' },
      { label: 'Drawdown Risk', val: result.components.drawdown_risk, weight: '20%' }
    ];
    c.innerHTML = comps.map(comp => {
      const pct = Math.min(comp.val / 0.3 * 100, 100);
      const col = pct > 66 ? 'var(--block)' : pct > 33 ? 'var(--reduce)' : 'var(--approve)';
      return `<div style="margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--text-muted);margin-bottom:2px;">
          <span>${comp.label} <span style="color:var(--text-dim)">(${comp.weight})</span></span>
          <span style="color:${col};font-weight:800;font-family:var(--mono)">${(comp.val*100).toFixed(1)}%</span>
        </div>
        <div style="width:100%;height:5px;background:rgba(30,41,59,0.6);border-radius:3px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:${col};border-radius:3px;transition:width 0.8s ease-out;"></div>
        </div>
      </div>`;
    }).join('');
  },

  drawGauge(riskScore) {
    const canvas = document.getElementById('riskGauge');
    const ctx = canvas.getContext('2d');
    const r100 = Math.round(riskScore * 100);
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h - 10;
    const radius = Math.min(w, h) - 30;
    ctx.clearRect(0, 0, w, h);
    // BG arc
    ctx.beginPath(); ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI); ctx.lineWidth = 14; ctx.strokeStyle = '#111827'; ctx.stroke();
    // Zone arcs
    [[0,0.3,'rgba(0,200,150,0.12)'],[0.3,0.6,'rgba(255,184,0,0.12)'],[0.6,0.8,'rgba(255,68,68,0.12)'],[0.8,1,'rgba(139,0,0,0.15)']].forEach(([s,e,c]) => {
      ctx.beginPath(); ctx.arc(cx, cy, radius, Math.PI + s * Math.PI, Math.PI + e * Math.PI); ctx.lineWidth = 14; ctx.strokeStyle = c; ctx.stroke();
    });
    // Value arc
    const color = r100 >= 80 ? '#8B0000' : r100 >= 60 ? '#FF4444' : r100 >= 30 ? '#FFB800' : '#00C896';
    ctx.beginPath(); ctx.arc(cx, cy, radius, Math.PI, Math.PI + (r100/100) * Math.PI); ctx.lineWidth = 14; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.stroke();
    const vEl = document.getElementById('riskGaugeValue');
    vEl.textContent = r100;
    vEl.style.color = color;
  },

  renderERC() {
    const c = document.getElementById('ercIdentities');
    c.innerHTML = this.agents.map(a => {
      const e = this.erc.agents[a.id];
      if (!e) return '';
      return `<div class="erc-identity">
        <div class="erc-row"><span class="erc-label">Agent</span><span class="erc-value" style="color:var(--text)">${a.name}</span></div>
        <div class="erc-row"><span class="erc-label">Wallet</span><span class="erc-value">${e.walletAddress.slice(0,8)}...${e.walletAddress.slice(-6)}</span></div>
        <div class="erc-row"><span class="erc-label">Reg. Block</span><span class="erc-value">#${e.registrationBlock.toLocaleString()}</span></div>
        <div class="erc-row"><span class="erc-label">Reputation</span><span class="erc-value" style="color:${a.trust >= 60 ? 'var(--approve)' : 'var(--block)'}">${a.trust}/100</span></div>
      </div>`;
    }).join('');
  },

  renderArtifacts() {
    const c = document.getElementById('artifactsList');
    const arts = this.erc.artifacts.slice(0, 8);
    if (!arts.length) return;
    c.innerHTML = arts.map((a, i) => {
      const decColor = a.decision === 'APPROVE' ? 'var(--approve)' : a.decision === 'REDUCE' ? 'var(--reduce)' : 'var(--block)';
      return `<div class="artifact-entry">
        <div class="artifact-info">
          <div style="font-weight:700;color:${decColor}">${a.decision} · ${a.asset} ${a.action}</div>
          <div class="artifact-hash">${a.hash.slice(0,18)}...</div>
        </div>
        <button class="btn-verify" onclick="AEGIS.showVerify(${i})">Verify</button>
      </div>`;
    }).join('');
  },

  showVerify(idx) {
    const a = this.erc.artifacts[idx];
    if (!a) return;
    const m = document.getElementById('verifyModal');
    const b = document.getElementById('verifyBody');
    const decColor = a.decision === 'APPROVE' ? 'var(--approve)' : 'var(--block)';
    const compHTML = Object.entries(a.components || {}).map(([k,v]) => {
      return '<div class="verify-row"><span style="color:var(--text-dim)">' + k + '</span><span style="font-family:var(--mono)">' + (v*100).toFixed(1) + '%</span></div>';
    }).join('');
    const rulesHTML = (a.triggeredRules || []).length
      ? '<div style="margin-top:8px;padding:6px 10px;background:var(--block-bg);border-radius:4px;font-size:10px;color:var(--block);">⛔ ' + a.triggeredRules.join(' · ') + '</div>'
      : '';
    b.innerHTML = '<div class="verify-row"><span style="color:var(--text-dim)">Trade ID</span><span style="font-family:var(--mono);font-size:10px;color:var(--accent)">' + a.tradeId + '</span></div>'
      + '<div class="verify-row"><span style="color:var(--text-dim)">Decision</span><span style="color:' + decColor + ';font-weight:800">' + a.decision + '</span></div>'
      + '<div class="verify-row"><span style="color:var(--text-dim)">Risk Score</span><span style="font-family:var(--mono)">' + a.riskScore + '</span></div>'
      + '<div class="verify-row"><span style="color:var(--text-dim)">Agent</span><span>' + a.agent + '</span></div>'
      + '<div class="verify-row"><span style="color:var(--text-dim)">Asset</span><span>' + a.asset + ' ' + a.action + '</span></div>'
      + '<div class="verify-row"><span style="color:var(--text-dim)">Timestamp</span><span style="font-size:10px">' + a.timestamp + '</span></div>'
      + '<div class="verify-row"><span style="color:var(--text-dim)">Hash</span><span style="font-family:var(--mono);font-size:9px;color:var(--accent)">' + a.hash + '</span></div>'
      + '<div style="margin-top:10px;padding:10px;background:rgba(10,14,26,0.5);border-radius:8px;">'
      + '<div style="font-size:9px;color:var(--text-dim);letter-spacing:1px;margin-bottom:6px;">RISK COMPONENTS</div>'
      + compHTML + '</div>' + rulesHTML;
    m.style.display = 'flex';
  },
  closeVerify() { document.getElementById('verifyModal').style.display = 'none'; },

  // ── Demo Mode (scripted 60s sequence) ──
  toggleDemo() {
    if (this.demoRunning) { this.stopSimulation(); return; }
    this.reset();
    this.demoRunning = true;
    // Immediately show ~$42k capital protected for demo presentation
    this.totalCapitalProtected = 41850;
    this.updateMetricsBar();
    document.getElementById('btnDemo').classList.add('running');
    document.getElementById('btnDemo').innerHTML = '<span class="btn-icon">⏹</span> STOP DEMO';
    document.getElementById('feedEmpty').style.display = 'none';
    this.running = true;
    document.getElementById('btnSimLabel').textContent = 'STOP';

    const mom = this.agents[0], mr = this.agents[1], con = this.agents[2];
    const seq = [
      // 0:05 — Momentum fires aggressive BTC trade
      [5000, () => {
        const p = { agentId:'momentum', asset:'BTC/USD', action:'BUY', size:38, leverage:4.5,
          reasoning:'Massive 3.2% surge detected — all-in with high leverage!',
          timestamp: new Date().toISOString(), proposalId:'demo-mom-1-'+Date.now() };
        this.processProposal(p, mom);
      }],
      // 0:15 — Conservative fires safe trade
      [10000, () => {
        const p = { agentId:'conservative', asset:'ETH/USD', action:'BUY', size:6, leverage:1.2,
          reasoning:'Stable conditions, 0.8% MA deviation, low vol — safe entry',
          timestamp: new Date().toISOString(), proposalId:'demo-con-1-'+Date.now() };
        this.processProposal(p, con);
      }],
      // 0:22 — MeanRev moderate trade
      [7000, () => {
        const p = { agentId:'meanrev', asset:'SOL/USD', action:'SELL', size:14, leverage:2.1,
          reasoning:'SOL 1.8% above 20-MA — reversion sell with moderate sizing',
          timestamp: new Date().toISOString(), proposalId:'demo-mr-1-'+Date.now() };
        this.processProposal(p, mr);
      }],
      // 0:30 — Momentum fires RECKLESS trade → HARD BLOCK (large position = big capitalPreserved)
      [8000, () => {
        mom.trust = 35; // force low trust for hard block
        const p = { agentId:'momentum', asset:'BTC/USD', action:'BUY', size:48, leverage:5,
          reasoning:'YOLO — doubling down on BTC breakout with max leverage!',
          timestamp: new Date().toISOString(), proposalId:'demo-mom-2-'+Date.now() };
        this.processProposal(p, mom);
      }],
      // 0:40 — Conservative makes another safe trade
      [10000, () => {
        const p = { agentId:'conservative', asset:'BTC/USD', action:'BUY', size:5, leverage:1.1,
          reasoning:'BTC stabilized post-volatility, safe re-entry at low exposure',
          timestamp: new Date().toISOString(), proposalId:'demo-con-2-'+Date.now() };
        this.processProposal(p, con);
      }],
      // 0:48 — MeanRev moderate trade
      [8000, () => {
        const p = { agentId:'meanrev', asset:'ETH/USD', action:'BUY', size:16, leverage:2.5,
          reasoning:'ETH reverting to mean after dip — moderate buy signal',
          timestamp: new Date().toISOString(), proposalId:'demo-mr-2-'+Date.now() };
        this.processProposal(p, mr);
      }],
      // 0:55 — End demo, switch to continuous
      [7000, () => {
        this.demoRunning = false;
        document.getElementById('btnDemo').classList.remove('running');
        document.getElementById('btnDemo').innerHTML = '<span class="btn-icon">🚀</span> DEMO MODE';
        // Start continuous simulation
        this.agents.forEach(a => this._scheduleAgent(a));
      }]
    ];

    let delay = 0;
    seq.forEach(([wait, fn]) => {
      delay += wait;
      setTimeout(() => { if (this.running) fn(); }, delay);
    });
  },

  // ── Reset ──
  reset() {
    this.stopSimulation();
    this.prices = new PriceEngine();
    this.agents = [new MomentumAgent(), new MeanRevAgent(), new ConservativeAgent()];
    this.risk = new RiskEngine();
    this.erc = new ERC8004Registry();
    this.agents.forEach(a => this.erc.registerAgent(a));
    this.decisions = [];
    this.totalCapitalProtected = 0;
    this.startTime = Date.now();
    document.getElementById('feedEmpty').style.display = 'block';
    document.getElementById('tradeFeed').querySelectorAll('.trade-entry').forEach(e => e.remove());
    document.getElementById('whatIfContent').innerHTML = '<div style="text-align:center;padding:30px 0;color:var(--text-dim);font-size:12px;">Waiting for a BLOCK decision to analyze...</div>';
    document.getElementById('artifactsList').innerHTML = '<div style="text-align:center;padding:20px 0;color:var(--text-dim);font-size:12px;">Artifacts will appear as trades are processed...</div>';
    this.renderAgentCards();
    this.updatePriceTickers();
    this.updateMetricsBar();
    this.renderERC();
    this.drawGauge(0);
    this.renderRiskComponents({ components: { position_risk: 0, leverage_risk: 0, volatility_risk: 0, drawdown_risk: 0 } });
  }
};

// ── Boot ──
document.addEventListener('DOMContentLoaded', () => AEGIS.init());
