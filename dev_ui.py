"""Dev UI v2 — single-page management interface for MAKO sub-agents."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

# Inline the HTML to avoid static file serving issues
_DEV_UI_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MAKO Dev UI v2</title>
<style>
  :root {
    --bg: #0d1117; --bg2: #161b22; --bg3: #21262d; --border: #30363d;
    --text: #c9d1d9; --text2: #8b949e; --accent: #58a6ff; --accent2: #1f6feb;
    --ok: #3fb950; --warn: #d29922; --err: #f85149; --purple: #bc8cff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.5; min-height: 100vh;
  }
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0; border-bottom: 1px solid var(--border); margin-bottom: 20px;
  }
  header h1 { font-size: 20px; font-weight: 600; letter-spacing: -0.5px; }
  header h1 span { color: var(--accent); }
  .version { font-size: 11px; color: var(--text2); background: var(--bg3); padding: 2px 8px; border-radius: 12px; margin-left: 8px; }
  .auth-bar {
    background: var(--bg2); border: 1px solid var(--border); border-radius: 8px;
    padding: 12px 16px; margin-bottom: 20px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
  }
  .auth-bar label { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.5px; }
  .auth-bar input {
    background: var(--bg3); border: 1px solid var(--border); color: var(--text);
    padding: 6px 10px; border-radius: 6px; font-size: 13px; font-family: monospace; flex: 1; min-width: 200px;
  }
  .auth-bar input:focus { outline: none; border-color: var(--accent); }
  .auth-bar button {
    background: var(--accent2); color: #fff; border: none; padding: 6px 14px;
    border-radius: 6px; font-size: 13px; cursor: pointer; font-weight: 500;
  }
  .auth-bar button:hover { background: var(--accent); }
  .auth-bar button.secondary { background: var(--bg3); color: var(--text); border: 1px solid var(--border); }
  .auth-bar button.secondary:hover { background: var(--border); }
  .auth-status { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
  .auth-status.ok { background: rgba(63,185,80,0.15); color: var(--ok); }
  .auth-status.err { background: rgba(248,81,73,0.15); color: var(--err); }
  .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin-bottom: 20px; overflow-x: auto; }
  .tab {
    padding: 8px 16px; font-size: 13px; font-weight: 500; color: var(--text2);
    cursor: pointer; border-bottom: 2px solid transparent; white-space: nowrap;
    display: flex; align-items: center; gap: 6px;
  }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
  .tab .badge { font-size: 10px; padding: 1px 6px; border-radius: 10px; min-width: 18px; text-align: center; }
  .tab .badge { background: var(--err); color: #fff; }
  .tab .badge.ok { background: var(--ok); }
  .tab .badge.warn { background: var(--warn); color: #000; }
  .panel { display: none; }
  .panel.active { display: block; }
  .card { background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 16px; }
  .card h3 { font-size: 14px; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
  .card h3 .icon { font-size: 16px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; padding: 8px 12px; color: var(--text2); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
  td { padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(88,166,255,0.03); }
  .mono { font-family: 'SFMono-Regular', Consolas, monospace; font-size: 12px; }
  .small { font-size: 11px; color: var(--text2); }
  .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; }
  .tag.ok { background: rgba(63,185,80,0.15); color: var(--ok); }
  .tag.err { background: rgba(248,81,73,0.15); color: var(--err); }
  .tag.warn { background: rgba(210,153,34,0.15); color: var(--warn); }
  .tag.info { background: rgba(88,166,255,0.15); color: var(--accent); }
  .tag.purple { background: rgba(188,140,255,0.15); color: var(--purple); }
  .btn { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; cursor: pointer; border: 1px solid var(--border); background: var(--bg3); color: var(--text); }
  .btn:hover { background: var(--border); }
  .btn.primary { background: var(--accent2); color: #fff; border-color: var(--accent2); }
  .btn.primary:hover { background: var(--accent); }
  .btn.ok { background: var(--ok); color: #000; border-color: var(--ok); }
  .btn.danger { background: var(--err); color: #fff; border-color: var(--err); }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  select { background: var(--bg3); border: 1px solid var(--border); color: var(--text); padding: 4px 8px; border-radius: 6px; font-size: 12px; }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .status-dot.ok { background: var(--ok); box-shadow: 0 0 6px rgba(63,185,80,0.4); }
  .status-dot.err { background: var(--err); box-shadow: 0 0 6px rgba(248,81,73,0.4); }
  .status-dot.warn { background: var(--warn); box-shadow: 0 0 6px rgba(210,153,34,0.4); }
  .toast-container { position: fixed; top: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 8px; }
  .toast { background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; font-size: 13px; max-width: 320px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); animation: slideIn 0.2s ease; }
  .toast.ok { border-color: var(--ok); } .toast.err { border-color: var(--err); } .toast.warn { border-color: var(--warn); }
  @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
  .empty { text-align: center; padding: 40px; color: var(--text2); font-size: 13px; }
  .gate-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
  .gate-mode { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg3); border-radius: 8px; }
  .gate-mode select { flex: 1; }
  .confirm-card { border-left: 3px solid var(--warn); padding-left: 12px; margin-bottom: 12px; }
  .confirm-card.critical { border-left-color: var(--err); }
  .confirm-actions { display: flex; gap: 8px; margin-top: 8px; }
  .refresh { float: right; font-size: 11px; color: var(--text2); cursor: pointer; }
  .refresh:hover { color: var(--accent); }
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; }
  pre { background: var(--bg3); padding: 12px; border-radius: 6px; font-size: 11px; overflow-x: auto; color: var(--text); font-family: monospace; }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1><span>MAKO</span> Dev UI <span class="version">v2.0</span></h1>
    <div style="display:flex;align-items:center;gap:12px;">
      <span class="status-dot" id="health-dot"></span>
      <span id="health-text" class="small">Checking...</span>
    </div>
  </header>

  <div class="auth-bar">
    <label>API Base</label>
    <input type="text" id="api-base" placeholder="http://192.168.1.100:8000" value="">
    <label>PAT Token</label>
    <input type="password" id="pat-token" placeholder="Paste your PAT here..." value="">
    <button onclick="saveAuth()">Save</button>
    <button class="secondary" onclick="clearAuth()">Clear</button>
    <span class="auth-status" id="auth-status">Not configured</span>
  </div>

  <div class="tabs">
    <div class="tab active" onclick="switchTab('agents')" id="tab-agents"><span>Agents</span></div>
    <div class="tab" onclick="switchTab('alerts')" id="tab-alerts"><span>Alerts</span><span class="badge" id="alert-badge" style="display:none">0</span></div>
    <div class="tab" onclick="switchTab('audit')" id="tab-audit"><span>Audit Log</span></div>
    <div class="tab" onclick="switchTab('gate')" id="tab-gate"><span>Confirmation Gate</span><span class="badge warn" id="gate-badge" style="display:none">0</span></div>
    <div class="tab" onclick="switchTab('health')" id="tab-health"><span>Health</span></div>
  </div>

  <div class="panel active" id="panel-agents">
    <div class="card">
      <h3><span class="icon">&#x1F916;</span> Registered Agents <span class="refresh" onclick="loadAgents()">&#x21bb; Refresh</span></h3>
      <div id="agents-loading"><span class="spinner"></span> Loading agents...</div>
      <div id="agents-content" style="display:none">
        <table><thead><tr><th>Slug</th><th>Role</th><th>Status</th><th>Mode</th><th>Depth</th><th>Last Seen</th><th>Actions</th></tr></thead><tbody id="agents-table"></tbody></table>
      </div>
      <div id="agents-empty" class="empty" style="display:none">No agents registered.</div>
    </div>
    <div class="card">
      <h3><span class="icon">&#x1F511;</span> PAT Management</h3>
      <div style="display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap;">
        <div><label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Agent Slug</label><select id="pat-agent-slug"></select></div>
        <div><label style="font-size:11px;color:var(--text2);display:block;margin-bottom:4px;">Expires (hours)</label><input type="number" id="pat-expiry" value="24" min="1" max="168" style="width:80px;background:var(--bg3);border:1px solid var(--border);color:var(--text);padding:4px 8px;border-radius:6px;font-size:12px;"></div>
        <button class="btn primary" onclick="mintPat()">Mint PAT</button>
      </div>
      <div id="pat-result" style="margin-top:12px;display:none"><div class="tag ok" style="font-family:monospace;word-break:break-all;" id="pat-display"></div></div>
    </div>
  </div>

  <div class="panel" id="panel-alerts">
    <div class="card">
      <h3><span class="icon">&#x1F6A8;</span> Unacknowledged Alerts <span class="refresh" onclick="loadAlerts()">&#x21bb; Refresh</span></h3>
      <div id="alerts-loading"><span class="spinner"></span> Loading alerts...</div>
      <div id="alerts-content" style="display:none"></div>
      <div id="alerts-empty" class="empty" style="display:none">No unacknowledged alerts. All clear!</div>
    </div>
  </div>

  <div class="panel" id="panel-audit">
    <div class="card">
      <h3><span class="icon">&#x1F4CB;</span> Recent Audit Log <span class="refresh" onclick="loadAudit()">&#x21bb; Refresh</span></h3>
      <div id="audit-loading"><span class="spinner"></span> Loading audit log...</div>
      <div id="audit-content" style="display:none">
        <table><thead><tr><th>Time</th><th>Session</th><th>Tool</th><th>Sensitivity</th><th>Mode</th><th>Action</th><th>Duration</th></tr></thead><tbody id="audit-table"></tbody></table>
      </div>
      <div id="audit-empty" class="empty" style="display:none">No audit entries found.</div>
    </div>
  </div>

  <div class="panel" id="panel-gate">
    <div class="card">
      <h3><span class="icon">&#x1F6E1;&#xFE0F;</span> Confirmation Gate</h3>
      <div class="gate-grid">
        <div class="gate-mode">
          <label style="font-size:12px;white-space:nowrap;">Global Mode:</label>
          <select id="global-mode" onchange="setGlobalMode(this.value)">
            <option value="off">off (gate ON - confirm all)</option>
            <option value="auto_infinite">auto_infinite (gate OFF)</option>
            <option value="auto_session">auto_session (gate OFF, per-session)</option>
          </select>
          <span class="tag" id="mode-tag">checking...</span>
        </div>
      </div>
      <p class="small" style="margin-top:8px;"><strong>off</strong> = every sensitive tool requires confirmation &bull; <strong>auto_infinite</strong> = gate disabled until explicitly re-enabled &bull; <strong>auto_session</strong> = gate disabled for current session only</p>
    </div>
    <div class="card">
      <h3><span class="icon">&#x23F3;</span> Pending Confirmations <span class="refresh" onclick="loadPending()">&#x21bb; Refresh</span></h3>
      <div id="pending-loading"><span class="spinner"></span> Loading...</div>
      <div id="pending-content" style="display:none"></div>
      <div id="pending-empty" class="empty" style="display:none">No pending confirmations.</div>
    </div>
  </div>

  <div class="panel" id="panel-health">
    <div class="card">
      <h3><span class="icon">&#x1F493;</span> System Health <span class="refresh" onclick="loadHealth()">&#x21bb; Refresh</span></h3>
      <div id="health-loading"><span class="spinner"></span> Loading health status...</div>
      <div id="health-content" style="display:none"><div class="gate-grid" id="health-grid"></div></div>
    </div>
    <div class="card">
      <h3><span class="icon">&#x1F4CA;</span> Raw Health JSON</h3>
      <pre id="health-raw"></pre>
    </div>
  </div>
</div>

<div class="toast-container" id="toasts"></div>

<script>
const state={apiBase:localStorage.getItem('mako_api_base')||'',pat:localStorage.getItem('mako_pat')||'',agents:[],alerts:[],audit:[],pending:[],health:null,globalMode:'off'};
document.addEventListener('DOMContentLoaded',()=>{document.getElementById('api-base').value=state.apiBase;document.getElementById('pat-token').value=state.pat;updateAuthStatus();if(state.apiBase&&state.pat){loadAll()}setInterval(()=>{if(state.apiBase&&state.pat)loadHealth(true)},30000)});
function saveAuth(){state.apiBase=document.getElementById('api-base').value.trim();state.pat=document.getElementById('pat-token').value.trim();localStorage.setItem('mako_api_base',state.apiBase);localStorage.setItem('mako_pat',state.pat);updateAuthStatus();toast('Auth saved','ok');if(state.apiBase&&state.pat)loadAll()}
function clearAuth(){state.apiBase='';state.pat='';localStorage.removeItem('mako_api_base');localStorage.removeItem('mako_pat');document.getElementById('api-base').value='';document.getElementById('pat-token').value='';updateAuthStatus();toast('Auth cleared','warn')}
function updateAuthStatus(){const el=document.getElementById('auth-status');if(state.apiBase&&state.pat){el.textContent='Ready';el.className='auth-status ok'}else{el.textContent='Not configured';el.className='auth-status err'}}
function apiHeaders(){return{'Authorization':'Bearer '+state.pat,'Content-Type':'application/json'}}
async function apiGet(path){const r=await fetch(state.apiBase+path,{headers:apiHeaders()});if(!r.ok)throw new Error(r.status+' '+r.statusText);return r.json()}
async function apiPost(path,body){const r=await fetch(state.apiBase+path,{method:'POST',headers:apiHeaders(),body:JSON.stringify(body)});if(!r.ok)throw new Error(r.status+' '+r.statusText);return r.json()}
function switchTab(name){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('tab-'+name).classList.add('active');document.getElementById('panel-'+name).classList.add('active');if(state.apiBase&&state.pat){if(name==='agents')loadAgents();if(name==='alerts')loadAlerts();if(name==='audit')loadAudit();if(name==='gate'){loadPending();detectMode()}if(name==='health')loadHealth()}}
async function loadAgents(){if(!state.apiBase||!state.pat){toast('Configure auth first','err');return}document.getElementById('agents-loading').style.display='';document.getElementById('agents-content').style.display='none';document.getElementById('agents-empty').style.display='none';try{const data=await apiGet('/agents');state.agents=Array.isArray(data)?data:(data.agents||[]);renderAgents();updatePatAgentSelect()}catch(e){toast('Failed to load agents: '+e.message,'err');document.getElementById('agents-loading').style.display='none'}}
function renderAgents(){document.getElementById('agents-loading').style.display='none';const tbody=document.getElementById('agents-table');if(!state.agents.length){document.getElementById('agents-empty').style.display='';return}document.getElementById('agents-content').style.display='';tbody.innerHTML=state.agents.map(a=>{const status=a.is_active!==false?'active':'inactive';const mode=a.mode||'off';const depth=a.delegation_depth!==undefined?a.delegation_depth:'-';const lastSeen=a.last_seen_at?timeAgo(new Date(a.last_seen_at)):'never';return`<tr><td><strong class="mono">${esc(a.slug)}</strong></td><td>${esc(a.role||'-')}</td><td><span class="tag ${status==='active'?'ok':'err'}">${status}</span></td><td><select onchange="setAgentMode('${a.slug}',this.value)" data-slug="${esc(a.slug)}"><option value="off" ${mode==='off'?'selected':''}>off</option><option value="auto_infinite" ${mode==='auto_infinite'?'selected':''}>auto_infinite</option><option value="auto_session" ${mode==='auto_session'?'selected':''}>auto_session</option></select></td><td>${depth}</td><td class="small">${lastSeen}</td><td><button class="btn primary" onclick="mintPatFor('${esc(a.slug)}')">Mint PAT</button></td></tr>`}).join('')}
function updatePatAgentSelect(){const sel=document.getElementById('pat-agent-slug');sel.innerHTML=state.agents.map(a=>`<option value="${esc(a.slug)}">${esc(a.slug)}</option>`).join('')}
async function setAgentMode(slug,mode){try{await apiPost('/agents/'+slug+'/mode',{mode});toast(slug+' mode set to '+mode,'ok')}catch(e){toast('Failed to set mode: '+e.message,'err')}}
async function mintPat(){const slug=document.getElementById('pat-agent-slug').value;if(!slug){toast('Select an agent','warn');return}await mintPatFor(slug)}
async function mintPatFor(slug){try{const hours=parseInt(document.getElementById('pat-expiry').value)||24;const result=await apiPost('/agents/'+slug+'/pat/mint',{expires_in_hours:hours});const pat=result.pat||result.token||result.access_token||JSON.stringify(result);document.getElementById('pat-result').style.display='';document.getElementById('pat-display').textContent=pat;toast('PAT minted for '+slug,'ok')}catch(e){toast('Failed to mint PAT: '+e.message,'err')}}
async function loadAlerts(){if(!state.apiBase||!state.pat)return;document.getElementById('alerts-loading').style.display='';document.getElementById('alerts-content').style.display='none';document.getElementById('alerts-empty').style.display='none';try{const data=await apiGet('/inbox/alerts');state.alerts=Array.isArray(data)?data:(data.alerts||[]);renderAlerts()}catch(e){document.getElementById('alerts-loading').style.display='none';document.getElementById('alerts-empty').style.display='';document.getElementById('alerts-empty').textContent='Error: '+e.message}}
function renderAlerts(){document.getElementById('alerts-loading').style.display='none';const badge=document.getElementById('alert-badge');if(!state.alerts.length){document.getElementById('alerts-empty').style.display='';badge.style.display='none';return}badge.style.display='';badge.textContent=state.alerts.length;document.getElementById('alerts-content').style.display='';document.getElementById('alerts-content').innerHTML=state.alerts.map(a=>{const sev=a.severity||'warning';const created=a.created_at?timeAgo(new Date(a.created_at)):'just now';return`<div class="confirm-card ${sev==='critical'?'critical':''}" style="background:var(--bg3);padding:12px;border-radius:6px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;align-items:center;"><strong>${esc(a.title||a.alert_type||'Alert')}</strong><span class="tag ${sev==='critical'?'err':'warn'}">${esc(sev)}</span></div><p class="small" style="margin-top:4px;">${esc(a.message||a.description||'')}</p><div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;"><span class="small">${esc(a.source||'')}&bull;${created}</span><button class="btn ok" onclick="ackAlert('${a.id}')">Acknowledge</button></div></div>`}).join('')}
async function ackAlert(id){try{await apiPost('/alerts/'+id+'/ack',{});toast('Alert acknowledged','ok');loadAlerts()}catch(e){toast('Failed to ack: '+e.message,'err')}}
async function loadAudit(){if(!state.apiBase||!state.pat)return;document.getElementById('audit-loading').style.display='';document.getElementById('audit-content').style.display='none';document.getElementById('audit-empty').style.display='none';try{const data=await apiGet('/audit/recent');state.audit=Array.isArray(data)?data:(data.entries||data.audit||[]);renderAudit()}catch(e){document.getElementById('audit-loading').style.display='none';document.getElementById('audit-empty').style.display='';document.getElementById('audit-empty').textContent='Error: '+e.message}}
function renderAudit(){document.getElementById('audit-loading').style.display='none';if(!state.audit.length){document.getElementById('audit-empty').style.display='';return}document.getElementById('audit-content').style.display='';document.getElementById('audit-table').innerHTML=state.audit.map(e=>{const ts=e.created_at||e.timestamp||e.ts;const time=ts?fmtTime(new Date(ts)):'-';const tool=e.tool_name||e.tool||'-';const sens=e.sensitivity||'medium';const mode=e.confirmation_mode||e.mode||'-';const action=e.action||e.result||'-';const dur=e.duration_ms?(e.duration_ms+'ms'):'-';const sid=e.session_id||e.session||'-';return`<tr><td class="small">${time}</td><td class="mono small">${esc(sid.substring(0,12))}</td><td class="mono">${esc(tool)}</td><td><span class="tag ${sens==='critical'?'err':sens==='medium'?'warn':'ok'}">${esc(sens)}</span></td><td class="small">${esc(mode)}</td><td><span class="tag ${action==='confirmed'?'ok':action==='denied'?'err':'info'}">${esc(action)}</span></td><td class="small">${dur}</td></tr>`}).join('')}
async function detectMode(){try{const h=await apiGet('/inbox/health');const mode=h.confirmation_mode||h.mode||'off';state.globalMode=mode;document.getElementById('global-mode').value=mode;updateModeTag(mode)}catch(e){document.getElementById('mode-tag').textContent='unknown';document.getElementById('mode-tag').className='tag warn'}}
function updateModeTag(mode){const el=document.getElementById('mode-tag');el.textContent=mode;el.className='tag '+(mode==='off'?'ok':'purple')}
async function setGlobalMode(mode){try{await apiPost('/gate/mode',{mode});state.globalMode=mode;updateModeTag(mode);toast('Global mode set to '+mode,'ok')}catch(e){toast('Failed to set mode: '+e.message,'err');document.getElementById('global-mode').value=state.globalMode}}
async function loadPending(){if(!state.apiBase||!state.pat)return;document.getElementById('pending-loading').style.display='';document.getElementById('pending-content').style.display='none';document.getElementById('pending-empty').style.display='none';try{const data=await apiGet('/confirm/pending');state.pending=Array.isArray(data)?data:(data.pending||[]);renderPending()}catch(e){document.getElementById('pending-loading').style.display='none';document.getElementById('pending-empty').style.display='';document.getElementById('pending-empty').textContent='Error: '+e.message}}
function renderPending(){document.getElementById('pending-loading').style.display='none';const badge=document.getElementById('gate-badge');if(!state.pending.length){document.getElementById('pending-empty').style.display='';badge.style.display='none';return}badge.style.display='';badge.textContent=state.pending.length;document.getElementById('pending-content').style.display='';document.getElementById('pending-content').innerHTML=state.pending.map(p=>{const tool=p.tool_name||p.tool||'unknown';const sens=p.sensitivity||'medium';const ts=p.created_at||p.ts;const time=ts?timeAgo(new Date(ts)):'just now';const summary=p.args_summary||p.summary||JSON.stringify(p.args||{}).substring(0,100);return`<div class="confirm-card ${sens==='critical'?'critical':''}" style="background:var(--bg3);padding:12px;border-radius:6px;margin-bottom:8px;"><div style="display:flex;justify-content:space-between;align-items:center;"><strong class="mono">${esc(tool)}</strong><span class="tag ${sens==='critical'?'err':'warn'}">${esc(sens)}</span></div><p class="mono" style="margin-top:4px;font-size:11px;color:var(--text2);word-break:break-all;">${esc(summary)}</p><div class="small" style="margin-top:4px;">${time}</div><div class="confirm-actions"><button class="btn ok" onclick="resolvePending('${p.id}','confirm')">Confirm</button><button class="btn danger" onclick="resolvePending('${p.id}','deny')">Deny</button></div></div>`}).join('')}
async function resolvePending(id,action){try{await apiPost('/confirm/'+id+'/action',{action});toast('Confirmation '+action+'ed','ok');loadPending()}catch(e){toast('Failed: '+e.message,'err')}}
async function loadHealth(silent){if(!state.apiBase||!state.pat)return;if(!silent){document.getElementById('health-loading').style.display='';document.getElementById('health-content').style.display='none'}try{const h=await apiGet('/inbox/health');state.health=h;renderHealth(h);updateHealthDot(h)}catch(e){document.getElementById('health-dot').className='status-dot err';document.getElementById('health-text').textContent='Disconnected';if(!silent){document.getElementById('health-loading').style.display='none';document.getElementById('health-grid').innerHTML='<div class="empty">Error: '+e.message+'</div>';document.getElementById('health-content').style.display=''}}}
function renderHealth(h){document.getElementById('health-loading').style.display='none';document.getElementById('health-content').style.display='';document.getElementById('health-raw').textContent=JSON.stringify(h,null,2);const components=[];if(h.database!==undefined)components.push({name:'Database',ok:h.database===true||h.database==='ok'});if(h.inbox!==undefined)components.push({name:'Inbox',ok:h.inbox===true||h.inbox==='ok'});if(h.chronicle!==undefined)components.push({name:'Chronicle',ok:h.chronicle===true||h.chronicle==='ok'});if(h.consumer!==undefined)components.push({name:'Consumer',ok:h.consumer===true||h.consumer==='ok'});if(h.delegation!==undefined)components.push({name:'Delegation',ok:h.delegation===true||h.delegation==='ok'});if(h.confirmation_gate!==undefined)components.push({name:'Confirmation Gate',ok:h.confirmation_gate===true||h.confirmation_gate==='ok'});if(h.kms!==undefined)components.push({name:'KMS',ok:h.kms===true||h.kms==='ok'});for(const[k,v]of Object.entries(h)){if(typeof v==='boolean'&&!components.find(c=>c.name.toLowerCase()===k.toLowerCase())){components.push({name:k.charAt(0).toUpperCase()+k.slice(1),ok:v})}}document.getElementById('health-grid').innerHTML=components.map(c=>`<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--bg3);border-radius:6px;"><span class="status-dot ${c.ok?'ok':'err'}"></span><span style="font-size:12px;">${esc(c.name)}</span></div>`).join('')}
function updateHealthDot(h){const allOk=Object.values(h).every(v=>v===true||v==='ok'||typeof v!=='boolean');document.getElementById('health-dot').className='status-dot '+(allOk?'ok':'warn');document.getElementById('health-text').textContent=allOk?'All systems operational':'Some components degraded'}
function loadAll(){loadAgents();loadAlerts();loadAudit();loadHealth()}
function esc(s){if(s===null||s===undefined)return'';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function timeAgo(d){const s=Math.floor((Date.now()-d.getTime())/1000);if(s<60)return s+'s ago';if(s<3600)return Math.floor(s/60)+'m ago';if(s<86400)return Math.floor(s/3600)+'h ago';return Math.floor(s/86400)+'d ago'}
function fmtTime(d){return d.toISOString().replace('T',' ').substring(0,19)}
function toast(msg,type){const c=document.getElementById('toasts');const t=document.createElement('div');t.className='toast '+(type||'');t.textContent=msg;c.appendChild(t);setTimeout(()=>t.remove(),4000)}
</script>
</body>
</html>'''


@router.get("/", response_class=HTMLResponse)
async def dev_ui_root():
    return HTMLResponse(content=_DEV_UI_HTML, status_code=200)


@router.get("/v2", response_class=HTMLResponse)
async def dev_ui_v2():
    return HTMLResponse(content=_DEV_UI_HTML, status_code=200)
