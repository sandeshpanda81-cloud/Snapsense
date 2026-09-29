const pages = document.querySelectorAll(".page");
const navs = document.querySelectorAll(".nav");
const title = document.getElementById("pageTitle");
const titles = {home:"On-device intelligence, made useful.",chat:"Talk to your local AI.",documents:"Turn documents into decisions.",ocr:"Extract text from your screen.",voice:"Speak. Capture. Organize."};

function showPage(id){
  pages.forEach(p=>p.classList.toggle("active-page",p.id===id));
  navs.forEach(n=>n.classList.toggle("active",n.dataset.page===id));
  title.textContent = titles[id] || titles.home;
}
navs.forEach(n=>n.onclick=()=>showPage(n.dataset.page));
document.querySelectorAll("[data-page-jump]").forEach(b=>b.onclick=()=>showPage(b.dataset.pageJump));

async function checkHealth(){
  try{
    const r=await fetch("/api/health"); const d=await r.json();
    document.getElementById("statusText").textContent = d.local_ai ? `Local AI • ${d.model}` : "App online • local fallback";
  }catch(e){document.getElementById("statusText").textContent="App offline";}
}
checkHealth();

function setResult(el, html){el.classList.remove("hidden");el.innerHTML=html}

document.getElementById("sendChat").onclick=async()=>{
  const input=document.getElementById("chatInput"), box=document.getElementById("chatMessages");
  const msg=input.value.trim(); if(!msg)return;
  box.innerHTML += `<div class="msg user"><b>You</b><p>${escapeHtml(msg)}</p></div>`;
  input.value="";
  box.innerHTML += `<div class="msg bot" id="typing"><b>SnapSense</b><p>Thinking locally...</p></div>`;
  box.scrollTop=box.scrollHeight;
  try{
    const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg})});
    const d=await r.json(); document.getElementById("typing").remove();
    box.innerHTML += `<div class="msg bot"><b>SnapSense • ${escapeHtml(d.mode||"AI")}</b><p>${escapeHtml(d.answer||d.error)}</p></div>`;
  }catch(e){document.getElementById("typing").innerHTML="<b>SnapSense</b><p>Request failed. Is Flask running?</p>";}
  box.scrollTop=box.scrollHeight;
};

document.getElementById("summarizeBtn").onclick=async()=>{
  const f=document.getElementById("docFile").files[0], out=document.getElementById("docResult");
  if(!f){setResult(out,"<h3>Select a document first.</h3>");return}
  setResult(out,"<h3>Analyzing locally...</h3>");
  const fd=new FormData();fd.append("file",f);
  try{
    const d=await (await fetch("/api/summarize",{method:"POST",body:fd})).json();
    if(d.error){setResult(out,`<h3>Error</h3>${escapeHtml(d.error)}`);return}
    setResult(out,`<h3>${escapeHtml(d.filename)} • ${escapeHtml(d.mode)}</h3><p>${escapeHtml(d.summary)}</p><h3>Keywords</h3>${d.keywords.map(k=>`<span class="keyword">${escapeHtml(k)}</span>`).join("")}`);
  }catch(e){setResult(out,"<h3>Something went wrong.</h3>")}
};

document.getElementById("ocrBtn").onclick=async()=>{
  const f=document.getElementById("ocrFile").files[0], out=document.getElementById("ocrResult");
  if(!f){setResult(out,"<h3>Select an image first.</h3>");return}
  setResult(out,"<h3>Running local OCR...</h3>");
  const fd=new FormData();fd.append("file",f);
  try{
    const d=await (await fetch("/api/ocr",{method:"POST",body:fd})).json();
    setResult(out,`<h3>${escapeHtml(d.mode||"OCR")}</h3><p>${escapeHtml(d.text||d.error||"No result")}</p>`);
  }catch(e){setResult(out,"<h3>OCR failed.</h3>")}
};

let recognition=null, finalTranscript="";
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
const mic=document.getElementById("micBtn"), voiceState=document.getElementById("voiceState"), transcript=document.getElementById("transcript");
if(SpeechRecognition){
  recognition=new SpeechRecognition(); recognition.continuous=true; recognition.interimResults=true; recognition.lang="en-IN";
  recognition.onstart=()=>{mic.classList.add("recording");voiceState.textContent="Listening...";};
  recognition.onend=()=>{mic.classList.remove("recording");voiceState.textContent="Recording stopped";};
  recognition.onresult=e=>{let t="";for(let i=e.resultIndex;i<e.results.length;i++)t+=e.results[i][0].transcript;finalTranscript=t;transcript.textContent=t||"Listening...";};
}else{mic.disabled=true;voiceState.textContent="Speech recognition is not supported in this browser. Try Chrome or Edge."}
mic.onclick=()=>{if(!recognition)return;try{recognition.start()}catch(e){recognition.stop()}};
document.getElementById("processVoice").onclick=async()=>{
  const out=document.getElementById("voiceResult");
  if(!finalTranscript.trim()){setResult(out,"<h3>No transcript yet.</h3>");return}
  setResult(out,"<h3>Processing locally...</h3>");
  try{
    const d=await (await fetch("/api/voice",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({transcript:finalTranscript})})).json();
    setResult(out,`<h3>${escapeHtml(d.mode||"AI")}</h3><p>${escapeHtml(d.answer||d.error)}</p>`);
  }catch(e){setResult(out,"<h3>Request failed.</h3>")}
};

function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
