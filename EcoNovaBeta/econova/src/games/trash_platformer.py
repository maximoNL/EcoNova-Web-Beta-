"""Game A - Eco-Runner: Trash Collect & Sort (10 levels, SDG 13).

A self-contained HTML5 Canvas game (no external assets). ``get_trash_platformer_html``
returns the page to embed with ``streamlit.components.v1.html(..., height=620)``.
"""
from __future__ import annotations

import json

LEVELS = 10

WASTE_ITEMS = [
    {"id": "newspaper", "name": "Newspaper", "bin": "paper",
     "reason": "Paper fibres can be recycled into new paper."},
    {"id": "plastic_bottle", "name": "Plastic Bottle", "bin": "plastic",
     "reason": "Plastic bottles are collected with plastics so they can be recycled."},
    {"id": "glass_jar", "name": "Glass Jar", "bin": "glass",
     "reason": "Glass can be recycled again and again."},
    {"id": "banana_peel", "name": "Banana Peel", "bin": "organic",
     "reason": "Food scraps are organic. Rotting in a landfill they release methane, a greenhouse gas."},
    {"id": "cardboard_box", "name": "Cardboard Box", "bin": "paper",
     "reason": "Cardboard is made of paper fibres and goes with paper."},
    {"id": "plastic_cup", "name": "Plastic Cup", "bin": "plastic",
     "reason": "A plastic cup is plastic, so it goes in the plastic bin."},
    {"id": "glass_bottle", "name": "Glass Bottle", "bin": "glass",
     "reason": "Glass bottles go with glass, never with plastic."},
    {"id": "apple_core", "name": "Apple Core", "bin": "organic",
     "reason": "An apple core is organic waste that can rot and return to the soil as compost."},
]

BINS = [
    {"id": "paper", "label": "Paper/Cardboard", "color": "#3b82c4"},
    {"id": "plastic", "label": "Plastic", "color": "#e0a526"},
    {"id": "glass", "label": "Glass", "color": "#2f9e6f"},
    {"id": "organic", "label": "Organic", "color": "#8a5a36"},
]

