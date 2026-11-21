"""Game B - Eco-School Quiz Quest (SDG 4): a calm, top-down classroom adventure.

Inspired by classic school-hallway games but with NO jumpscares, horror, chasing or
frightening audio/visuals (the game has no sound at all). Collect 7 Eco-Notebooks;
each opens a 3-question quiz (20 seconds per question). A friendly guide wanders the
hallway and shares tips.
"""
from __future__ import annotations

import json

NOTEBOOKS = 7
SECONDS_PER_QUESTION = 20

# Each notebook holds 3 questions: q, four options, answer index, hint, explanation.
QUIZ = [
    [  # 1. The goals
        {"q": "What is the focus of Sustainable Development Goal 4 (SDG 4)?",
         "o": ["Climate Action", "Quality Education", "Clean Water", "Zero Hunger"], "a": 1,
         "hint": "Think about schools, teachers and learning.",
         "e": "SDG 4 is Quality Education."},
        {"q": "What is the focus of Sustainable Development Goal 13 (SDG 13)?",
         "o": ["Life on Land", "Affordable Energy", "Climate Action", "Quality Education"], "a": 2,
         "hint": "It is about protecting our climate.",
         "e": "SDG 13 is Climate Action."},
        {"q": "How many Sustainable Development Goals are there?",
         "o": ["10", "12", "17", "20"], "a": 2,
         "hint": "It is more than 12 and fewer than 20.",
         "e": "There are 17 Sustainable Development Goals."},
    ],
    [  # 2. Climate facts from the EcoNova page
        {"q": "Roughly how much of the extra heat from global warming is absorbed by the oceans?",
         "o": ["About 15 out of 100", "About 50 out of 100", "About 85 out of 100", "About 100 out of 100"], "a": 2,
         "hint": "It is most of it. Oceans cover a huge part of our planet.",
         "e": "Roughly 85% of the excess heat is absorbed by the oceans."},
        {"q": "Nearly all UN member states joined which agreement to limit global warming?",
         "o": ["The Montreal Protocol", "The Geneva Conventions", "The Antarctic Treaty", "The Paris Agreement"], "a": 3,
         "hint": "It is named after a European capital famous for the Eiffel Tower.",
         "e": "Nearly all UN member states joined the Paris Agreement."},
        {"q": "Which greenhouse gas do rotting food scraps release in a landfill?",
         "o": ["Helium", "Methane", "Neon", "Oxygen"], "a": 1,
         "hint": "It is the gas that proper waste separation helps reduce in landfills.",
         "e": "Landfills with organic waste release methane, a greenhouse gas."},
    ],
    [  # 3. Waste bins
        {"q": "Which bin does a banana peel go in?",
         "o": ["Plastic", "Glass", "Paper/Cardboard", "Organic"], "a": 3,
         "hint": "It is food waste that can rot.",
         "e": "A banana peel is organic waste."},
        {"q": "Which bin does a glass jar go in?",
         "o": ["Glass", "Organic", "Plastic", "Paper/Cardboard"], "a": 0,
         "hint": "Match the material of the jar to the bin.",
         "e": "Glass jars go in the glass bin."},
        {"q": "Which bin does a cardboard box go in?",
         "o": ["Glass", "Paper/Cardboard", "Organic", "Plastic"], "a": 1,
         "hint": "Cardboard is made from paper fibres.",
         "e": "Cardboard goes with paper."},
    ],
    [  # 4. Green habits
        {"q": "How does a reusable water bottle help the climate?",
         "o": ["It cuts emissions from making single-use plastic", "It makes water colder", "It makes rain", "It cleans the air"], "a": 0,
         "hint": "Think about what you do NOT need to buy and throw away.",
         "e": "Fewer single-use plastic bottles means fewer emissions from producing them."},
        {"q": "Why should we turn off unused lights and unplug chargers?",
         "o": ["To make rooms darker", "To save energy and reduce emissions", "To fix the wires", "To make devices heavier"], "a": 1,
         "hint": "Less electricity used means less pollution made.",
         "e": "Saving energy helps reduce the emissions linked to electricity."},
        {"q": "Which of these is a green daily tip?",
         "o": ["Take only the food you will eat", "Leave the lights on all day", "Use one side of paper only", "Buy a new bottle every day"], "a": 0,
         "hint": "Which choice creates less waste?",
         "e": "Taking only the food you will eat reduces food waste."},
    ],
    [  # 5. General climate literacy
        {"q": "Burning fossil fuels mainly releases which greenhouse gas?",
         "o": ["Carbon dioxide", "Helium", "Hydrogen", "Nitrogen"], "a": 0,
         "hint": "Its chemical formula is CO2.",
         "e": "Burning coal, oil and gas releases carbon dioxide."},
        {"q": "What does 'carbon footprint' mean?",
         "o": ["The mark a shoe leaves", "The greenhouse gases caused by our activities", "The size of a forest", "The weight of a pencil"], "a": 1,
         "hint": "It measures our impact on the climate.",
         "e": "A carbon footprint is the amount of greenhouse gases our activities cause."},
        {"q": "For a short trip, which option usually causes the least emissions?",
         "o": ["Car alone", "Motorbike", "Walking or cycling", "Taxi"], "a": 2,
         "hint": "It uses your own energy instead of fuel.",
         "e": "Walking or cycling produces almost no emissions."},
    ],
    [  # 6. Energy and the three Rs
        {"q": "Which of these is a renewable energy source?",
         "o": ["Coal", "Solar power", "Oil", "Natural gas"], "a": 1,
         "hint": "It comes from the sun.",
         "e": "Solar power is renewable; coal, oil and gas are fossil fuels."},
        {"q": "Complete the three Rs: Reduce, Reuse, ...",
         "o": ["Repair", "Return", "Recycle", "Rewind"], "a": 2,
         "hint": "It is what we do with paper, glass and plastic in the right bin.",
         "e": "The three Rs are Reduce, Reuse, Recycle."},
        {"q": "What does it mean to 'reduce' waste?",
         "o": ["Use fewer disposable things", "Throw things farther away", "Burn rubbish", "Hide the bin"], "a": 0,
         "hint": "The best waste is the waste we never make.",
         "e": "Reducing means making less waste in the first place."},
    ],
    [  # 7. Education and action
        {"q": "Why does education (SDG 4) matter for climate action?",
         "o": ["It does not matter", "Learning helps people understand and change habits", "It makes the weather warmer", "It replaces recycling"], "a": 1,
         "hint": "When people understand a problem, they can act on it.",
         "e": "Learning helps people understand climate change and choose greener habits."},
        {"q": "You do not have to change everything at once. A good start is...",
         "o": ["All habits at the same time", "Nothing until you are older", "One weekly habit", "Ten habits tomorrow"], "a": 2,
         "hint": "Small steps are easier to keep.",
         "e": "Starting with one weekly habit is a great way to begin."},
        {"q": "Which action spreads green habits at school?",
         "o": ["Keep your habits secret", "Teach a peer a green habit", "Ignore the recycling bins", "Waste more paper"], "a": 1,
         "hint": "Sharing what you know helps everyone.",
         "e": "Teaching a peer a green habit multiplies your impact."},
    ],
]

