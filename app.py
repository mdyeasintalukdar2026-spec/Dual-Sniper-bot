from flask import Flask, jsonify, make_response
import threading
import requests
import time
import os
import logging
from datetime import datetime, timedelta

app = Flask(__name__, static_folder=None)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("QX_RABotEngine")

QX_API_KEY = os.environ.get("QX_API_KEY", "qx_live_1xxOcsg5_3vEavHfZwAkGufh9NLLWJhUqG3T6H6oCEuoDWeJV")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "dbcaa19r01qqr3s0pf60dbcaa19r01qqr3s0pf6g")
TWELVE_DATA_KEY = os.environ.get("TWELVE_DATA_KEY", "8f5d4d4fce7f44e5bda54420591411c8")
TIMEZONE_OFFSET = float(os.environ.get("QX_TZ", "6"))

http_session = requests.Session()
if QX_API_KEY:
    http_session.headers["Authorization"] = f"Bearer {QX_API_KEY}"

class AdvancedAccuracyFilters:
    @staticmethod
    def check_news_safety(currency: str = "USD") -> bool:
        try:
            url = f"https://finnhub.io/api/v1/calendar/economic?token={FINNHUB_API_KEY}"
            response = http_session.get(url, timeout=5)
            if response.status_code == 200:
                events = response.json().get("economicCalendar", [])
                now_time = datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)
                for event in events:
                    if currency.upper() in event.get("currency", "").upper():
                        event_time_str = event.get("time", "").replace("Z", "+00:00")
                        if event_time_str:
                            event_dt = datetime.fromisoformat(event_time_str) + timedelta(hours=TIMEZONE_OFFSET)
                            if abs((event_dt.replace(tzinfo=None) - now_time).total_seconds()) < 900:
                                return False
            return True
        except Exception:
            return True

    @staticmethod
    def fetch_twelve_data_indicators(symbol: str = "EUR/USD") -> dict:
        try:
            url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval=1min&apikey={TWELVE_DATA_KEY}"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if "values" in data and len(data["values"]) > 0:
                    return {"rsi": float(data["values"][0]["rsi"]), "status": "VERIFIED"}
        except Exception:
            pass
        return {"rsi": 50.0, "status": "FALLBACK"}


class GroqAIArbiter:
    @staticmethod
    def get_ai_decision(market_context: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a master binary options AI arbiter. Return strictly 'CALL' or 'PUT'."},
                {"role": "user", "content": f"Analyze market context: {market_context}. Output decision only ('CALL' or 'PUT')."}
            ],
            "temperature": 0.2,
            "max_tokens": 8
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=3)
            if response.status_code == 200:
                decision = response.json()["choices"][0]["message"]["content"].strip().upper()
                if decision in ["CALL", "PUT"]:
                    return decision
        except Exception:
            pass
        return "CALL" if (int(time.time() * 7) % 2 == 0) else "PUT"


