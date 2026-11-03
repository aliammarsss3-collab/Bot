(()=>{
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,fine=matchMedia('(hover:hover)').matches;
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money=v=>new Intl.NumberFormat('en-US').format(v);

// شريط التقدم + الهيدر + زر الأعلى (تُضاف في آخر body حتى لا تتأثر نصوص لوحة الإدارة)
const bar=document.body.appendChild(Object.assign(document.createElement('div'),{className:'scroll-progress'}));
const top=document.body.appendChild(Object.assign(document.createElement('button'),{className:'to-top',type:'button'}));
top.setAttribute('aria-label','العودة للأعلى');top.onclick=()=>scrollTo({top:0,behavior:'smooth'});
const header=$('.header'),links=$$('#main-nav a'),secs=links.map(a=>$(a.getAttribute('href')));
let tick=false;
function onScroll(){tick=false;const y=scrollY,max=document.documentElement.scrollHeight-innerHeight;
 bar.style.setProperty('--p',max>0?y/max:0);header.classList.toggle('scrolled',y>40);top.classList.toggle('show',y>700);
 let cur=-1;secs.forEach((s,i)=>{if(s&&s.getBoundingClientRect().top<innerHeight*.4)cur=i});links.forEach((a,i)=>a.classList.toggle('active',i===cur))}
addEventListener('scroll',()=>{if(!tick){tick=true;requestAnimationFrame(onScroll)}},{passive:true});onScroll();

if(!reduce&&fine){
 // حركة المنظور في الهيرو
 const hero=$('.hero'),fig=$('.hero-scene .figure'),halo=$('.hero-scene .halo');
 hero?.addEventListener('pointermove',e=>{const r=hero.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
  if(fig)fig.style.translate=`${x*-22}px ${y*-14}px`;if(halo)halo.style.translate=`${x*28}px ${y*18}px`});
 hero?.addEventListener('pointerleave',()=>{fig&&(fig.style.translate='');halo&&(halo.style.translate='')});
 // ميلان البطاقات
 $$('.product-card,.plan-card,.tv-grid article').forEach(c=>{c.classList.add('tilt');
  c.addEventListener('pointermove',e=>{const r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
   c.style.transform=`perspective(800px) rotateY(${x*7}deg) rotateX(${y*-7}deg) translateY(-4px)`});
  c.addEventListener('pointerleave',()=>c.style.transform='')});
 // ظهور متتابع للبطاقات
 if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting){en.target.classList.add('revealed');io.unobserve(en.target);setTimeout(()=>{en.target.removeAttribute('data-reveal');en.target.classList.add('reveal-done')},1400)}}),{threshold:.1});
  $$('.product-card,.category,.tv-grid article,.review-grid article,.steps>div').forEach((el,i)=>{el.dataset.reveal='';el.style.transitionDelay=(i%4)*90+'ms';io.observe(el)})}
}
// تأثير الموجة على الأزرار
document.addEventListener('pointerdown',e=>{const b=e.target.closest('.button,.add-cart');if(!b||reduce)return;const r=b.getBoundingClientRect(),d=Math.max(r.width,r.height);
 const s=Object.assign(document.createElement('span'),{className:'ripple'});s.style.cssText=`width:${d}px;height:${d}px;left:${e.clientX-r.left-d/2}px;top:${e.clientY-r.top-d/2}px`;b.append(s);setTimeout(()=>s.remove(),600)});

// السلة: حفظ دائم + أزرار الكمية + آمنة من حقن HTML
const KEY='moon-store-cart-v1';
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(cart))}catch{}};
renderCart=function(){
 const count=cart.reduce((n,i)=>n+i.qty,0);
 $$('.cart-count').forEach(el=>el.textContent=count);
 $('#cart-total').textContent=money(cart.reduce((s,i)=>s+i.price*i.qty,0))+' د.ع';
 save();
 if(!count){cartItems.innerHTML='<div class="empty-cart"><span>♧</span><p>سلتك فاضية حالياً</p><small>يبدو أنك ما أضفت أي منتجات بعد.</small><button class="button primary drawer-close">تسوّق الآن</button></div>';return}
 cartItems.innerHTML=cart.map((it,i)=>`<div class="cart-row"><div><b>${esc(it.name)}</b><small>${money(it.price)} د.ع للواحد</small><div class="qty"><button data-q="${i}" data-d="-1" aria-label="تقليل">−</button><b>${it.qty}</b><button data-q="${i}" data-d="1" aria-label="زيادة">+</button></div></div><button class="remove-item" data-remove="${i}" aria-label="حذف ${esc(it.name)}">حذف</button></div>`).join('');
};
try{const s=JSON.parse(localStorage.getItem(KEY)||'[]');if(Array.isArray(s))s.forEach(i=>i&&i.name&&Number(i.price)>0&&cart.push({name:String(i.name),price:Number(i.price),qty:Math.max(1,Number(i.qty)||1)}))}catch{}
renderCart();
document.addEventListener('click',e=>{
 const q=e.target.closest('[data-q]');
 if(q){const it=cart[+q.dataset.q];if(it){it.qty+=+q.dataset.d;if(it.qty<1)cart.splice(+q.dataset.q,1);renderCart()}return}
 if(e.target.closest('.add-cart,.add-plan')){const b=$('.cart-open');b.classList.remove('bump');void b.offsetWidth;b.classList.add('bump')}
},true);
// إتمام الطلب عبر واتساب (إذا أُضيف الرقم من لوحة الإدارة)
document.addEventListener('click',e=>{
 if(!e.target.closest('.checkout')||!cart.length)return;
 const phone=(settings.whatsapp||'').replace(/\D/g,'');if(!/^\d{8,15}$/.test(phone))return;
 e.stopImmediatePropagation();
 const total=cart.reduce((s,i)=>s+i.price*i.qty,0);
 const msg=`مرحباً، أريد إتمام طلبي:\n${cart.map(i=>`• ${i.name} × ${i.qty} = ${money(i.price*i.qty)} د.ع`).join('\n')}\nالمجموع: ${money(total)} د.ع`;
 open(`https://wa.me/${phone}?text=${encodeURIComponent(msg)}`,'_blank','noopener,noreferrer');
},true);
})();

// فلاتر المنتجات: تُضاف في آخر عنوان القسم حتى لا تتغير مواقع نصوص لوحة الإدارة
(()=>{
 const head=document.querySelector('.products-section .section-head > div'),cards=[...document.querySelectorAll('.product-card')];
 if(!head||!cards.length)return;
 const sets=[['الكل',''],['سناب شات','سناب'],['ذكاء اصطناعي','ذكاء']];
 const wrap=document.createElement('div');wrap.className='filter-chips';wrap.setAttribute('role','group');wrap.setAttribute('aria-label','تصفية المنتجات');
 sets.forEach(([label,key],i)=>{const b=document.createElement('button');b.type='button';b.textContent=label;b.className=i?'':'on';
  b.onclick=()=>{[...wrap.children].forEach(x=>x.classList.toggle('on',x===b));
   cards.forEach(c=>{const show=!key||(c.dataset.search||'').includes(key);
    if(show){c.hidden=false;requestAnimationFrame(()=>c.classList.remove('out'))}
    else{c.classList.add('out');setTimeout(()=>{if(c.classList.contains('out'))c.hidden=true},250)}})};
  wrap.append(b)});
 head.append(wrap);
})();