SECRET_MESSAGE = (
    "Every item you sorted is a small climate action. Food scraps that rot in a landfill release methane, "
    "a greenhouse gas that warms the planet, so sorting waste properly helps protect the climate (SDG 13). "
    "And when you share what you learned with a friend, you are also supporting quality education (SDG 4)."
)

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Eco-Runner</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#0f2a1d;color:#D8F3DC;font-family:'Segoe UI',Arial,sans-serif;overflow:hidden}
#wrap{display:flex;flex-direction:column;align-items:center}
#bar{font-size:13px;padding:6px 10px;text-align:center;line-height:1.3}
canvas{display:block;width:100%;height:auto;max-width:min(1000px,calc((100vh - 52px) * 1.7778));background:#cfeedd;border-radius:10px;outline:none}
</style></head><body><div id="wrap">
<div id="bar"><b>Eco-Runner</b> &middot; Move: A/D or Arrow keys &middot; Jump: W, Up or Space &middot; Sort: drag item to a bin, click a bin, or press 1-4 &middot; Click the game first</div>
<canvas id="game" width="960" height="540" tabindex="0"></canvas></div>
<script>
(function(){
"use strict";
const CFG = __CONFIG__;
const W=960,H=540,GROUND=480,SPEED=260,GRAV=1800,JUMP=640;
const cv=document.getElementById('game'),ctx=cv.getContext('2d');
const ITEMS=CFG.items,BINS=CFG.bins,TOTAL=CFG.levels;
const keys={};let state='menu',level=1,score=0,scoreAtStart=0,time=0,tAnim=0,worldW=1600;
let P,platforms,items,obstacles,collected,queue,floaters=[],feedback=null,shake={i:-1,t:0},trans=0,bonus=0,confetti=[];
let drag=null,itemPos={x:480,y:190},camX=0;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const levelTime=n=>Math.round(90-(n-1)*10/3);
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
function wrap(text,maxW,font){ctx.font=font;const out=[];let line='';for(const w of text.split(' ')){const t=line?line+' '+w:w;if(ctx.measureText(t).width>maxW&&line){out.push(line);line=w;}else line=t;}if(line)out.push(line);return out;}
function centerText(text,y,font,color,maxW){const ls=wrap(text,maxW||820,font);ctx.font=font;ctx.fillStyle=color;ctx.textAlign='center';ls.forEach((l,i)=>ctx.fillText(l,W/2,y+i*parseInt(font,10)*1.35));ctx.textAlign='left';return ls.length;}

/* ---------- level generation (seeded, so every level is the same each time) ---------- */
function buildLevel(n){
  const rng=mulberry32(n*7919+13);
  worldW=1500+n*110;platforms=[];obstacles=[];items=[];collected=[];
  if(n<3){platforms.push({x:0,y:GROUND,w:worldW,h:60,ground:true});}
  else{
    const pitMax=Math.min(120,40+n*8);let x=0;
    while(x<worldW-400){const len=x===0?420:300+rng()*250;platforms.push({x:x,y:GROUND,w:len,h:60,ground:true});x+=len+50+rng()*(pitMax-50);}
    platforms.push({x:x,y:GROUND,w:worldW-x,h:60,ground:true});
  }
  const maxGap=40+n*7,riseMax=50+n*4,minY=330-n*17;
  let px=220,py=GROUND-80;
  while(px<worldW-250){
    const w=Math.max(90,170-n*6+rng()*60);
    platforms.push({x:px,y:py,w:w,h:16,ground:false});
    px+=w+30+rng()*(maxGap-30);
    py=clamp(py+(rng()*2-1)*riseMax,minY,GROUND-70);
  }
  const spots=[];
  platforms.forEach(p=>{
    if(!p.ground)spots.push({x:p.x+p.w/2,y:p.y-24});
    else for(let sx=p.x+60;sx<p.x+p.w-40;sx+=200)if(sx>260)spots.push({x:sx,y:GROUND-24});
  });
  const count=7+n;
  for(let sx=300;spots.length<count;sx+=140)spots.push({x:sx,y:GROUND-24});
  spots.sort((a,b)=>a.x-b.x);
  for(let i=0;i<count;i++){
    const s=spots[Math.min(spots.length-1,Math.floor((i+rng()*0.6)*spots.length/count))];
    items.push({x:s.x,y:s.y,def:ITEMS[i%ITEMS.length],got:false});
  }
  const nObs=Math.floor((n+1)/2),homes=platforms.filter(p=>p.x>350&&p.w>=(p.ground?250:140));
  for(let i=0;i<nObs&&homes.length;i++){
    const p=homes.splice(Math.floor(rng()*homes.length),1)[0];
    obstacles.push({x:p.x+20,y:p.y-28,w:34,h:28,min:p.x+8,max:p.x+p.w-42,dir:1,speed:50+n*10});
  }
  P={x:60,y:GROUND-40,w:28,h:40,vx:0,vy:0,face:1,onGround:false,coyote:0,buffer:0,inv:0,safe:{x:60,y:GROUND-40},jumpHeld:false};
  time=levelTime(n);floaters=[];feedback=null;
}
function startLevel(n){level=n;scoreAtStart=score;buildLevel(n);state='intro';}
function say(text,x,y,color){floaters.push({text:text,x:x,y:y,t:1.2,color:color||'#fff'});}

/* ---------- input ---------- */
const JUMPS=['KeyW','ArrowUp','Space'];
window.addEventListener('keydown',e=>{
  if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();
  if(!keys[e.code]&&JUMPS.includes(e.code)&&P)P.buffer=0.12;
  keys[e.code]=true;
  if(e.code==='Enter'||e.code==='Space')advance();
  if(state==='sort'&&e.code.startsWith('Digit')){const i=parseInt(e.code.slice(5),10)-1;if(i>=0&&i<BINS.length)place(i);}
});
window.addEventListener('keyup',e=>{keys[e.code]=false;});
window.addEventListener('blur',()=>{for(const k in keys)keys[k]=false;});
function advance(){
  if(state==='menu'){score=0;startLevel(1);}
  else if(state==='intro'){state='play';}
  else if(state==='levelDone'){if(level>=TOTAL){state='victory';for(let i=0;i<120;i++)confetti.push({x:Math.random()*W,y:-Math.random()*H,v:60+Math.random()*120,c:['#2D6A4F','#D8F3DC','#e0a526','#3b82c4'][i%4]});}else startLevel(level+1);}
  else if(state==='timeup'){score=scoreAtStart;startLevel(level);}
  else if(state==='victory'){score=0;startLevel(1);}
}
function mouse(e){const r=cv.getBoundingClientRect();return{x:(e.clientX-r.left)*W/r.width,y:(e.clientY-r.top)*H/r.height};}
const binRect=i=>({x:38+i*228,y:370,w:200,h:140});
function binAt(m){for(let i=0;i<BINS.length;i++){const b=binRect(i);if(m.x>=b.x&&m.x<=b.x+b.w&&m.y>=b.y&&m.y<=b.y+b.h)return i;}return -1;}
cv.addEventListener('pointerdown',e=>{
  cv.focus();const m=mouse(e);
  if(state==='sort'&&queue.length){
    if(Math.hypot(m.x-itemPos.x,m.y-itemPos.y)<80){drag={dx:itemPos.x-m.x,dy:itemPos.y-m.y,moved:false};cv.setPointerCapture(e.pointerId);return;}
    const b=binAt(m);if(b>=0){place(b);return;}
  } else if(state!=='play'&&state!=='transition'){advance();}
});
cv.addEventListener('pointermove',e=>{if(!drag)return;const m=mouse(e);itemPos.x=m.x+drag.dx;itemPos.y=m.y+drag.dy;drag.moved=true;});
cv.addEventListener('pointerup',e=>{
  if(!drag)return;const m=mouse(e);const moved=drag.moved;drag=null;
  const b=binAt({x:itemPos.x,y:itemPos.y+30});itemPos={x:480,y:190};
  if(moved&&b>=0)place(b);
});

/* ---------- sorting ---------- */
function place(i){
  if(!queue.length)return;const it=queue[0],right=BINS.findIndex(b=>b.id===it.def.bin);
  if(i===right){
    queue.shift();score+=20;
    feedback={ok:true,t:3,text:'Correct! '+it.def.name+' goes in '+BINS[right].label+'. '+it.def.reason};
    if(!queue.length){bonus=Math.round(Math.max(0,time))*2;score+=bonus;state='levelDone';}
  }else{
    shake={i:i,t:0.5};
    feedback={ok:false,t:5,text:'Not quite! '+it.def.name+' does not go in '+BINS[i].label+'. It goes in '+BINS[right].label+'. '+it.def.reason+' Try again!'};
  }
}

/* ---------- update ---------- */
function update(dt){
  tAnim+=dt;
  floaters.forEach(f=>{f.t-=dt;f.y-=30*dt;});floaters=floaters.filter(f=>f.t>0);
  if(feedback){feedback.t-=dt;if(feedback.t<=0&&state==='sort')feedback.t=0;}
  if(shake.t>0)shake.t-=dt;
  if(state==='victory')confetti.forEach(c=>{c.y+=c.v*dt;if(c.y>H)c.y=-10;});
  if(state==='transition'){trans-=dt;if(trans<=0){state='sort';queue=collected.slice();itemPos={x:480,y:190};feedback=null;}return;}
  if(state!=='play')return;
  const l=keys.KeyA||keys.ArrowLeft,r=keys.KeyD||keys.ArrowRight,ax=(r?1:0)-(l?1:0);
  P.vx=ax*SPEED;if(ax)P.face=ax;
  P.coyote-=dt;P.buffer-=dt;P.inv-=dt;
  const jh=keys.KeyW||keys.ArrowUp||keys.Space;
  if(P.buffer>0&&P.coyote>0){P.vy=-JUMP;P.buffer=0;P.coyote=0;P.onGround=false;}
  if(!jh&&P.vy<-260)P.vy=-260;
  P.vy=Math.min(P.vy+GRAV*dt,1100);
  const prevBottom=P.y+P.h;
  P.x=clamp(P.x+P.vx*dt,0,worldW-P.w);P.y+=P.vy*dt;P.onGround=false;
  if(P.vy>=0){
    for(const p of platforms){
      if(P.x+P.w>p.x+2&&P.x<p.x+p.w-2&&prevBottom<=p.y+2&&P.y+P.h>=p.y){
        P.y=p.y-P.h;P.vy=0;P.onGround=true;
        if(p.w>80&&P.x>p.x+20&&P.x+P.w<p.x+p.w-20)P.safe={x:P.x,y:P.y};
        break;
      }
    }
  }
  if(P.onGround)P.coyote=0.1;
  if(P.y>H+80){time-=3;say('-3s (pit!)',P.x,GROUND-90,'#fecaca');P.x=P.safe.x;P.y=P.safe.y;P.vy=0;}
  obstacles.forEach(o=>{
    o.x+=o.dir*o.speed*dt;if(o.x<o.min){o.x=o.min;o.dir=1;}if(o.x>o.max){o.x=o.max;o.dir=-1;}
    if(P.inv<=0&&P.x<o.x+o.w&&P.x+P.w>o.x&&P.y<o.y+o.h&&P.y+P.h>o.y){time-=4;P.inv=1.5;P.vy=-300;say('-4s (smog!)',P.x,P.y-10,'#fecaca');}
  });
  items.forEach(it=>{
    if(!it.got&&Math.hypot(it.x-(P.x+P.w/2),it.y-(P.y+P.h/2))<30){it.got=true;collected.push(it);score+=10;say('+10 '+it.def.name,it.x,it.y-20,'#fff7a8');}
  });
  time-=dt;
  if(time<=0){time=0;state='timeup';}
  else if(collected.length===items.length){state='transition';trans=1.1;}
  camX=clamp(P.x+P.w/2-W*0.4,0,worldW-W);
}

/* ---------- drawing ---------- */
function drawItem(id,x,y,s){
  ctx.save();ctx.translate(x,y);ctx.scale(s,s);ctx.lineWidth=1.5;ctx.strokeStyle='rgba(0,0,0,.35)';
  const f=(c)=>{ctx.fillStyle=c;};
  if(id==='newspaper'){ctx.rotate(-0.15);f('#f1f1ea');rr(-16,-14,32,28,2);ctx.fill();ctx.stroke();f('#333');ctx.fillRect(-12,-10,24,5);f('#777');for(let i=0;i<3;i++)ctx.fillRect(-12,-2+i*5,i===2?12:24,2);}
  else if(id==='plastic_bottle'){f('rgba(120,190,235,.9)');rr(-8,-8,16,26,4);ctx.fill();ctx.stroke();ctx.fillRect(-4,-15,8,8);f('#2563eb');ctx.fillRect(-5,-20,10,5);f('rgba(255,255,255,.8)');ctx.fillRect(-8,2,16,6);}
  else if(id==='glass_jar'){f('rgba(190,235,215,.75)');rr(-12,-8,24,24,5);ctx.fill();ctx.stroke();f('#d4a017');ctx.fillRect(-13,-14,26,6);f('rgba(255,255,255,.7)');ctx.fillRect(-8,-3,3,14);}
  else if(id==='banana_peel'){ctx.rotate(0.2);f('#f6d533');ctx.beginPath();ctx.moveTo(-16,6);ctx.quadraticCurveTo(0,-22,16,4);ctx.quadraticCurveTo(0,-6,-16,6);ctx.fill();ctx.stroke();f('#6b4a1a');ctx.fillRect(13,0,5,5);ctx.beginPath();ctx.moveTo(-4,4);ctx.quadraticCurveTo(0,16,10,14);ctx.quadraticCurveTo(2,10,-4,4);f('#f1c40f');ctx.fill();}
  else if(id==='cardboard_box'){f('#c8914f');ctx.fillRect(-16,-12,32,26);ctx.strokeRect(-16,-12,32,26);f('#e3b779');ctx.fillRect(-4,-12,8,26);f('#a9763a');ctx.fillRect(-16,-12,32,4);}
  else if(id==='plastic_cup'){f('#ef6f6c');ctx.beginPath();ctx.moveTo(-11,-14);ctx.lineTo(11,-14);ctx.lineTo(8,16);ctx.lineTo(-8,16);ctx.closePath();ctx.fill();ctx.stroke();f('#fff');ctx.fillRect(-12,-16,24,4);}
  else if(id==='glass_bottle'){f('#2f9e6f');rr(-8,-2,16,22,4);ctx.fill();ctx.stroke();ctx.fillRect(-3,-16,6,16);f('#1f6b4a');ctx.fillRect(-4,-20,8,5);f('rgba(255,255,255,.55)');ctx.fillRect(-5,2,2,12);}
  else if(id==='apple_core'){f('#d64545');ctx.beginPath();ctx.ellipse(0,-9,10,6,0,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.ellipse(0,10,10,6,0,0,Math.PI*2);ctx.fill();f('#f7f1d8');ctx.fillRect(-5,-9,10,20);ctx.strokeRect(-5,-9,10,20);f('#5a3a1a');ctx.fillRect(-1,-4,2,3);ctx.fillRect(-1,3,2,3);ctx.fillRect(-1,-18,2,8);}
  ctx.restore();
}
function drawBg(){
  const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#bfe6f5');g.addColorStop(1,'#e8f7ea');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#fff6bf';ctx.beginPath();ctx.arc(820,80,38,0,7);ctx.fill();
  ctx.fillStyle='rgba(255,255,255,.85)';for(let i=0;i<7;i++){const cx=((i*260-camX*0.3)%1700+1700)%1700-150;ctx.beginPath();ctx.arc(cx,90+(i%3)*40,26,0,7);ctx.arc(cx+30,84+(i%3)*40,32,0,7);ctx.arc(cx+62,92+(i%3)*40,24,0,7);ctx.fill();}
  ctx.fillStyle='#a8d5ba';ctx.beginPath();ctx.moveTo(0,H);for(let x=0;x<=W;x+=40){ctx.lineTo(x,330+Math.sin((x+camX*0.2)/90)*30);}ctx.lineTo(W,H);ctx.fill();
  ctx.fillStyle='#7fbf9a';ctx.beginPath();ctx.moveTo(0,H);for(let x=0;x<=W;x+=40){ctx.lineTo(x,400+Math.sin((x+camX*0.5)/60+2)*22);}ctx.lineTo(W,H);ctx.fill();
}
function drawWorld(){
  ctx.fillStyle='#16352a';ctx.fillRect(0,GROUND+10,W,H);
  platforms.forEach(p=>{
    const x=p.x-camX;if(x>W||x+p.w<0)return;
    if(p.ground){ctx.fillStyle='#7a5230';ctx.fillRect(x,p.y,p.w,p.h);ctx.fillStyle='#5f3f23';for(let dx=10;dx<p.w;dx+=34)ctx.fillRect(x+dx,p.y+22+(dx%3)*9,8,5);ctx.fillStyle='#3f9b61';ctx.fillRect(x,p.y,p.w,10);}
    else{ctx.fillStyle='#8a5c34';rr(x,p.y,p.w,p.h,5);ctx.fill();ctx.fillStyle='#3f9b61';rr(x,p.y-3,p.w,9,4);ctx.fill();}
  });
  items.forEach((it,i)=>{if(it.got)return;const bob=Math.sin(tAnim*3+i)*3;ctx.fillStyle='rgba(255,255,255,.55)';ctx.beginPath();ctx.arc(it.x-camX,it.y+bob,24,0,7);ctx.fill();drawItem(it.def.id,it.x-camX,it.y+bob,1);});
  obstacles.forEach(o=>{
    const x=o.x-camX+o.w/2,y=o.y+o.h/2;ctx.fillStyle='#8b94a0';
    ctx.beginPath();ctx.arc(x-9,y+2,11,0,7);ctx.arc(x+9,y+2,11,0,7);ctx.arc(x,y-4,13,0,7);ctx.fill();
    ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(x-5,y-3,4,0,7);ctx.arc(x+5,y-3,4,0,7);ctx.fill();ctx.fillStyle='#222';ctx.beginPath();ctx.arc(x-5+o.dir*1.5,y-3,2,0,7);ctx.arc(x+5+o.dir*1.5,y-3,2,0,7);ctx.fill();
  });
  const px=P.x-camX;
  if(P.inv<=0||Math.floor(tAnim*12)%2===0){
    const step=P.onGround&&P.vx?Math.sin(tAnim*16)*6:0;
    ctx.fillStyle='#24456b';ctx.fillRect(px+5,P.y+28,7,12+step*0.3);ctx.fillRect(px+16,P.y+28,7,12-step*0.3);
    ctx.fillStyle='#2D6A4F';rr(px+2,P.y+12,24,19,5);ctx.fill();
    ctx.fillStyle='#f0c9a0';ctx.beginPath();ctx.arc(px+14,P.y+8,9,0,7);ctx.fill();
    ctx.fillStyle='#1B4332';ctx.beginPath();ctx.arc(px+14,P.y+5,9,Math.PI,0);ctx.fill();ctx.fillStyle='#74c69d';ctx.beginPath();ctx.ellipse(px+14+P.face*8,P.y-2,6,3,P.face*0.6,0,7);ctx.fill();
    ctx.fillStyle='#222';ctx.fillRect(px+14+P.face*4-1,P.y+7,3,3);
  }
  floaters.forEach(f=>{ctx.globalAlpha=Math.min(1,f.t);ctx.font='bold 15px Segoe UI,Arial';ctx.fillStyle=f.color;ctx.strokeStyle='rgba(0,0,0,.5)';ctx.lineWidth=3;ctx.strokeText(f.text,f.x-camX,f.y);ctx.fillText(f.text,f.x-camX,f.y);ctx.globalAlpha=1;});
}
function hud(){
  ctx.fillStyle='rgba(15,42,29,.78)';rr(10,10,940,40,10);ctx.fill();ctx.font='bold 17px Segoe UI,Arial';ctx.fillStyle='#D8F3DC';
  ctx.fillText('Level '+level+' / '+TOTAL,26,36);ctx.fillText('Items '+collected.length+' / '+items.length,200,36);
  ctx.fillStyle=time<=10?'#fca5a5':'#D8F3DC';ctx.fillText('Time '+Math.ceil(time)+'s',390,36);ctx.fillStyle='#D8F3DC';ctx.fillText('Score '+score,560,36);
}
function panel(title,lines,hint){
  ctx.fillStyle='rgba(15,42,29,.88)';rr(120,90,720,360,18);ctx.fill();
  ctx.font='bold 34px Segoe UI,Arial';ctx.fillStyle='#D8F3DC';ctx.textAlign='center';ctx.fillText(title,W/2,148);ctx.textAlign='left';
  let y=198;lines.forEach(t=>{y+=centerText(t,y,'19px Segoe UI,Arial','#F8FAF9',640)*26+6;});
  ctx.font='bold 17px Segoe UI,Arial';ctx.fillStyle='#74c69d';ctx.textAlign='center';ctx.fillText(hint,W/2,428);ctx.textAlign='left';
}
function drawBin(i){
  const b=binRect(i),bin=BINS[i],dx=shake.t>0&&shake.i===i?Math.sin(shake.t*60)*6:0,x=b.x+dx;
  ctx.fillStyle=bin.color;rr(x,b.y+22,b.w,b.h-22,12);ctx.fill();ctx.fillStyle='rgba(0,0,0,.25)';rr(x-6,b.y,b.w+12,26,8);ctx.fill();
  ctx.fillStyle='rgba(255,255,255,.18)';for(let k=1;k<4;k++)ctx.fillRect(x+k*b.w/4,b.y+34,3,b.h-50);
  ctx.fillStyle='#fff';ctx.font='bold 21px Segoe UI,Arial';ctx.textAlign='center';ctx.fillText(bin.label,x+b.w/2,b.y+88);ctx.font='bold 17px Segoe UI,Arial';ctx.fillText('Key '+(i+1),x+b.w/2,b.y+118);ctx.textAlign='left';
}
function drawSort(){
  const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#1B4332');g.addColorStop(1,'#2D6A4F');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.textAlign='center';ctx.fillStyle='#D8F3DC';ctx.font='bold 30px Segoe UI,Arial';ctx.fillText('Sorting Challenge',W/2,48);
  ctx.font='17px Segoe UI,Arial';ctx.fillText('Level '+level+': put each item in the right bin ('+queue.length+' left). Drag it, click a bin, or press 1-4.',W/2,78);ctx.textAlign='left';
  if(queue.length){ctx.fillStyle='rgba(255,255,255,.14)';ctx.beginPath();ctx.arc(itemPos.x,itemPos.y,70,0,7);ctx.fill();drawItem(queue[0].def.id,itemPos.x,itemPos.y,2.4);
    ctx.textAlign='center';ctx.font='bold 22px Segoe UI,Arial';ctx.fillStyle='#fff';ctx.fillText(queue[0].def.name,W/2,285);ctx.textAlign='left';}
  queue.slice(1,9).forEach((q,i)=>drawItem(q.def.id,60+i*38,130,0.8));
  if(feedback&&feedback.t>0)centerText(feedback.text,318,'bold 16px Segoe UI,Arial',feedback.ok?'#b7f5c8':'#ffd0a8',860);
  for(let i=0;i<BINS.length;i++)drawBin(i);
}
function draw(){
  ctx.clearRect(0,0,W,H);
  if(state==='sort'){drawSort();return;}
  if(state==='levelDone'){drawSort();panel('Level '+level+' complete!',['All items sorted correctly. Time bonus: +'+bonus+'. Score: '+score+'.',level<TOTAL?'Next up: Level '+(level+1)+' with higher platforms, wider gaps and faster smog clouds.':'You finished the final level!'],'Press Enter or click to continue');return;}
  if(state==='victory'){
    const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#1B4332');g.addColorStop(1,'#2D6A4F');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    confetti.forEach(c=>{ctx.fillStyle=c.c;ctx.fillRect(c.x,c.y,8,8);});
    ctx.textAlign='center';ctx.fillStyle='#D8F3DC';ctx.font='bold 38px Segoe UI,Arial';ctx.fillText('You cleared all 10 levels!',W/2,80);ctx.font='20px Segoe UI,Arial';ctx.fillText('Final score: '+score,W/2,116);ctx.textAlign='left';
    ctx.fillStyle='rgba(248,250,249,.96)';rr(110,150,740,250,18);ctx.fill();ctx.textAlign='center';ctx.fillStyle='#1B4332';ctx.font='bold 22px Segoe UI,Arial';ctx.fillText('Secret SDG 13 Climate Action Message',W/2,190);ctx.textAlign='left';
    centerText(CFG.secret,226,'19px Segoe UI,Arial','#1E293B',660);
    ctx.textAlign='center';ctx.fillStyle='#D8F3DC';ctx.font='bold 17px Segoe UI,Arial';ctx.fillText('Press Enter or click to play again',W/2,450);ctx.textAlign='left';return;}
  if(!P){drawBg();panel('Eco-Runner',['Collect the waste scattered around each level before time runs out, then sort it into the right bins.','10 levels: higher platforms, wider gaps, moving smog clouds and less time.'],'Press Enter or click to start');return;}
  drawBg();drawWorld();hud();
  if(state==='intro')panel('Level '+level+' of '+TOTAL,['Collect all '+items.length+' waste items in '+levelTime(level)+' seconds.','Avoid the smog clouds (-4s) and the pits (-3s).'],'Press Enter or click to go');
  if(state==='transition'){ctx.fillStyle='rgba(15,42,29,.7)';ctx.fillRect(0,230,W,80);centerText('All items collected! Time to sort!',282,'bold 30px Segoe UI,Arial','#D8F3DC');}
  if(state==='timeup')panel("Time's up!",['You collected '+collected.length+' of '+items.length+' items. Try the level again, you can do it!'],'Press Enter or click to retry');
}
let last=performance.now();
function frame(now){const dt=Math.min(0.033,(now-last)/1000);last=now;update(dt);draw();requestAnimationFrame(frame);}
requestAnimationFrame(frame);
window.__eco={get state(){return state;},get level(){return level;},keys:keys,advance:advance,place:place,get P(){return P;},get items(){return items;},get queue(){return queue;},startLevel:startLevel,update:update,draw:draw,get platforms(){return platforms;},get obstacles(){return obstacles;},get time(){return time;},set time(v){time=v;}};
})();
</script></body></html>
"""


def get_trash_platformer_html() -> str:
    """Return the complete Eco-Runner HTML page."""
    config = {"items": WASTE_ITEMS, "bins": BINS, "levels": LEVELS, "secret": SECRET_MESSAGE}
    return _TEMPLATE.replace("__CONFIG__", json.dumps(config))