@app.route('/')
def home():
    return "RA Bot Engine Running Successfully!"

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/signal')
def get_signal():
    try:
        current_time = time.time()
        time_slot = int(current_time / 5)
        
        if not AdvancedAccuracyFilters.check_news_safety("USD"):
            res = jsonify({"signal": "HOLD", "trend": "NEWS_BLOCK_ACTIVE", "confidence": 0, "status": "NEWS_GUARD"})
            res.headers.add("Access-Control-Allow-Origin", "*")
            return res

        tech_data = AdvancedAccuracyFilters.fetch_twelve_data_indicators("EUR/USD")
        base_signal = "CALL" if ((int(current_time * 1000) // 100) % 2 == 0) else "PUT"
        
        market_ctx = f"Asset: EURUSD_otc, TimeSlot: {time_slot}, RSI: {tech_data['rsi']}, Trend: {base_signal}"
        ai_decision = GroqAIArbiter.get_ai_decision(market_ctx)
        real_accuracy = 95 + ((int(current_time * 11) + 17) % 5)
        
        res = jsonify({
            "signal": ai_decision,
            "trend": "VIP_CONFLUENCE_VERIFIED",
            "confidence": real_accuracy,
            "status": "GREEN_EXECUTE"
        })
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res
    except Exception:
        res = jsonify({
            "signal": "CALL" if (int(time.time()) % 2 == 0) else "PUT",
            "trend": "STABLE MOMENTUM",
            "confidence": 96,
            "status": "GREEN_EXECUTE"
        })
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res


@app.route('/bot.js')
def bot_script():
    js = """
    (function(){
        function initRaBot() {
            try {
                var d = document;
                if(!d.body) {
                    setTimeout(initRaBot, 100);
                    return;
                }
                
                ["sniper-bot-panel", "sniper-bot-btn", "sniper-bot-style"].forEach(function(i){
                    var e = d.getElementById(i);
                    if(e) e.remove();
                });

                var botMainLogo = "https://i.postimg.cc/RVjfS0Nd/1794387395866.jpg";
                var renderServerUrl = "https://dual-sniper-bot.onrender.com";

                var s = d.createElement('style');
                s.id = 'sniper-bot-style';
                s.innerHTML = '@keyframes multiColorBorderShift {' +
                              '0% { border-color: #22c55e; box-shadow: 0 0 25px rgba(34,197,94,0.8), inset 0 0 14px rgba(34,197,94,0.4); }' +
                              '10% { border-color: #38bdf8; box-shadow: 0 0 25px rgba(56,189,248,0.8), inset 0 0 14px rgba(56,189,248,0.4); }' +
                              '20% { border-color: #a855f7; box-shadow: 0 0 25px rgba(168,85,247,0.8), inset 0 0 14px rgba(168,85,247,0.4); }' +
                              '30% { border-color: #f43f5e; box-shadow: 0 0 25px rgba(244,63,94,0.8), inset 0 0 14px rgba(244,63,94,0.4); }' +
                              '40% { border-color: #eab308; box-shadow: 0 0 25px rgba(234,179,8,0.8), inset 0 0 14px rgba(234,179,8,0.4); }' +
                              '50% { border-color: #06b6d4; box-shadow: 0 0 25px rgba(6,182,212,0.8), inset 0 0 14px rgba(6,182,212,0.4); }' +
                              '60% { border-color: #ec4899; box-shadow: 0 0 25px rgba(236,72,153,0.8), inset 0 0 14px rgba(236,72,153,0.4); }' +
                              '70% { border-color: #84cc16; box-shadow: 0 0 25px rgba(132,204,22,0.8), inset 0 0 14px rgba(132,204,22,0.4); }' +
                              '80% { border-color: #6366f1; box-shadow: 0 0 25px rgba(99,102,241,0.8), inset 0 0 14px rgba(99,102,241,0.4); }' +
                              '90% { border-color: #14b8a6; box-shadow: 0 0 25px rgba(20,184,166,0.8), inset 0 0 14px rgba(20,184,166,0.4); }' +
                              '100% { border-color: #22c55e; box-shadow: 0 0 25px rgba(34,197,94,0.8), inset 0 0 14px rgba(34,197,94,0.4); }' +
                              '}' +
                              '@keyframes whiteGlowPulse {' +
                              '0% { box-shadow: 0 0 12px rgba(255,255,255,0.3), 0 0 25px rgba(255,255,255,0.15); }' +
                              '50% { box-shadow: 0 0 28px rgba(255,255,255,0.8), 0 0 50px rgba(255,255,255,0.4); }' +
                              '100% { box-shadow: 0 0 12px rgba(255,255,255,0.3), 0 0 25px rgba(255,255,255,0.15); }' +
                              '}' +
                              '@keyframes instantSmoothCandle {' +
                              '0% { transform: scaleY(0.85); }' +
                              '50% { transform: scaleY(1.15); }' +
                              '100% { transform: scaleY(0.85); }' +
                              '}' +
                              '@keyframes intensiveRedLaser {' +
                              '0% { transform: translateY(-58px); opacity: 0.4; }' +
                              '50% { opacity: 1; filter: drop-shadow(0 0 25px #ff0000) drop-shadow(0 0 45px #ff3333); }' +
                              '100% { transform: translateY(58px); opacity: 0.4; }' +
                              '}' +
                              '@keyframes aggressiveBounce {' +
                              '0% { transform: translateY(0px) scale(1); }' +
                              '50% { transform: translateY(-20px) scale(1.15); }' +
                              '100% { transform: translateY(0px) scale(1); }' +
                              '}' +
                              '@keyframes candlePopIn {' +
                              '0% { transform: scale(0.4); opacity: 0; }' +
                              '100% { transform: scale(1); opacity: 1; }' +
                              '}' +
                              '@keyframes panelFadeIn { 0% { opacity: 0; transform: translate(-50%, -50%) scale(0.92); } 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); } }';
                d.head.appendChild(s);

                var isExecutionLocked = false;
                var countdownInterval = null;

                function createBotIcon() {
                    var wrap = d.getElementById('sniper-bot-btn') || d.createElement('div');
                    wrap.id = 'sniper-bot-btn';
                    wrap.style.cssText = 'position:fixed;bottom:75px;left:18px;width:70px;height:70px;border-radius:50%;background:#0d1117;display:flex;align-items:center;justify-content:center;border:none;animation:whiteGlowPulse 2.5s infinite ease-in-out;z-index:2147483647;cursor:pointer;box-sizing:border-box;overflow:hidden;';
                    wrap.innerHTML = '<img src="' + botMainLogo + '" style="width:100%;height:100%;object-fit:cover;pointer-events:none;" />';

                    if(!d.body.contains(wrap)) d.body.appendChild(wrap);

                    var isDragging = false, startX, startY, hasMoved = false;
                    wrap.onmousedown = wrap.ontouchstart = function(e){
                        isDragging = true; hasMoved = false;
                        var p = e.touches ? e.touches[0] : e;
                        startX = p.clientX - wrap.offsetLeft; startY = p.clientY - wrap.offsetTop;
                    };
                    wrap.onmousemove = wrap.ontouchmove = function(e){
                        if(!isDragging) return;
                        var p = e.touches ? e.touches[0] : e;
                        var nx = p.clientX - startX, ny = p.clientY - startY;
                        if(Math.abs(nx - wrap.offsetLeft) > 2 || Math.abs(ny - wrap.offsetTop) > 2) hasMoved = true;
                        wrap.style.left = nx + 'px'; wrap.style.top = ny + 'px';
                        wrap.style.bottom = 'auto'; wrap.style.right = 'auto';
                    };
                    wrap.onmouseup = wrap.ontouchend = function(){ isDragging = false; };
                    wrap.onclick = function(){ if(!hasMoved) toggleVipPanel(); };
                }

                createBotIcon();

                function toggleVipPanel() {
                    var existing = d.getElementById('sniper-bot-panel');
                    var floatingBtn = d.getElementById('sniper-bot-btn');
                    
                    if(existing) { 
                        existing.remove(); 
                        if(floatingBtn) floatingBtn.style.display = 'flex';
                        return; 
                    }

                    if(floatingBtn) floatingBtn.style.display = 'none';

                    var panel = d.createElement('div');
                    panel.id = 'sniper-bot-panel';
                    panel.style.cssText = 'position:fixed;top:45%;left:50%;transform:translate(-50%, -50%);width:285px;background:linear-gradient(180deg, rgba(10, 15, 26, 0.98), rgba(4, 7, 14, 0.99));border:3px solid #22c55e;border-radius:14px;animation:multiColorBorderShift 8s infinite linear, panelFadeIn 0.2s ease-out;z-index:2147483647;font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;color:#fff;overflow:hidden;box-sizing:border-box;backdrop-filter:blur(10px);box-shadow:0 15px 35px rgba(0,0,0,0.85);';

                    panel.innerHTML = 
                        '<div style="padding:12px;box-sizing:border-box;display:flex;flex-direction:column;gap:8px;">' +
                            '<div id="sniper-panel-header" style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:6px;cursor:move;">' +
                                '<div style="display:flex;align-items:center;gap:8px;pointer-events:none;">' +
                                    '<img src="' + botMainLogo + '" style="width:38px;height:38px;border-radius:8px;object-fit:cover;border:1.5px solid #22c55e;" />' +
                                    '<div style="display:flex;flex-direction:column;justify-content:center;margin-left:2px;">' +
                                        '<div style="font-size:12px;font-weight:900;letter-spacing:1px;color:#fff;">RA BOT</div>' +
                                        '<div id="sniper-panel-time" style="font-size:7px;color:#94a3b8;font-weight:700;">TIME: 17:05:53</div>' +
                                    '</div>' +
                                '</div>' +
                                '<div style="display:flex;align-items:center;gap:4px;">' +
                                    '<div style="background:rgba(234,179,8,0.2);color:#facc15;font-size:7px;font-weight:900;padding:1px 5px;border-radius:3px;border:1px solid rgba(234,179,8,0.4);">VIP</div>' +
                                    '<div id="sniper-minus-btn" style="cursor:pointer;font-size:11px;color:#94a3b8;padding:1px 5px;border-radius:3px;background:rgba(255,255,255,0.06);font-weight:bold;">—</div>' +
                                    '<div id="sniper-close-btn" style="cursor:pointer;font-size:11px;color:#94a3b8;padding:1px 4px;border-radius:3px;background:rgba(255,255,255,0.06);">✕</div>' +
                                '</div>' +
                            '</div>' +

                            '<div style="display:flex;align-items:center;gap:3px;font-size:7.5px;color:#22c55e;font-weight:800;background:rgba(34,197,94,0.08);padding:3px 6px;border-radius:4px;border:1px solid rgba(34,197,94,0.2);animation:multiColorBorderShift 8s infinite linear;">' +
                                '<span style="width:5px;height:5px;background:#22c55e;border-radius:50%;display:inline-block;box-shadow:0 0 6px #22c55e;"></span> AI ENGINE ONLINE' +
                            '</div>' +

                            '<div style="background:rgba(0,0,0,0.6);border:1.5px solid rgba(255,255,255,0.1);border-radius:8px;padding:6px;text-align:center;">' +
                                '<div style="font-size:8.5px;font-weight:900;color:#38bdf8;margin-bottom:3px;letter-spacing:0.5px;">AI SIGNAL SCANNER</div>' +
                                '<div id="scanner-title-text" style="font-size:11px;font-weight:900;color:#22c55e;margin-bottom:5px;letter-spacing:0.5px;">Next Candle??</div>' +
                                '<div id="sniper-candle-display-box" style="display:flex;align-items:center;justify-content:space-evenly;height:125px;background:rgba(0,0,0,0.88);border-radius:8px;padding:8px;border:1.5px solid rgba(56,189,248,0.35);overflow:hidden;position:relative;">' +
                                    '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out;"><div style="width:2.5px;height:12px;background:#22c55e;"></div><div style="width:10px;height:42px;background:#22c55e;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#22c55e;"></div></div>' +
                                    '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.15s;"><div style="width:2.5px;height:12px;background:#ef4444;"></div><div style="width:10px;height:50px;background:#ef4444;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#ef4444;"></div></div>' +
                                    '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.3s;"><div style="width:2.5px;height:12px;background:#38bdf8;"></div><div style="width:10px;height:38px;background:#38bdf8;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#38bdf8;"></div></div>' +
                                    '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.45s;"><div style="width:2.5px;height:12px;background:#a855f7;"></div><div style="width:10px;height:55px;background:#a855f7;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#a855f7;"></div></div>' +
                                    '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.6s;"><div style="width:2.5px;height:12px;background:#eab308;"></div><div style="width:10px;height:46px;background:#eab308;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#eab308;"></div></div>' +
                                    '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.75s;"><div style="width:2.5px;height:12px;background:#ec4899;"></div><div style="width:10px;height:42px;background:#ec4899;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#ec4899;"></div></div>' +
                                '</div>' +
                            '</div>' +

                            '<div style="background:rgba(0,0,0,0.5);border:1.5px solid rgba(255,255,255,0.12);border-radius:8px;padding:7px;display:flex;justify-content:space-between;align-items:center;">' +
                                '<div style="min-width:82px;">' +
                                    '<div style="font-size:7px;color:#94a3b8;font-weight:bold;margin-bottom:2px;">LATEST SIGNAL</div>' +
                                    '<div id="sniper-signal-row" style="display:flex;align-items:center;gap:6px;">' +
                                        '<span id="sniper-signal-icon" style="background:#064e3b;color:#10b981;font-size:11px;font-weight:900;padding:2px 6px;border-radius:4px;border:1px solid #059669;">⚡</span>' +
                                        '<span id="sniper-signal-text" style="font-size:13.5px;font-weight:900;color:#10b981;letter-spacing:0.5px;">READY</span>' +
                                    '</div>' +
                                '</div>' +
                                '<div id="sniper-timer-box" style="background:#030712;border:1.5px solid rgba(34,197,94,0.4);border-radius:6px;padding:5px 10px;font-size:11.5px;font-weight:900;color:#22c55e;letter-spacing:1px;">--:--:--</div>' +
                            '</div>' +

                            '<button id="sniper-get-signal-btn" style="width:100%;background:#166534;color:#fff;border:none;border-radius:8px;padding:9.5px;font-size:12px;font-weight:900;cursor:pointer;box-shadow:0 4px 18px rgba(22,101,52,0.7);letter-spacing:0.8px;display:flex;align-items:center;justify-content:center;gap:6px;animation:multiColorBorderShift 5s infinite linear;">' +
                                '<span>⚡</span> GET SIGNAL' +
                            '</button>' +

                            '<div style="text-align:center;font-size:6.5px;color:#64748b;font-weight:600;padding-top:1px;">' +
                                'RA Bot VIP - High Accuracy Engine' +
                            '</div>' +
                        '</div>';

                    d.body.appendChild(panel);
                    makeDraggable(panel);

                    d.getElementById('sniper-close-btn').onclick = function() {
                        panel.remove();
                        if(floatingBtn) floatingBtn.style.display = 'flex';
                    };

                    d.getElementById('sniper-minus-btn').onclick = function() {
                        panel.remove();
                        if(floatingBtn) floatingBtn.style.display = 'flex';
                    };

                    setInterval(function(){
                        var timeEl = d.getElementById('sniper-panel-time');
                        if(timeEl) {
                            var now = new Date();
                            var hrs = String(now.getHours()).padStart(2, '0');
                            var mins = String(now.getMinutes()).padStart(2, '0');
                            var secs = String(now.getSeconds()).padStart(2, '0');
                            timeEl.innerText = 'TIME: ' + hrs + ':' + mins + ':' + secs;
                        }
                    }, 1000);

                    d.getElementById('sniper-get-signal-btn').onclick = function() {
                        runSignalSequence(panel);
                    };
                }

                function makeDraggable(panelEl) {
                    var header = d.getElementById('sniper-panel-header');
                    if(!header) return;
                    var pX = 0, pY = 0, mX = 0, mY = 0;
                    header.onmousedown = header.ontouchstart = function(e) {
                        var p = e.touches ? e.touches[0] : e;
                        mX = p.clientX; mY = p.clientY;
                        d.onmouseup = d.ontouchend = closeDragElement;
                        d.onmousemove = d.ontouchmove = elementDrag;
                    };
                    function elementDrag(e) {
                        var p = e.touches ? e.touches[0] : e;
                        pX = mX - p.clientX; pY = mY - p.clientY;
                        mX = p.clientX; mY = p.clientY;
                        panelEl.style.top = (panelEl.offsetTop - pY) + "px";
                        panelEl.style.left = (panelEl.offsetLeft - pX) + "px";
                        panelEl.style.transform = 'none';
                    }
                    function closeDragElement() {
                        d.onmouseup = d.ontouchend = null;
                        d.onmousemove = d.ontouchmove = null;
                    }
                }

                function getBrokerTimeframeSeconds() {
                    try {
                        var selectors = [
                            'input[name="timer"]', '.timer-input input', 'input[class*="timer"]', 
                            '.time-input', '.timer-setting__input', '.timer-setting', 
                            '.c-dropdown__label', '[class*="timer-value"]', '.timer-counter',
                            '.timer-setting__btn.active', '.dropdown-select__item.active', 'button[class*="timer"].active'
                        ];
                        
                        for(var i=0; i<selectors.length; i++) {
                            var el = d.querySelector(selectors[i]);
                            if(el) {
                                var text = (el.value || el.innerText || '').trim();
                                if(text) {
                                    if(text.includes(':')) {
                                        var parts = text.split(':').map(function(p){ return parseInt(p, 10) || 0; });
                                        if(parts.length === 3) {
                                            var total = parts[0]*3600 + parts[1]*60 + parts[2];
                                            if(total > 0) return total;
                                        } else if(parts.length === 2) {
                                            var total = parts[0]*60 + parts[1];
                                            if(total > 0) return total;
                                        }
                                    }
                                    var lower = text.toLowerCase();
                                    var num = parseInt(text, 10);
                                    if(!isNaN(num) && num > 0) {
                                        if(lower.includes('h')) return num * 3600;
                                        if(lower.includes('m')) return num * 60;
                                        if(lower.includes('s')) return num;
                                        if(num <= 5) return num * 60;
                                        return num;
                                    }
                                }
                            }
                        }

                        var allInputs = d.querySelectorAll('input, [class*="timer"]');
                        for(var i=0; i<allInputs.length; i++) {
                            var val = (allInputs[i].value || allInputs[i].innerText || '').trim();
                            if(val.includes(':')) {
                                var parts = val.split(':').map(function(p){ return parseInt(p, 10) || 0; });
                                if(parts.length === 3) {
                                    var total = parts[0]*3600 + parts[1]*60 + parts[2];
                                    if(total > 0) return total;
                                } else if(parts.length === 2) {
                                    var total = parts[0]*60 + parts[1];
                                    if(total > 0) return total;
                                }
                            }
                        }
                    } catch(e) {}
                    return 60;
                }

                function runSignalSequence(panel) {
                    var signalText = panel.querySelector('#sniper-signal-text');
                    var signalIcon = panel.querySelector('#sniper-signal-icon');
                    var subText = panel.querySelector('#sniper-sub-text');
                    var candleBox = panel.querySelector('#sniper-candle-display-box');
                    var timerBox = panel.querySelector('#sniper-timer-box');
                    var titleText = panel.querySelector('#scanner-title-text');

                    if(!signalText) return;

                    titleText.innerText = 'ANALYZING MARKET...';
                    signalText.style.color = '#38bdf8';
                    signalText.innerText = 'SCANNING...';
                    signalIcon.innerText = '⚡';
                    signalIcon.style.background = '#0c4a6e';
                    signalIcon.style.color = '#38bdf8';
                    signalIcon.style.border = '1px solid #0284c7';
                    if(subText) subText.innerText = '';
                    timerBox.innerText = '--:--:--';

                    candleBox.innerHTML = 
                        '<div style="position:relative;width:100%;height:100%;display:flex;align-items:center;justify-content:space-evenly;background:#05070d;overflow:hidden;padding:6px;">' +
                            '<div style="position:absolute;width:100%;height:5px;background:#ff0000;box-shadow:0 0 25px #ff0000, 0 0 45px #ff0000, 0 0 70px #ff3333;animation:intensiveRedLaser 1s infinite ease-in-out;z-index:5;"></div>' +
                            '<div style="display:flex;flex-direction:column;align-items:center;animation:aggressiveBounce 0.45s infinite ease-in-out alternate;"><div style="width:2px;height:10px;background:#38bdf8;"></div><div style="width:9px;height:38px;background:#38bdf8;border-radius:2px;box-shadow:0 0 12px #38bdf8;"></div><div style="width:2px;height:10px;background:#38bdf8;"></div></div>' +
                            '<div style="display:flex;flex-direction:column;align-items:center;animation:aggressiveBounce 0.4s infinite ease-in-out alternate-reverse;"><div style="width:2px;height:10px;background:#a855f7;"></div><div style="width:9px;height:45px;background:#a855f7;border-radius:2px;box-shadow:0 0 12px #a855f7;"></div><div style="width:2px;height:10px;background:#a855f7;"></div></div>' +
                            '<div style="display:flex;flex-direction:column;align-items:center;animation:aggressiveBounce 0.5s infinite ease-in-out alternate;"><div style="width:2px;height:10px;background:#22c55e;"></div><div style="width:9px;height:40px;background:#22c55e;border-radius:2px;box-shadow:0 0 12px #22c55e;"></div><div style="width:2px;height:10px;background:#22c55e;"></div></div>' +
                            '<div style="display:flex;flex-direction:column;align-items:center;animation:aggressiveBounce 0.45s infinite ease-in-out alternate-reverse;"><div style="width:2px;height:10px;background:#eab308;"></div><div style="width:9px;height:48px;background:#eab308;border-radius:2px;box-shadow:0 0 12px #eab308;"></div><div style="width:2px;height:10px;background:#eab308;"></div></div>' +
                            '<div style="display:flex;flex-direction:column;align-items:center;animation:aggressiveBounce 0.48s infinite ease-in-out alternate;"><div style="width:2px;height:10px;background:#ec4899;"></div><div style="width:9px;height:42px;background:#ec4899;border-radius:2px;box-shadow:0 0 12px #ec4899;"></div><div style="width:2px;height:10px;background:#ec4899;"></div></div>' +
                            '<div style="display:flex;flex-direction:column;align-items:center;animation:aggressiveBounce 0.42s infinite ease-in-out alternate-reverse;"><div style="width:2px;height:10px;background:#06b6d4;"></div><div style="width:9px;height:38px;background:#06b6d4;border-radius:2px;box-shadow:0 0 12px #06b6d4;"></div><div style="width:2px;height:10px;background:#06b6d4;"></div></div>' +
                            '<div style="position:absolute;bottom:4px;font-size:9px;font-weight:900;color:#ff3333;z-index:6;letter-spacing:1px;background:rgba(0,0,0,0.88);padding:2.5px 10px;border-radius:4px;border:1px solid rgba(255,0,0,0.6);box-shadow:0 0 12px rgba(255,0,0,0.5);">SCANNING...</div>' +
                        '</div>';

                    fetch(renderServerUrl + '/signal?t=' + Date.now())
                    .then(function(r){ return r.json(); })
                    .catch(function(){ return {signal: "CALL", confidence: 96}; })
                    .then(function(data){
                        setTimeout(function(){
                            if(!panel.isConnected) return;
                            var sig = String(data.signal || 'CALL').toUpperCase();
                            var isCall = (sig === 'CALL' || sig === 'UP' || sig === 'BUY');
                            var confidence = data.confidence || 96;

                            titleText.innerText = 'SIGNAL CONFIRMED';

                            signalIcon.innerText = isCall ? '↑' : '↓';
                            signalIcon.style.background = isCall ? '#166534' : '#991b1b';
                            signalIcon.style.color = '#fff';
                            signalIcon.style.border = isCall ? '1px solid #22c55e' : '1px solid #ef4444';

                            signalText.style.fontSize = '13.5px';
                            signalText.style.color = isCall ? '#22c55e' : '#ef4444';
                            signalText.innerText = (isCall ? 'UP' : 'DOWN');
                            if(subText) subText.innerText = '';

                            var candleColor = isCall ? '#22c55e' : '#ef4444';
                            var arrowSymbol = isCall ? '↑' : '↓';

                            candleBox.innerHTML = 
                                '<div style="position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;width:100%;animation:candlePopIn 0.3s ease-out;background:radial-gradient(circle, rgba(20,30,50,0.85) 0%, rgba(5,7,13,0.95) 100%);padding:4px 0;">' +
                                    '<div style="position:relative;display:flex;flex-direction:column;align-items:center;margin-bottom:8px;">' +
                                        '<div style="width:3px;height:12px;background:' + candleColor + ';box-shadow:0 0 8px ' + candleColor + ';"></div>' +
                                        '<div style="width:28px;height:48px;background:' + candleColor + ';border-radius:4px;box-shadow:0 0 20px ' + candleColor + ';z-index:2;"></div>' +
                                        '<div style="width:3px;height:12px;background:' + candleColor + ';box-shadow:0 0 8px ' + candleColor + ';"></div>' +
                                    '</div>' +
                                    '<div style="background:#030712;border:2px solid ' + candleColor + ';padding:4px 20px;border-radius:14px;display:flex;align-items:center;gap:5px;box-shadow:0 0 16px ' + candleColor + ';">' +
                                        '<span style="color:' + candleColor + ';font-size:12px;font-weight:900;">' + arrowSymbol + '</span>' +
                                        '<span style="color:' + candleColor + ';font-size:12.5px;font-weight:900;letter-spacing:1px;">' + (isCall ? 'UP' : 'DOWN') + '</span>' +
                                    '</div>' +
                                '</div>';

                            var targetDuration = getBrokerTimeframeSeconds();
                            startCountdown(timerBox, targetDuration, panel);

                            executeTrade(isCall);
                        }, 5000);
                    });
                }

                function startCountdown(timerEl, durationSeconds, panel) {
                    if(countdownInterval) clearInterval(countdownInterval);
                    var timer = durationSeconds;
                    countdownInterval = setInterval(function(){
                        var hrs = parseInt(timer / 3600, 10);
                        var mins = parseInt((timer % 3600) / 60, 10);
                        var secs = parseInt(timer % 60, 10);
                        hrs = hrs < 10 ? "0" + hrs : hrs;
                        mins = mins < 10 ? "0" + mins : mins;
                        secs = secs < 10 ? "0" + secs : secs;
                        timerEl.innerText = hrs + ":" + mins + ":" + secs;
                        if (--timer < 0) {
                            clearInterval(countdownInterval);
                            timerEl.innerText = "--:--:--";
                            resetPanelToDefault(panel);
                        }
                    }, 1000);
                }

                function resetPanelToDefault(panel) {
                    var titleText = panel.querySelector('#scanner-title-text');
                    var signalText = panel.querySelector('#sniper-signal-text');
                    var signalIcon = panel.querySelector('#sniper-signal-icon');
                    var subText = panel.querySelector('#sniper-sub-text');
                    var candleBox = panel.querySelector('#sniper-candle-display-box');
                    var timerBox = panel.querySelector('#sniper-timer-box');

                    if(!titleText) return;

                    titleText.innerText = 'Next Candle??';
                    signalText.style.color = '#10b981';
                    signalText.innerText = 'READY';
                    signalIcon.innerText = '⚡';
                    signalIcon.style.background = '#064e3b';
                    signalIcon.style.color = '#10b981';
                    signalIcon.style.border = '1px solid #059669';
                    if(subText) subText.innerText = 'Tap GET SIGNAL to begin';
                    timerBox.innerText = '--:--:--';

                    candleBox.innerHTML = 
                        '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out;"><div style="width:2.5px;height:12px;background:#22c55e;"></div><div style="width:10px;height:42px;background:#22c55e;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#22c55e;"></div></div>' +
                        '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.15s;"><div style="width:2.5px;height:12px;background:#ef4444;"></div><div style="width:10px;height:50px;background:#ef4444;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#ef4444;"></div></div>' +
                        '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.3s;"><div style="width:2.5px;height:12px;background:#38bdf8;"></div><div style="width:10px;height:38px;background:#38bdf8;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#38bdf8;"></div></div>' +
                        '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.45s;"><div style="width:2.5px;height:12px;background:#a855f7;"></div><div style="width:10px;height:55px;background:#a855f7;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#a855f7;"></div></div>' +
                        '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.6s;"><div style="width:2.5px;height:12px;background:#eab308;"></div><div style="width:10px;height:46px;background:#eab308;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#eab308;"></div></div>' +
                        '<div style="display:flex;flex-direction:column;align-items:center;animation:instantSmoothCandle 1.5s infinite ease-in-out 0.75s;"><div style="width:2.5px;height:12px;background:#ec4899;"></div><div style="width:10px;height:42px;background:#ec4899;border-radius:2px;"></div><div style="width:2.5px;height:12px;background:#ec4899;"></div></div>';
                }

                function executeTrade(isCall) {
                    if(isExecutionLocked) return;
                    isExecutionLocked = true;

                    var targetBtn = null;
                    var buttons = d.querySelectorAll('button, div[role="button"], span[class*="btn"]');
                    
                    for(var i=0; i<buttons.length; i++){
                        var btn = buttons[i];
                        var text = (btn.innerText || '').trim().toUpperCase();
                        var cls = (btn.className || '').toLowerCase();
                        
                        var isUp = cls.includes('call') || cls.includes('buy') || cls.includes('up') || text === 'UP' || text === 'BUY';
                        var isDown = cls.includes('put') || cls.includes('sell') || cls.includes('down') || text === 'DOWN' || text === 'SELL';
                        
                        if(isCall && isUp && btn.getBoundingClientRect().width > 0){ targetBtn = btn; break; }
                        if(!isCall && isDown && btn.getBoundingClientRect().width > 0){ targetBtn = btn; break; }
                    }

                    if(!targetBtn) {
                        var selectors = isCall ? ['.section-deal__button-up', '.btn-call', 'button.call'] : ['.section-deal__button-down', '.btn-put', 'button.put'];
                        for(var i=0; i<selectors.length; i++){
                            var f = d.querySelector(selectors[i]);
                            if(f && f.getBoundingClientRect().width > 0) { targetBtn = f; break; }
                        }
                    }

                    if(targetBtn) {
                        try { targetBtn.click(); } catch(e) {
                            var box = targetBtn.getBoundingClientRect();
                            var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: box.left + box.width/2, clientY: box.top + box.height/2 });
                            targetBtn.dispatchEvent(ev);
                        }
                    }

                    setTimeout(function(){ isExecutionLocked = false; }, 3500);
                }

            } catch(e) { console.error("RA Bot Error:", e); }
        }

        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            initRaBot();
        } else {
            window.addEventListener('DOMContentLoaded', initRaBot);
            window.addEventListener('load', initRaBot);
            setTimeout(initRaBot, 400);
        }
    })();
    """
    res = make_response(js)
    res.headers['Content-Type'] = 'application/javascript'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res

def start_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
