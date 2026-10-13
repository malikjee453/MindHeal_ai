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
          margin: 6px 0 10px; padding: 8px 7px;
          border: 1px solid #d7e5db; border-radius: 12px;
          background: linear-gradient(145deg, #f4f8f5, #e8f2eb);
          text-align: left; color: #173b2d; width: fit-content; min-width: 0; padding-left: 9px; padding-right: 9px;
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
            dateEl.textContent = new Intl.DateTimeFormat("en-GB", {
              timeZone: zone, day: "2-digit", month: "short", year: "2-digit"
            }).format(now).replace(/ /g, "-");
          } catch (err) {
            timeEl.textContent = now.toLocaleTimeString([], {hour:"numeric", minute:"2-digit"});
            dateEl.textContent = now.toLocaleDateString("en-GB", {day:"2-digit", month:"short", year:"2-digit"}).replace(/ /g, "-");
          }
        }

        drawClock();
        setInterval(drawClock, 1000);

        async function lookupCity() {
          const providers = [
            async () => {
              const response = await fetch("https://ipapi.co/json/");
              if (!response.ok) throw new Error("ipapi unavailable");
              const data = await response.json();
              if (!data || (!data.city && !data.timezone)) throw new Error("No location");
              return {city: data.city, timezone: data.timezone};
            },
            async () => {
              const response = await fetch("https://ipwho.is/");
              if (!response.ok) throw new Error("ipwho unavailable");
              const data = await response.json();
              if (!data || data.success === false || (!data.city && !data.timezone?.id)) throw new Error("No location");
              return {city: data.city, timezone: data.timezone?.id};
            }
          ];
          for (const provider of providers) {
            try {
              const data = await provider();
              if (data.timezone && data.timezone.includes("/")) zone = data.timezone;
              if (data.city) { cityEl.textContent = data.city; drawClock(); return; }
            } catch (error) {}
          }
          cityEl.textContent = "City unavailable";
          drawClock();
        }
        lookupCity();
      </script>
    </body>
    </html>
    """, height=100, scrolling=False)
