import streamlit.components.v1 as components

def render_world_clock():
    """Show one prominent local clock, using IP timezone with device fallback."""
    components.html("""
    <!doctype html><html><head><meta charset="utf-8"><style>
    *{box-sizing:border-box}html,body{margin:0;padding:0;background:transparent;font-family:"Segoe UI",Arial,sans-serif}
    .clock{margin:6px 0 10px;padding:11px 7px 10px;border:1px solid #d7e5db;border-radius:14px;background:linear-gradient(145deg,#f4f8f5,#e8f2eb);text-align:center;color:#173b2d;width:100%}
    .label{font-size:.8rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#527160}
    .time{font-size:1.65rem;font-weight:850;line-height:1.3;letter-spacing:-.6px;margin:3px 0;font-variant-numeric:tabular-nums}
    .date{font-size:.78rem;font-weight:600;color:#42614f}.place{font-size:.66rem;margin-top:7px;color:#718378;overflow-wrap:anywhere}
    </style></head><body><section class="clock">
    <div class="label">🕒 Your Local Time</div><div class="time" id="t">--:--:--</div>
    <div class="date" id="d">Loading date…</div><div class="place" id="p">Detecting timezone…</div></section>
    <script>
    let zone=Intl.DateTimeFormat().resolvedOptions().timeZone||"UTC", place="Device timezone";
    function draw(){let n=new Date();try{
      document.getElementById("t").textContent=new Intl.DateTimeFormat(undefined,{timeZone:zone,hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:true}).format(n);
      document.getElementById("d").textContent=new Intl.DateTimeFormat(undefined,{timeZone:zone,weekday:"long",year:"numeric",month:"long",day:"numeric"}).format(n);
      document.getElementById("p").textContent=place+" · "+zone;
    }catch(e){document.getElementById("t").textContent=n.toLocaleTimeString();document.getElementById("d").textContent=n.toLocaleDateString();}}
    draw();setInterval(draw,1000);
    fetch("https://ipapi.co/json/").then(r=>{if(!r.ok)throw Error();return r.json()}).then(x=>{
      if(x&&x.timezone&&x.timezone.indexOf("/")>0){zone=x.timezone;place=[x.city,x.country_name].filter(Boolean).join(", ")||"Approximate IP location";}else{place="Device timezone";}
      draw();
    }).catch(()=>{place="Device timezone";draw();});
    </script></body></html>""", height=132, scrolling=False)
