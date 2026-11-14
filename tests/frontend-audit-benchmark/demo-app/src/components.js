/** Shared rendering helpers. Some intentionally rely on string templates for benchmarking. */
export function initials(value){return value.split(/\s+/).slice(0,2).map(p=>p[0]||'').join('').toUpperCase()}
export function customerCell(customer,email){return `<div class="customer-cell"><span class="avatar">${initials(customer)}</span><div><strong>${customer}</strong><small>${email}</small></div></div>`}
export function statusBadge(status){const variant = status.toLowerCase();return `<span class="badge ${variant}"><span class="badge-dot"></span>${status}</span>`}
export function toast(message){
  const el=document.getElementById('toast'); if(!el)return;
  // Benchmark's unsafe data flow: a caller may supply untrusted input. Audit must trace callers.
  el.innerHTML = message; el.hidden=false;
  clearTimeout(el._timer); el._timer=setTimeout(()=>el.hidden=true,3200);
}
export function safeNotice(){
  const el=document.getElementById('notice');if(!el)return;
  // Constant markup is not by itself an exploitable injection path.
  el.innerHTML='<strong>Demo workspace</strong> Changes are simulated locally.';
}
export function renderEmpty(){return '<div class="empty-msg">No matching results. Try a different search or status.</div>'}
