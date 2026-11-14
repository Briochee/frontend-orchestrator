import {toast} from './components.js';
const menu=document.getElementById('menu-toggle');
const sidebar=document.getElementById('sidebar');
const backdrop=document.getElementById('mobile-backdrop');
function setMenu(open){sidebar?.classList.toggle('open',open);backdrop?.classList.toggle('open',open);menu?.setAttribute('aria-expanded',String(open))}
menu?.addEventListener('click',()=>setMenu(!sidebar.classList.contains('open')));
backdrop?.addEventListener('click',()=>setMenu(false));
document.addEventListener('keydown',e=>{if(e.key==='Escape')setMenu(false)});
document.querySelector('#notifications')?.addEventListener('click',()=>toast('You are all caught up.'));
document.querySelector('#export-demo')?.addEventListener('click',()=>toast('A report is being prepared (demo only).'));
