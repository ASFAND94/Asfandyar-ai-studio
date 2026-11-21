const $ = (id) => document.getElementById(id);
let csrfToken = sessionStorage.getItem("asfandyar_csrf") || "";

function message(id, text, error=false){const el=$(id);el.textContent=text;el.classList.toggle("error",error)}
async function api(path, options={}){
  const headers={"Content-Type":"application/json",...(options.headers||{})};
  if(options.method && !["GET","HEAD"].includes(options.method.toUpperCase()) && csrfToken) headers["X-CSRF-Token"]=csrfToken;
  const response=await fetch(path,{...options,headers,credentials:"same-origin"});
  const data=await response.json().catch(()=>({detail:"Unexpected server response"}));
  if(!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}
function showLogin(setup){
  $("auth-panel").classList.remove("hidden");$("dashboard").classList.add("hidden");
  $("setup-form").classList.toggle("hidden",!setup);$("login-form").classList.toggle("hidden",setup);
  $("auth-title").textContent=setup?"Create your private owner account":"Secure sign in";
  $("auth-note").textContent=setup?"One-time setup. Keep the setup key private.":"Only the owner can access this workspace.";
}
function showDashboard(){ $("auth-panel").classList.add("hidden");$("dashboard").classList.remove("hidden"); loadAll(); }
async function initialize(){
  try{
    const status=await api("/auth/status");
    if(status.setup_required){showLogin(true);return;}
    if(csrfToken){
      try{await api("/auth/me");showDashboard();return;}catch(_){}
    }
    showLogin(false);
  }catch(error){showLogin(false);message("auth-message","Cannot reach server: "+error.message,true);}
}
$("setup-form").addEventListener("submit",async e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget));
  try{await api("/auth/setup",{method:"POST",body:JSON.stringify(data)});e.currentTarget.reset();showLogin(false);message("auth-message","Owner account created. Sign in now.");}
  catch(error){message("auth-message",error.message,true);}
});
$("login-form").addEventListener("submit",async e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget));
  try{const result=await api("/auth/login",{method:"POST",body:JSON.stringify(data)});csrfToken=result.csrf_token;sessionStorage.setItem("asfandyar_csrf",csrfToken);e.currentTarget.reset();showDashboard();}
  catch(error){message("auth-message",error.message,true);}
});
$("logout").addEventListener("click",async()=>{
  try{await api("/auth/logout",{method:"POST",body:"{}"});}catch(_){}
  csrfToken="";sessionStorage.removeItem("asfandyar_csrf");showLogin(false);
});
async function loadAll(){await Promise.all([loadAccounts(),loadControls()]);}
async function loadControls(){
  try{const c=await api("/control/settings");$("global-publish").checked=c.global_publishing_enabled;$("global-approval").checked=c.require_approval;}
  catch(error){message("account-message",error.message,true);}
}
$("save-global").addEventListener("click",async()=>{
  try{const result=await api("/control/settings",{method:"PUT",body:JSON.stringify({global_publishing_enabled:$("global-publish").checked,require_approval:$("global-approval").checked})});message("account-message","Control settings saved. Global publishing: "+(result.settings.global_publishing_enabled?"ON":"OFF"));}
  catch(error){message("account-message",error.message,true);}
});
$("account-form").addEventListener("submit",async e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget));
  try{await api("/social/accounts",{method:"POST",body:JSON.stringify(data)});e.currentTarget.reset();message("account-message","Account slot added. Connect authorization later through official OAuth.");await loadAccounts();}
  catch(error){message("account-message",error.message,true);}
});
$("refresh").addEventListener("click",loadAccounts);
async function loadAccounts(){
  try{
    const data=await api("/social/accounts");const limits=$("limits");limits.replaceChildren();
    Object.entries(data.limits).forEach(([platform,v])=>{const span=document.createElement("span");span.className="limit";span.textContent=platform+" "+v.used+"/"+v.limit;limits.append(span);});
    const list=$("accounts");list.replaceChildren();
    if(!data.accounts.length){const p=document.createElement("p");p.className="muted";p.textContent="No accounts registered yet.";list.append(p);return;}
    for(const account of data.accounts){const pref=await api("/social/accounts/"+account.id+"/preferences");list.append(renderAccount(account,pref));}
  }catch(error){message("account-message",error.message,true);}
}
function renderAccount(account,pref){
  const wrap=document.createElement("article");wrap.className="account";
  const head=document.createElement("div");head.className="account-head";
  const title=document.createElement("div");title.className="account-name";title.textContent=account.platform.toUpperCase()+" · "+account.account_name+" ("+account.account_handle+")";
  const status=document.createElement("span");status.className="tag";status.textContent=account.status.replaceAll("_"," ");head.append(title,status);wrap.append(head);
  const fields=document.createElement("div");fields.className="account-settings";
  const nicheLabel=document.createElement("label");nicheLabel.textContent="Your chosen niche";
  const niche=document.createElement("input");niche.value=pref.niche;niche.placeholder="You decide this niche";niche.maxLength=160;nicheLabel.append(niche);
  const formatLabel=document.createElement("label");formatLabel.textContent="Content formats (comma separated)";
  const formats=document.createElement("input");formats.value=pref.content_formats.join(", ");formats.placeholder="post, video, reel";formatLabel.append(formats);
  const enabledLabel=document.createElement("label");enabledLabel.className="inline-check";
  const enabled=document.createElement("input");enabled.type="checkbox";enabled.checked=pref.publishing_enabled;enabledLabel.append(enabled,document.createTextNode("Publishing allowed for this account"));
  const approvalLabel=document.createElement("label");approvalLabel.className="inline-check";
  const approval=document.createElement("input");approval.type="checkbox";approval.checked=pref.require_approval;approvalLabel.append(approval,document.createTextNode("My approval required"));
  fields.append(nicheLabel,formatLabel,enabledLabel,approvalLabel);wrap.append(fields);
  const actions=document.createElement("div");actions.className="account-actions";
  const save=document.createElement("button");save.textContent="Save account settings";save.addEventListener("click",async()=>{
    const list=formats.value.split(",").map(x=>x.trim().toLowerCase()).filter(Boolean);
    try{await api("/social/accounts/"+account.id+"/preferences",{method:"PUT",body:JSON.stringify({niche:niche.value,content_formats:list,publishing_enabled:enabled.checked,require_approval:approval.checked})});message("account-message","Saved settings for "+account.account_name+". Your niche remains exactly as you entered it.");}
    catch(error){message("account-message",error.message,true);}
  });
  const remove=document.createElement("button");remove.className="secondary";remove.textContent="Remove";remove.addEventListener("click",async()=>{
    if(!confirm("Remove this registered account slot?"))return;
    try{await api("/social/accounts/"+account.id,{method:"DELETE",body:"{}"});await loadAccounts();}
    catch(error){message("account-message",error.message,true);}
  });
  actions.append(save,remove);wrap.append(actions);return wrap;
}
$("password-form").addEventListener("submit",async e=>{
  e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget));
  try{await api("/auth/change-password",{method:"POST",body:JSON.stringify(data)});csrfToken="";sessionStorage.removeItem("asfandyar_csrf");e.currentTarget.reset();showLogin(false);message("auth-message","Password changed. Please sign in with the new password.");}
  catch(error){message("password-message",error.message,true);}
});
initialize();
