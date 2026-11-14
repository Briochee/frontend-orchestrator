import {customers} from './data.js';
import {toast} from './components.js';
const search=document.getElementById('customer-search');
const cards=[...document.querySelectorAll('.customer-card')];
search?.addEventListener('input',()=>{
 const q=search.value.trim().toLowerCase();
 cards.forEach(card=>card.hidden=!card.dataset.customer.toLowerCase().includes(q));
});
document.querySelector('#invite-customer')?.addEventListener('click',()=>toast('Customer invitation requires a connected account.'));
