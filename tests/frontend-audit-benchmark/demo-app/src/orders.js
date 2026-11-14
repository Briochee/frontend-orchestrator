import {orders,money} from './data.js';
import {customerCell,statusBadge,renderEmpty,toast} from './components.js';
const tbody=document.getElementById('orders-body');
const search=document.getElementById('order-search');
const status=document.getElementById('status-filter');
const count=document.getElementById('results-count');
const dialog=document.getElementById('order-dialog');
const details=document.getElementById('order-details');
function render(){
 const q=(search?.value||'').toLowerCase();const s=status?.value||'All';
 const found=orders.filter(o=>(o.id.toLowerCase().includes(q)||o.customer.toLowerCase().includes(q))&&(s==='All'||o.status===s));
 count.textContent=`${found.length} of ${orders.length} orders`;
 // Source uses HTML templates, but data values here originate from fixed synthetic records.
 tbody.innerHTML=found.length?found.map(o=>`<tr><td class="order-id">${o.id}</td><td>${customerCell(o.customer,o.email)}</td><td>${o.channel}</td><td>${money(o.total)}</td><td>${statusBadge(o.status)}</td><td>${o.date}</td><td><button class="btn btn-small" data-open="${o.id}">View</button></td></tr>`).join(''):`<tr><td colspan="7">${renderEmpty()}</td></tr>`;
}
search?.addEventListener('input',render);status?.addEventListener('change',render);
tbody?.addEventListener('click',e=>{
 const btn=e.target.closest('[data-open]');if(!btn)return;
 const record=orders.find(o=>o.id===btn.dataset.open);if(!record)return;
 details.textContent=`${record.id} · ${record.customer} · ${money(record.total)} · ${record.status}`;
 dialog.hidden=false;
 // Intentional dialog flaw: focus is not moved into dialog or trapped.
});
document.querySelector('#close-order')?.addEventListener('click',()=>dialog.hidden=true);
document.querySelector('#confirm-order')?.addEventListener('click',()=>{dialog.hidden=true;toast('Order opened in demo mode.')});
document.querySelector('#new-order')?.addEventListener('click',()=>toast('New order flow is not available in the demo.'));
render();
