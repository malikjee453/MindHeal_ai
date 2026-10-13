import streamlit.components.v1 as components


def render_world_clock():
    """Show a compact local clock using IP timezone, with device fallback."""
    components.html("""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * { box-sizing: border-box; }
        html, body {
          margin: 0; padding: 0; background: transparent;
          font-family: "Segoe UI", Arial, sans-serif;
        }
        .clock {
          margin: 6px 0 10px; padding: 10px 7px;
          border: 1px solid #d7e5db; border-radius: 12px;
          background: linear-gradient(145deg, #f4f8f5, #e8f2eb);
          text-align: center; color: #173b2d; width: 100%;
        }
        .city {
          font-size: .78rem; font-weight: 700;
          letter-spacing: .02em; color: #527160; margin-bottom: 3px;
        }
        .time {
          font-size: 1.55rem; font-weight: 800; line-height: 1.3;
          letter-spacing: -.5px; font-variant-numeric: tabular-nums;
          white-space: nowrap;
        }
        .ampm { font-size: .58em; font-weight: 700; letter-spacing: 0; }
        .date {
          font-size: .82rem; font-weight: 600;
          color: #42614f; margin-top: 2px;
        }
      </style>
    </head>
    <body>
      <section class="clock" aria-label="Local time and date">
        <div class="city" id="city">Local Time</div>
        <div class="time" id="time">--:-- <span class="ampm">--</span></div>
        <div class="date" id="date">--/--/----</div>
      </section>
      <script>
        let zone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
        const cityEl = document.getElementById("city");
        const timeEl = document.getElementById("time");
        const dateEl = document.getElementById("date");

        function drawClock() {
          const now = new Date();
          try {
            const parts = new Intl.DateTimeFormat("en-US", {
              timeZone: zone, hour: "numeric", minute: "2-digit", hour12: true
            }).formatToParts(now);
            const hour = parts.find(p => p.type === "hour")?.value || "";
            const minute = parts.find(p => p.type === "minute")?.value || "00";
            const period = parts.find(p => p.type === "dayPeriod")?.value || "";
            timeEl.innerHTML = hour + ":" + minute +
              ' <span class="ampm">' + period + "</span>";
            dateEl.textContent = new Intl.DateTimeFormat("en-US", {
              timeZone: zone, month: "2-digit", day: "2-digit", year: "numeric"
            }).format(now);
          } catch (err) {
            timeEl.textContent = now.toLocaleTimeString([], {hour:"numeric", minute:"2-digit"});
            dateEl.textContent = now.toLocaleDateString("en-US");
          }
        }

        drawClock();
        setInterval(drawClock, 1000);

        fetch("https://ipapi.co/json/", {headers: {"Accept":"application/json"}})
          .then(response => { if (!response.ok) throw new Error("IP lookup unavailable"); return response.json(); })
          .then(data => {
            if (data && typeof data.timezone === "string" && data.timezone.includes("/")) {
              zone = data.timezone;
              cityEl.textContent = data.city || data.region || data.country_name || "City unavailable";
            } else {
              cityEl.textContent = "City unavailable";
            }
            drawClock();
          })
          .catch(() => {
            cityEl.textContent = "City unavailable";
            drawClock();
          });
      </script>
    </body>
    </html>
    """, height=105, scrolling=False)