GUIDE_TIPS = [
    "SDG 4 is Quality Education and SDG 13 is Climate Action.",
    "Roughly 85% of the excess heat from global warming is absorbed by the oceans.",
    "Separating waste properly helps reduce methane from landfills.",
    "Turn off unused lights and unplug chargers to save energy.",
    "Starting with one weekly habit is enough. You do not have to change everything at once.",
    "Teach a friend a green habit. Sharing knowledge is SDG 4 in action!",
]

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Eco-School Quiz Quest</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#0f2a1d;color:#D8F3DC;font-family:'Segoe UI',Arial,sans-serif;overflow:hidden}
#wrap{position:relative;display:flex;flex-direction:column;align-items:center}
#bar{font-size:13px;padding:6px 10px;text-align:center;line-height:1.3}
#stage{position:relative;width:100%;max-width:min(1000px,calc((100vh - 52px) * 1.7143))}
canvas{display:block;width:100%;height:auto;background:#cfeedd;border-radius:10px;outline:none}
#quiz{display:none;position:absolute;left:5%;right:5%;top:8%;background:#F8FAF9;color:#1E293B;border:4px solid #2D6A4F;border-radius:18px;padding:16px 22px;box-shadow:0 10px 40px rgba(0,0,0,.45);font-size:clamp(13px,2.1vw,19px)}
#quiz h3{margin:0 0 4px;color:#1B4332;font-size:1.05em}
#qtext{font-weight:700;margin:8px 0 10px}
#timer{height:8px;background:#D8F3DC;border-radius:6px;overflow:hidden}
#timer i{display:block;height:100%;width:100%;background:#2D6A4F}
.opt{display:block;width:100%;text-align:left;margin:6px 0;padding:9px 12px;border:2px solid #2D6A4F;border-radius:10px;background:#fff;color:#1E293B;font:inherit;cursor:pointer}
.opt:hover:not(:disabled){background:#D8F3DC}.opt:focus-visible{outline:3px solid #1B4332}
.opt.bad{background:#fde8d8;border-color:#d97706;opacity:.7}.opt.good{background:#b7f5c8;border-color:#1B4332}
#msg{min-height:2.6em;margin-top:6px;font-size:.95em}
#next{display:none;margin-top:6px;padding:8px 18px;border:0;border-radius:10px;background:#2D6A4F;color:#fff;font:inherit;font-weight:700;cursor:pointer}
</style></head><body><div id="wrap">
<div id="bar"><b>Eco-School Quiz Quest</b> &middot; Move: WASD or Arrow keys &middot; Collect all 7 Eco-Notebooks &middot; Answer with the mouse or keys 1-4 &middot; Click the game first &middot; No scary stuff, just learning!</div>
<div id="stage"><canvas id="game" width="960" height="560" tabindex="0"></canvas>
<div id="quiz"><h3 id="qhead"></h3><div id="timer"><i></i></div><div id="qtext"></div><div id="opts"></div><div id="msg"></div><button id="next">Continue</button></div></div></div>
<script>
(function(){
"use strict";
const CFG=__CONFIG__;
const W=960,H=560,TS=40,COLS=24,ROWS=13,TOP=40,SPEED=170,QTIME=CFG.seconds;
const cv=document.getElementById('game'),ctx=cv.getContext('2d');
const quizEl=document.getElementById('quiz'),qhead=document.getElementById('qhead'),qtext=document.getElementById('qtext'),optsEl=document.getElementById('opts'),msgEl=document.getElementById('msg'),nextBtn=document.getElementById('next'),timerBar=document.querySelector('#timer i');
const keys={};let state='menu',score=0,tAnim=0,toast=null,tipT=0,tipI=0;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
function wrap(text,maxW,font){ctx.font=font;const out=[];let line='';for(const w of text.split(' ')){const t=line?line+' '+w:w;if(ctx.measureText(t).width>maxW&&line){out.push(line);line=w;}else line=t;}if(line)out.push(line);return out;}
function centerText(text,y,font,color,maxW){const ls=wrap(text,maxW||760,font);ctx.font=font;ctx.fillStyle=color;ctx.textAlign='center';ls.forEach((l,i)=>ctx.fillText(l,W/2,y+i*parseInt(font,10)*1.35));ctx.textAlign='left';return ls.length;}

/* ---------- map: hallway in the middle, three classrooms above and below ---------- */
const DOORS=[3,4,11,12,19,20];
const DESKS=[[2,2],[3,2],[5,3],[6,3],[9,2],[10,2],[12,2],[13,2],[17,3],[18,3],[21,2],[22,2],[2,10],[3,10],[9,10],[10,10],[13,10],[17,10],[18,10],[21,10]];
const NB_POS=[[6,1],[14,1],[22,4],[1,11],[14,11],[22,11],[13,7]];
function baseWall(c,r){
  if(r===0||r===ROWS-1||c===0||c===COLS-1)return true;
  if(r===5||r===8)return !DOORS.includes(c);
  if((r<5||r>8)&&(c===7||c===15))return true;
  return false;
}
let desks,notebooks,P,guide;
function reset(){
  desks=new Set(DESKS.map(d=>d[0]+','+d[1]));
  notebooks=NB_POS.map(p=>({c:p[0],r:p[1],got:false}));
  P={x:2*TS,y:6*TS+4,w:24,h:24,face:1,moving:false};
  guide={x:12*TS,y:6*TS+20,dir:1};
  score=0;toast={t:4,text:'Find all 7 Eco-Notebooks!'};
}
const exitOpen=()=>notebooks.every(n=>n.got);
function solid(c,r){
  if(c<0||r<0||c>=COLS||r>=ROWS)return true;
  if(c===COLS-1&&(r===6||r===7))return !exitOpen();
  return baseWall(c,r)||desks.has(c+','+r);
}
function blocked(x,y){return [[x,y],[x+P.w,y],[x,y+P.h],[x+P.w,y+P.h]].some(p=>solid(Math.floor(p[0]/TS),Math.floor(p[1]/TS)));}

/* ---------- input ---------- */
window.addEventListener('keydown',e=>{
  if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();
  keys[e.code]=true;
  if(state==='quiz'&&e.code.startsWith('Digit'))answer(parseInt(e.code.slice(5),10)-1);
  else if(state==='quiz'&&e.code==='Enter'&&nextBtn.style.display==='block')nextBtn.click();
  else if(e.code==='Enter')advance();
});
window.addEventListener('keyup',e=>{keys[e.code]=false;});
window.addEventListener('blur',()=>{for(const k in keys)keys[k]=false;});
cv.addEventListener('pointerdown',()=>{cv.focus();if(state==='menu'||state==='win')advance();});
function advance(){if(state==='menu'||state==='win'){reset();state='play';}}

/* ---------- quiz tablet ---------- */
let qi=0,qn=0,tries=0,tleft=0,locked=false,cur=null;
function openQuiz(n){state='quiz';qi=n;qn=0;showQuestion();quizEl.style.display='block';}
function showQuestion(){
  cur=CFG.quiz[qi][qn];tries=0;locked=false;tleft=QTIME;
  qhead.textContent='Eco-Notebook '+(qi+1)+' of '+CFG.notebooks+' \u00b7 Question '+(qn+1)+' of 3';
  qtext.textContent=cur.q;msgEl.textContent='You have '+QTIME+' seconds. Wrong answers just give you a hint!';msgEl.style.color='#1E293B';
  nextBtn.style.display='none';optsEl.innerHTML='';
  cur.o.forEach((t,i)=>{const b=document.createElement('button');b.className='opt';b.textContent=(i+1)+'. '+t;b.addEventListener('click',()=>answer(i));optsEl.appendChild(b);});
}
function answer(i){
  if(state!=='quiz'||locked||i<0||i>=cur.o.length)return;
  const btns=optsEl.children;if(btns[i].disabled)return;
  if(i===cur.a){
    const pts=[100,50,25,10][Math.min(tries,3)];score+=pts;locked=true;btns[i].classList.add('good');
    msgEl.style.color='#1B4332';msgEl.textContent='Correct! +'+pts+' points. '+cur.e;finishQuestion();
  }else{
    tries++;btns[i].classList.add('bad');btns[i].disabled=true;
    msgEl.style.color='#92400e';msgEl.textContent='Not quite, and that is okay! Hint: '+cur.hint+' Try another answer.';
  }
}
function timeout(){
  locked=true;msgEl.style.color='#92400e';
  Array.from(optsEl.children).forEach((b,i)=>{b.disabled=true;if(i===cur.a)b.classList.add('good');});
  msgEl.textContent="Time's up, no worries! The answer is: "+cur.o[cur.a]+'. '+cur.e;finishQuestion();
}
function finishQuestion(){nextBtn.textContent=(qn<2)?'Next question':'Close tablet';nextBtn.style.display='block';nextBtn.focus&&nextBtn.focus();}
nextBtn.addEventListener('click',()=>{
  if(qn<2){qn++;showQuestion();return;}
  quizEl.style.display='none';state='play';cv.focus();
  toast={t:3,text:exitOpen()?'All notebooks found! The exit door is open, head right along the hallway.':(notebooks.filter(n=>n.got).length+' of '+CFG.notebooks+' notebooks found.')};
});

/* ---------- update ---------- */
function update(dt){
  tAnim+=dt;if(toast){toast.t-=dt;if(toast.t<=0)toast=null;}
  if(state==='quiz'&&!locked){tleft-=dt;timerBar.style.width=Math.max(0,tleft/QTIME*100)+'%';if(tleft<=0)timeout();}
  if(state!=='play')return;
  guide.x+=guide.dir*45*dt;if(guide.x>20*TS){guide.dir=-1;}if(guide.x<3*TS){guide.dir=1;}
  const dx=((keys.KeyD||keys.ArrowRight)?1:0)-((keys.KeyA||keys.ArrowLeft)?1:0),dy=((keys.KeyS||keys.ArrowDown)?1:0)-((keys.KeyW||keys.ArrowUp)?1:0);
  P.moving=!!(dx||dy);if(dx)P.face=dx;
  if(P.moving){const n=Math.hypot(dx,dy),vx=dx/n*SPEED*dt,vy=dy/n*SPEED*dt;if(!blocked(P.x+vx,P.y))P.x+=vx;if(!blocked(P.x,P.y+vy))P.y+=vy;}
  const pcx=P.x+P.w/2,pcy=P.y+P.h/2;
  for(let i=0;i<notebooks.length;i++){const n=notebooks[i];if(!n.got&&Math.hypot(n.c*TS+TS/2-pcx,n.r*TS+TS/2-pcy)<28){n.got=true;openQuiz(i);return;}}
  if(Math.hypot(guide.x-pcx,guide.y-pcy)<70){tipT+=dt;}else if(tipT>0){tipT=0;tipI=(tipI+1)%CFG.tips.length;}
  if(pcx>(COLS-1)*TS-4&&pcy>6*TS&&pcy<8*TS){state='win';}
  else if(!exitOpen()&&pcx>(COLS-1)*TS-40&&pcy>6*TS&&pcy<8*TS&&!toast)toast={t:2.5,text:'The exit opens after you collect all 7 notebooks.'};
}

/* ---------- drawing ---------- */
function drawTiles(){
  for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++){
    const x=c*TS,y=TOP+r*TS,hall=r>=6&&r<=7;
    if(baseWall(c,r)){ctx.fillStyle='#1B4332';ctx.fillRect(x,y,TS,TS);ctx.fillStyle='#2D6A4F';ctx.fillRect(x,y,TS,6);}
    else{ctx.fillStyle=hall?((c+r)%2?'#e6efe9':'#d9e6dd'):((c+r)%2?'#e8d3a9':'#dfc796');ctx.fillRect(x,y,TS,TS);}
  }
  for(let r=1;r<5;r+=3){}
  [[2,0,'SDG 4','#c5192d'],[10,0,'SDG 13','#3f7e44'],[18,0,'SDG 4','#c5192d'],[2,12,'SDG 13','#3f7e44'],[11,12,'SDG 4','#c5192d'],[19,12,'SDG 13','#3f7e44']].forEach(p=>{
    ctx.fillStyle=p[3];rr(p[0]*TS-4,TOP+p[1]*TS+8,TS+14,TS-16,4);ctx.fill();ctx.fillStyle='#fff';ctx.font='bold 12px Segoe UI,Arial';ctx.textAlign='center';ctx.fillText(p[2],p[0]*TS+TS/2+3,TOP+p[1]*TS+TS/2+4);ctx.textAlign='left';});
  desks.forEach(k=>{const [c,r]=k.split(',').map(Number),x=c*TS,y=TOP+r*TS;ctx.fillStyle='#8a5c34';rr(x+3,y+6,TS-6,TS-14,4);ctx.fill();ctx.fillStyle='#a9763a';ctx.fillRect(x+5,y+8,TS-10,6);ctx.fillStyle='#6b4a28';ctx.fillRect(x+10,y+TS-10,6,6);ctx.fillRect(x+TS-16,y+TS-10,6,6);});
  const open=exitOpen(),ex=(COLS-1)*TS;
  ctx.fillStyle=open?'#74c69d':'#b45353';ctx.fillRect(ex,TOP+6*TS,TS,2*TS);ctx.fillStyle='#fff';ctx.font='bold 13px Segoe UI,Arial';ctx.textAlign='center';ctx.fillText(open?'EXIT':'LOCKED',ex+TS/2,TOP+7*TS+4);ctx.textAlign='left';
}
function drawNotebook(n){
  const x=n.c*TS+TS/2,y=TOP+n.r*TS+TS/2+Math.sin(tAnim*3+n.c)*3;
  ctx.fillStyle='rgba(255,247,168,.65)';ctx.beginPath();ctx.arc(x,y,22,0,7);ctx.fill();
  ctx.fillStyle='#2D6A4F';rr(x-11,y-14,22,28,3);ctx.fill();ctx.fillStyle='#D8F3DC';ctx.fillRect(x-8,y-11,3,22);
  ctx.fillStyle='#74c69d';ctx.beginPath();ctx.ellipse(x+2,y,6,3.5,-0.6,0,7);ctx.fill();
}
function drawPerson(x,y,body,hat,face){
  ctx.fillStyle='rgba(0,0,0,.2)';ctx.beginPath();ctx.ellipse(x,y+12,11,5,0,0,7);ctx.fill();
  ctx.fillStyle=body;rr(x-9,y-4,18,16,6);ctx.fill();
  ctx.fillStyle='#f0c9a0';ctx.beginPath();ctx.arc(x,y-8,9,0,7);ctx.fill();
  ctx.fillStyle=hat;ctx.beginPath();ctx.arc(x,y-11,9,Math.PI,0);ctx.fill();
  ctx.fillStyle='#222';ctx.fillRect(x+face*3-1,y-9,2,3);ctx.fillRect(x+face*3-6,y-9,2,3);
  ctx.strokeStyle='#222';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(x+face*1,y-5,3,0.2,Math.PI-0.2);ctx.stroke();
}
function hud(){
  ctx.fillStyle='#0f2a1d';ctx.fillRect(0,0,W,TOP);ctx.font='bold 17px Segoe UI,Arial';ctx.fillStyle='#D8F3DC';
  ctx.fillText('Eco-Notebooks '+notebooks.filter(n=>n.got).length+' / '+CFG.notebooks,16,27);ctx.fillText('Points '+score,260,27);
  ctx.fillStyle=exitOpen()?'#74c69d':'#fca5a5';ctx.fillText('Exit door: '+(exitOpen()?'open':'locked'),420,27);
}
function panel(title,lines,hint){
  ctx.fillStyle='rgba(15,42,29,.9)';rr(120,110,720,340,18);ctx.fill();
  ctx.font='bold 34px Segoe UI,Arial';ctx.fillStyle='#D8F3DC';ctx.textAlign='center';ctx.fillText(title,W/2,168);ctx.textAlign='left';
  let y=214;lines.forEach(t=>{y+=centerText(t,y,'19px Segoe UI,Arial','#F8FAF9',640)*26+8;});
  ctx.font='bold 17px Segoe UI,Arial';ctx.fillStyle='#74c69d';ctx.textAlign='center';ctx.fillText(hint,W/2,430);ctx.textAlign='left';
}
function draw(){
  ctx.clearRect(0,0,W,H);
  if(!P){ctx.fillStyle='#1B4332';ctx.fillRect(0,0,W,H);panel('Eco-School Quiz Quest',['Explore the Kipling Institute classrooms and collect 7 Eco-Notebooks.','Each notebook opens a 3-question quiz with 20 seconds per question. Wrong answers give a friendly hint, never a penalty. Collect them all to open the exit!'],'Press Enter or click to start');return;}
  drawTiles();notebooks.forEach(n=>{if(!n.got)drawNotebook(n);});
  drawPerson(guide.x,TOP+guide.y,'#e0a526','#1B4332',guide.dir);
  ctx.fillStyle='#74c69d';ctx.beginPath();ctx.ellipse(guide.x+4,TOP+guide.y-24,6,3,-0.5,0,7);ctx.fill();
  if(tipT>0){const t=CFG.tips[tipI],ls=wrap('Prof. Leaf: '+t,300,'bold 14px Segoe UI,Arial'),bx=clamp(guide.x-150,10,W-320),by=TOP+guide.y-60-ls.length*18;
    ctx.fillStyle='#fff';rr(bx,by,310,ls.length*18+14,10);ctx.fill();ctx.strokeStyle='#2D6A4F';ctx.lineWidth=2;ctx.stroke();ctx.fillStyle='#1E293B';ctx.font='bold 14px Segoe UI,Arial';ls.forEach((l,i)=>ctx.fillText(l,bx+8,by+20+i*18));}
  drawPerson(P.x+P.w/2,TOP+P.y+P.h/2-2,'#3b82c4','#1B4332',P.face);
  hud();
  if(toast){ctx.fillStyle='rgba(15,42,29,.85)';rr(180,TOP+8,600,38,10);ctx.fill();centerText(toast.text,TOP+33,'bold 16px Segoe UI,Arial','#D8F3DC',560);}
  if(state==='win')panel('You did it, Eco-Friend!',['You collected all '+CFG.notebooks+' Eco-Notebooks and escaped through the exit with '+score+' points.','Quality education (SDG 4) helps us take climate action (SDG 13). Now try one of the Green Challenges!'],'Press Enter or click to play again');
}
let last=performance.now();
function frame(now){const dt=Math.min(0.033,(now-last)/1000);last=now;update(dt);draw();requestAnimationFrame(frame);}
requestAnimationFrame(frame);
window.__quest={get state(){return state;},keys:keys,advance:advance,get P(){return P;},get notebooks(){return notebooks;},update:update,draw:draw,answer:answer,timeout:timeout,get score(){return score;},next:()=>nextBtn.click(),get exitOpen(){return exitOpen();},solid:solid,blocked:blocked,TS:TS,TOP:TOP};
})();
</script></body></html>
"""


def get_eco_school_quest_html() -> str:
    """Return the complete Eco-School Quiz Quest HTML page."""
    config = {"quiz": QUIZ, "tips": GUIDE_TIPS, "notebooks": NOTEBOOKS, "seconds": SECONDS_PER_QUESTION}
    return _TEMPLATE.replace("__CONFIG__", json.dumps(config))
