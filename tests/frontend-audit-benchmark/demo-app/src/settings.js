import {toast,safeNotice} from './components.js';
safeNotice();
const toggles=[...document.querySelectorAll('[role=switch]')];
toggles.forEach(toggle=>toggle.addEventListener('click',()=>{
 let on=toggle.getAttribute('aria-checked')==='true';toggle.setAttribute('aria-checked',String(!on));
 if(toggle.id==='theme-switch'){
  // Intentional false affordance: state changes but no actual theme is applied.
  toast('Appearance preference updated.');
 }
}));
document.getElementById('settings-form')?.addEventListener('submit',event=>{
 event.preventDefault();
 const team=document.getElementById('team-name').value;
 const threshold=Number(document.getElementById('alert-threshold').value);
 // Intentional optimistic acknowledgement without rollback after deterministic simulated failure.
 document.getElementById('save-status').textContent='Saved successfully';
 // Unsafe propagation of user-controlled team input into HTML toast.
 toast(`Saved preferences for <strong>${team}</strong>`);
 setTimeout(()=>{
  if(threshold>80000){document.getElementById('save-status').textContent='Sync failed; your changes were not stored';}
 },450);
});
