// Per-section "Save image" and "Share" buttons.
// Inlined into index.html by build_site.py (placeholder __SHARE__ in template.html).
(function(){
  const SITE="https://deadliestday.org/";
  const SHARE={
    "s-rate":"Children are hit hardest on Halloween: child pedestrians die at 3.1× the rate of an ordinary day, and 4.4× after dark. 25 years of NHTSA crash data.",
    "s-where":"Every pedestrian killed in the US on Halloween, 2000–2024, mapped. Orange dots are children under 18.",
    "s-who":"Of the 2,923 people killed in road crashes on Halloween over 25 years, 19% were pedestrians.",
    "s-users":"It's not just Halloween: about 38,600 people die every year on American streets. Pedestrians went from 11% of road deaths in 2000 to 18% in 2024.",
    "s-weekday":"Does it matter which weekday Halloween falls on? 25 years of Halloween pedestrian deaths, by weekday.",
    "s-years":"Pedestrians killed in the US on Halloween, year by year, 2000–2024."
  };
  const toast=document.createElement("div");toast.className="toast";document.body.appendChild(toast);
  function say(msg){toast.textContent=msg;toast.style.opacity=1;clearTimeout(say.t);say.t=setTimeout(()=>toast.style.opacity=0,4500);}

  // clone the chart SVG with CSS variables / class styles resolved so it renders standalone
  function inlineSvg(svg){
    const c=svg.cloneNode(true),src=svg.querySelectorAll("*"),dst=c.querySelectorAll("*");
    src.forEach((s,i)=>{const cs=getComputedStyle(s),d=dst[i];
      ["fill","stroke","stroke-width","fill-opacity","font-size","font-weight","font-family","text-anchor"].forEach(p=>d.style.setProperty(p,cs.getPropertyValue(p)));
      d.removeAttribute("class");});
    const vb=svg.viewBox.baseVal;
    c.setAttribute("xmlns","http://www.w3.org/2000/svg");c.setAttribute("width",vb.width);c.setAttribute("height",vb.height);c.removeAttribute("style");
    return c;
  }
  function wrap(ctx,text,x,y,maxW,lh,draw){
    let line="";
    for(const w of text.split(" ")){const t=line?line+" "+w:w;
      if(ctx.measureText(t).width>maxW&&line){if(draw)ctx.fillText(line,x,y);line=w;y+=lh;}else line=t;}
    if(draw)ctx.fillText(line,x,y);return y+lh;
  }
  function loadImage(src){return new Promise((res,rej)=>{const im=new Image();im.onload=()=>res(im);im.onerror=rej;im.src=src;});}

  async function makeImage(card){
    const css=getComputedStyle(document.documentElement),col=n=>css.getPropertyValue(n).trim();
    const svg=card.querySelector("svg"),vb=svg.viewBox.baseVal;
    const pressed=card.querySelector(".tabs button[aria-pressed=true]");
    const title=card.querySelector("h2").textContent+(pressed?" — "+pressed.textContent:"");
    const sub=((card.querySelector(".lead")?.textContent||"")+" "+(card.querySelector(".sub")?.textContent||"")).trim().replace(/\s*Hover[^.]*\./i,"");
    const note=card.querySelector(".note")?.textContent||"";
    const legend=[...card.querySelectorAll(".legend span")].filter(s=>!s.querySelector("button[aria-pressed=false]")).map(s=>({t:s.textContent.trim(),c:getComputedStyle(s.querySelector("i")).backgroundColor}));
    const img=await loadImage("data:image/svg+xml;charset=utf-8,"+encodeURIComponent(new XMLSerializer().serializeToString(inlineSvg(svg))));
    const W=1200,P=56,IW=W-2*P,IH=Math.round(IW*vb.height/vb.width),serif="Georgia,'Times New Roman',serif",sans="'Segoe UI',system-ui,sans-serif";
    const cv=document.createElement("canvas"),ctx=cv.getContext("2d");
    function layout(draw){
      let y=P;
      ctx.textBaseline="alphabetic";
      ctx.font="800 20px "+sans;ctx.fillStyle=col("--text-primary");if(draw)ctx.fillText("🎃 DEADLIESTDAY.ORG",P,y+14);y+=56;
      ctx.font="800 46px "+serif;ctx.fillStyle=col("--text-primary");y=wrap(ctx,title,P,y+30,IW,54,draw);
      ctx.font="22px "+sans;ctx.fillStyle=col("--text-secondary");y=wrap(ctx,sub,P,y+6,IW,30,draw);
      if(legend.length){let x=P;y+=8;ctx.font="20px "+sans;
        legend.forEach(l=>{if(draw){ctx.fillStyle=l.c;ctx.fillRect(x,y-15,16,16);ctx.fillStyle=col("--text-secondary");ctx.fillText(l.t,x+24,y);}x+=24+ctx.measureText(l.t).width+30;});y+=22;}
      if(draw)ctx.drawImage(img,P,y,IW,IH);y+=IH+20;
      if(note){ctx.font="22px "+sans;const y0=y;ctx.fillStyle=col("--text-secondary");y=wrap(ctx,note,P+22,y+22,IW-22,31,draw);if(draw){ctx.fillStyle=col("--series-2");ctx.fillRect(P,y0,5,y-y0-8);}}
      y+=26;
      ctx.font="22px "+sans;ctx.fillStyle=col("--text-primary");if(draw){ctx.font="700 26px "+sans;ctx.fillText("deadliestday.org",P,y+26);ctx.font="18px "+sans;ctx.fillStyle=col("--text-muted");ctx.textAlign="right";ctx.fillText("Source: NHTSA FARS, 2000–2024",W-P,y+26);ctx.textAlign="left";}
      return y+26+P;
    }
    layout(false);const H=Math.ceil(layout(false));
    cv.width=W;cv.height=H;
    const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,"#1c1030");g.addColorStop(1,"#0e0916");ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    const sw=ctx.createRadialGradient(W*.9,0,0,W*.9,0,500);sw.addColorStop(0,"rgba(120,70,190,.35)");sw.addColorStop(1,"rgba(120,70,190,0)");ctx.fillStyle=sw;ctx.fillRect(0,0,W,H);
    layout(true);
    return new Promise(res=>cv.toBlob(res,"image/png"));
  }
  async function save(card){
    try{const blob=await makeImage(card),a=document.createElement("a");
      a.href=URL.createObjectURL(blob);a.download="deadliestday-"+card.id.replace(/^s-/,"")+".png";document.body.appendChild(a);a.click();a.remove();
      setTimeout(()=>URL.revokeObjectURL(a.href),4000);return true;}
    catch(e){say("Sorry, the image could not be created in this browser.");return false;}
  }
  function shareText(card){return card.id==="s-days"?document.getElementById("calnote").textContent:SHARE[card.id];}

  // image cache per card, cleared whenever the chart redraws (tab / selection change)
  const cache=new WeakMap();
  function getBlob(card){
    if(!cache.has(card))cache.set(card,makeImage(card));
    return cache.get(card);
  }
  const canShareFiles=()=>{try{return matchMedia("(pointer:coarse)").matches&&navigator.canShare&&navigator.canShare({files:[new File([""],"x.png",{type:"image/png"})]});}catch(e){return false;}};

  async function share(card){
    const text=shareText(card),url=SITE+"#"+card.id;
    if(canShareFiles()){
      // phones and tablets: native share sheet with the image attached
      const blob=await getBlob(card),file=new File([blob],"deadliestday-"+card.id.replace(/^s-/,"")+".png",{type:"image/png"});
      try{await navigator.share({files:[file],text:text+"\n"+url});}
      catch(e){if(e.name==="NotAllowedError")say("Tap Share again to open the share sheet.");else if(e.name!=="AbortError")say("Sharing isn't available here. Use Save image instead.");}
      return;
    }
    // computers: open a Bluesky draft with the text and link, and put the image on the clipboard to paste in
    window.open("https://bsky.app/intent/compose?text="+encodeURIComponent(text+"\n"+url),"_blank","noopener");
    try{
      const blob=await getBlob(card);
      await navigator.clipboard.write([new ClipboardItem({"image/png":blob})]);
      say("Image copied. Paste it into your Bluesky post (Ctrl+V or Cmd+V).");
    }catch(e){
      if(await save(card))say("Image saved. Attach it to your Bluesky post.");
    }
  }

  document.querySelectorAll("section.card[id^=s-]").forEach(card=>{
    const tools=document.createElement("div");tools.className="tools";
    tools.innerHTML='<button data-act="img" title="Download this chart as a PNG">Save image</button><button data-act="share" title="Share this chart with its image">Share</button>';
    card.insertBefore(tools,card.firstChild);
    const svg=card.querySelector("svg");
    if(svg)new MutationObserver(()=>cache.delete(card)).observe(svg,{childList:true});
    const sb=tools.querySelector("[data-act=share]");
    ["pointerenter","focus","touchstart"].forEach(ev=>sb.addEventListener(ev,()=>getBlob(card),{passive:true}));
    tools.querySelector("[data-act=img]").onclick=async()=>{if(await save(card))say("Image saved.");};
    sb.onclick=()=>share(card);
  });
})();
