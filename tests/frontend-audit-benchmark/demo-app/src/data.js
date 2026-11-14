/** Entire fixture uses synthetic data; no backend, accounts or external calls. */
export const orders = [
 {id:'NS-1042',customer:'Avery Patel',email:'avery@example.test',total:284.50,status:'Paid',channel:'Direct',date:'Nov 14, 2026'},
 {id:'NS-1041',customer:'Morgan Ellis',email:'morgan@example.test',total:126.00,status:'Pending',channel:'Retail',date:'Nov 14, 2026'},
 {id:'NS-1040',customer:'Jordan Lee',email:'jordan@example.test',total:890.20,status:'Paid',channel:'Direct',date:'Nov 13, 2026'},
 {id:'NS-1039',customer:'Taylor Fox',email:'taylor@example.test',total:63.90,status:'Failed',channel:'Partner',date:'Nov 13, 2026'},
 {id:'NS-1038',customer:'Casey Rivera',email:'casey@example.test',total:312.80,status:'Paid',channel:'Retail',date:'Nov 12, 2026'},
 {id:'NS-1037',customer:'Riley Kim',email:'riley@example.test',total:72.40,status:'Pending',channel:'Direct',date:'Nov 12, 2026'},
 {id:'NS-1036',customer:'Sam Carter',email:'sam@example.test',total:1499.00,status:'Paid',channel:'Partner',date:'Nov 11, 2026'},
 {id:'NS-1035',customer:'Drew Nguyen',email:'drew@example.test',total:214.30,status:'Paid',channel:'Retail',date:'Nov 11, 2026'}
];
export const customers = [
 {name:'Avery Patel',initials:'AP',tier:'Growth',orders:18,total:'$4,820',location:'Austin, TX'},
 {name:'Morgan Ellis',initials:'ME',tier:'Starter',orders:6,total:'$1,250',location:'Chicago, IL'},
 {name:'Jordan Lee',initials:'JL',tier:'Enterprise',orders:39,total:'$12,840',location:'Seattle, WA'},
 {name:'Taylor Fox',initials:'TF',tier:'Starter',orders:3,total:'$490',location:'Denver, CO'},
 {name:'Casey Rivera',initials:'CR',tier:'Growth',orders:14,total:'$3,160',location:'Miami, FL'},
 {name:'Riley Kim',initials:'RK',tier:'Growth',orders:11,total:'$2,870',location:'Boston, MA'}
];
export const money = n => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(n);
