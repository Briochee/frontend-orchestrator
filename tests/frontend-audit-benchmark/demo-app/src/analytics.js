import { money } from './data.js';
import { toast } from './components.js';
const slider = document.getElementById('order-cutoff');
const output = document.getElementById('cutoff-label');
function update() { output.textContent = money(Number(slider.value)); document.getElementById('qualified-orders').textContent = Number(slider.value) > 40000 ? '11' : '286' }
slider?.addEventListener('input', update); if (slider) update();
document.querySelector('#download-analytics')?.addEventListener('click', () => toast('Report exported (demo only).'));
