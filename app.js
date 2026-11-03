const toast = document.querySelector('#toast');
let toastTimer;
function notify(message){toast.textContent=message;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),2600)}

const cart=[];
const cartDrawer=document.querySelector('#cart-drawer');
const overlay=document.querySelector('#overlay');
const cartItems=document.querySelector('#cart-items');
function renderCart(){
  const count=cart.reduce((n,item)=>n+item.qty,0);
  const money=value=>new Intl.NumberFormat('en-US').format(value);
  document.querySelectorAll('.cart-count').forEach(el=>el.textContent=count);
  document.querySelector('#cart-total').textContent=money(cart.reduce((sum,item)=>sum+item.price*item.qty,0))+' د.ع';
  if(!count){cartItems.innerHTML='<div class="empty-cart"><span>♧</span><p>سلتك فاضية حالياً</p><small>يبدو أنك ما أضفت أي منتجات بعد.</small><button class="button primary drawer-close">تسوّق الآن</button></div>';return}
  cartItems.innerHTML=cart.map((item,index)=>`<div class="cart-row"><div><b>${item.name}</b><small>${item.qty} × ${money(item.price)} د.ع</small></div><button class="remove-item" data-remove="${index}" aria-label="حذف ${item.name}">حذف</button></div>`).join('');
}
function openCart(){cartDrawer.classList.add('open');overlay.classList.add('show');cartDrawer.setAttribute('aria-hidden','false')}
function closePanels(){cartDrawer.classList.remove('open');overlay.classList.remove('show');cartDrawer.setAttribute('aria-hidden','true');searchModal.classList.remove('open');searchModal.setAttribute('aria-hidden','true')}
function addToCart(name,price){const item=cart.find(p=>p.name===name);if(item)item.qty++;else cart.push({name,price:Number(price),qty:1});renderCart();openCart();notify(`أضفنا «${name}» إلى السلة`)}
document.addEventListener('click',event=>{
  const add=event.target.closest('.add-cart,.add-plan');
  if(add){addToCart(add.dataset.name,add.dataset.price);return}
  if(event.target.closest('.cart-open')){openCart();return}
  if(event.target.closest('.drawer-close')){closePanels();return}
  if(event.target===overlay){closePanels();return}
  const remove=event.target.closest('[data-remove]');if(remove){cart.splice(Number(remove.dataset.remove),1);renderCart();return}
  const favorite=event.target.closest('.favorite');if(favorite){favorite.classList.toggle('on');favorite.textContent=favorite.classList.contains('on')?'♥':'♡';return}
  if(event.target.closest('.checkout')){notify(cart.length?'هذه معاينة محلية — الدفع غير مفعّل هنا':'سلتك فاضية');return}
});
renderCart();

const searchModal=document.querySelector('#search-modal');
document.querySelector('#search-open').addEventListener('click',()=>{searchModal.classList.add('open');searchModal.setAttribute('aria-hidden','false');overlay.classList.add('show');setTimeout(()=>document.querySelector('#search-input').focus(),40)});
document.querySelector('.search-close').addEventListener('click',closePanels);
const searchInput=document.querySelector('#search-input');
searchInput.addEventListener('input',()=>{const value=searchInput.value.trim().toLowerCase();const cards=[...document.querySelectorAll('.product-card')];cards.forEach(card=>card.hidden=Boolean(value&&!(`${card.dataset.search} ${card.innerText}`).toLowerCase().includes(value)));const visible=cards.filter(card=>!card.hidden).length;document.querySelector('#search-results').innerHTML=value?(visible?`وجدنا ${visible} منتج${visible===1?'اً':'ات'} — <a href="#products" class="search-jump">عرض النتائج ←</a>`:'<span class="no-results">ما لقينا نتائج. جرّب كلمة ثانية.</span>'):'جرّب: سناب، Gemini، ChatGPT';});
document.addEventListener('click',event=>{if(event.target.closest('.search-jump'))closePanels()});

const menuToggle=document.querySelector('.menu-toggle');
menuToggle.addEventListener('click',()=>{const nav=document.querySelector('#main-nav');const open=nav.classList.toggle('open');menuToggle.setAttribute('aria-expanded',String(open))});
document.querySelectorAll('#main-nav a').forEach(link=>link.addEventListener('click',()=>{document.querySelector('#main-nav').classList.remove('open');menuToggle.setAttribute('aria-expanded','false')}));

document.querySelectorAll('.plan-switch button').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.plan-switch button').forEach(b=>b.classList.toggle('active',b===button));document.querySelectorAll('.plan-card').forEach(card=>card.classList.toggle('selected',card.dataset.card===button.dataset.plan));document.querySelector(`[data-card="${button.dataset.plan}"]`).scrollIntoView({behavior:'smooth',block:'nearest'})}));
document.querySelector('#help-plan').addEventListener('click',()=>notify('الفضية للاستخدام اليومي، والماسية لمزايا أكثر وضمان ذهبي.'));
document.querySelectorAll('.swatches button').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.swatches button').forEach(b=>b.classList.toggle('selected',b===button));document.querySelector('.phone').style.setProperty('--snap',button.dataset.color)}));
document.querySelectorAll('.slider-controls button').forEach(button=>button.addEventListener('click',()=>document.querySelector('#product-grid').scrollBy({left:Number(button.dataset.scroll)*300,behavior:'smooth'})));
document.querySelector('#newsletter-form').addEventListener('submit',event=>{event.preventDefault();document.querySelector('#newsletter-note').textContent='شكراً لك! تم تسجيل البريد في هذه المعاينة.';event.target.reset()});
document.querySelector('#contact-button').addEventListener('click',()=>notify('هذه معاينة محلية. أضف رابط واتساب الرسمي قبل النشر.'));
document.addEventListener('keydown',event=>{if(event.key==='Escape')closePanels()});

// Local admin settings: no account or server required.
const settingsKey='moon-store-admin-v1';
const defaultColors={red:'#dba919',bg:'#090806',panel:'#15120b',text:'#fffaf0',gold:'#ffd34c'};
const imageTargets={logo:'.brand img',hero:'.hero-scene','cat-media':'.category:nth-child(1) img','cat-watch':'.category:nth-child(2) img','cat-plus':'.category:nth-child(3) img','cat-codes':'.category:nth-child(4) img','cat-offers':'.category:nth-child(5) img','cat-digital':'.category:nth-child(6) img','snap-annual':'.product-card:nth-child(1) .product-art img','snap-month':'.product-card:nth-child(2) .product-art img',gemini:'.product-card:nth-child(3) .product-art img',chatgpt:'.product-card:nth-child(4) .product-art img'};
let settings={storeName:'مون ستور',whatsapp:'',colors:{...defaultColors},images:{},texts:{}};
try{const saved=JSON.parse(localStorage.getItem(settingsKey)||'null');if(saved)settings={...settings,...saved,colors:{...defaultColors,...(saved.colors||{})},images:saved.images||{},texts:saved.texts||{}}}catch{notify('تعذر قراءة إعدادات لوحة الإدارة')}
function findPath(node){const path=[];let current=node;while(current&&current!==document.body){const parent=current.parentNode;if(!parent)return null;path.unshift([...parent.childNodes].indexOf(current));current=parent}return current===document.body?path:null}
function nodeAtPath(path){let node=document.body;for(const index of path||[]){if(!node?.childNodes?.[index])return null;node=node.childNodes[index]}return node?.nodeType===3?node:null}
function textNodes(){const result=[];const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;while(node=walker.nextNode()){const parent=node.parentElement;if(!parent||parent.closest('.admin-panel,.admin-launch,.toast,.drawer,.search-modal,script,style'))continue;if(!node.textContent.trim())continue;const path=findPath(node);if(path)result.push({node,path,key:JSON.stringify(path),text:node.textContent})}return result}
function syncLinkedContent(node,value){const parent=node?.parentElement;if(!parent)return;const card=parent.closest('.product-card,.plan-card,.tv-grid article');const action=card?.querySelector('.add-cart,.add-plan');if(!action)return;if(parent.matches('h3'))action.dataset.name=value.trim();if(parent.matches('.product-price strong,.price strong,.tv-grid b')){const digits=value.replace(/[^0-9]/g,'');if(digits)action.dataset.price=digits}}
function applySettings(){
  Object.entries(settings.colors||{}).forEach(([key,value])=>{document.documentElement.style.setProperty(`--${key}`,value);if(key==='red')document.documentElement.style.setProperty('--red2',value);if(key==='panel')document.documentElement.style.setProperty('--panel2',value)});
  document.title=`${settings.storeName||'مون ستور'} | كل اللي تحتاجه بمكان واحد`;
  document.querySelectorAll('.brand img').forEach(img=>img.alt=settings.storeName||'مون ستور');
  for(const [key,data] of Object.entries(settings.images||{})){if(!data)continue;const target=document.querySelector(imageTargets[key]);if(!target)continue;if(key==='hero'){target.classList.add('has-custom');target.style.backgroundImage=`url("${data}")`}else target.src=data}
  for(const [key,value] of Object.entries(settings.texts||{})){const node=nodeAtPath(JSON.parse(key));if(node){node.textContent=value;syncLinkedContent(node,value)}}
}
applySettings();

const adminPanel=document.querySelector('#admin-panel');
const adminStatus=document.querySelector('#admin-status');
function openAdmin(){adminPanel.classList.add('open');adminPanel.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';renderCopyList();syncAdminForm()}
function closeAdmin(){adminPanel.classList.remove('open');adminPanel.setAttribute('aria-hidden','true');document.body.style.overflow='';history.replaceState(null,'',location.pathname+location.search)}
document.querySelector('#admin-launch').addEventListener('click',openAdmin);
document.querySelector('#admin-close').addEventListener('click',closeAdmin);
if(location.hash==='#admin')openAdmin();
document.querySelectorAll('[data-admin-tab]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-admin-tab]').forEach(item=>item.classList.toggle('active',item===button));document.querySelectorAll('[data-admin-view]').forEach(view=>view.classList.toggle('active',view.dataset.adminView===button.dataset.adminTab));if(button.dataset.adminTab==='copy')renderCopyList()}));
function syncAdminForm(){document.querySelectorAll('[data-setting]').forEach(input=>input.value=settings[input.dataset.setting]||'');document.querySelectorAll('[data-color-setting]').forEach(input=>input.value=settings.colors[input.dataset.colorSetting]||defaultColors[input.dataset.colorSetting]);document.querySelectorAll('[data-preview]').forEach(img=>{const key=img.dataset.preview;if(settings.images[key])img.src=settings.images[key];else img.removeAttribute('src')})}
document.querySelectorAll('[data-setting]').forEach(input=>input.addEventListener('input',()=>{settings[input.dataset.setting]=input.value;if(input.dataset.setting==='storeName'){document.title=`${input.value||'مون ستور'} | كل اللي تحتاجه بمكان واحد`;document.querySelectorAll('.brand img').forEach(img=>img.alt=input.value)}}));
document.querySelectorAll('[data-color-setting]').forEach(input=>input.addEventListener('input',()=>{const key=input.dataset.colorSetting;settings.colors[key]=input.value;document.documentElement.style.setProperty(`--${key}`,input.value);if(key==='red')document.documentElement.style.setProperty('--red2',input.value);if(key==='panel')document.documentElement.style.setProperty('--panel2',input.value)}));
function renderCopyList(){const list=document.querySelector('#copy-list');if(list.dataset.built==='yes')return;list.dataset.built='yes';const nodes=textNodes();document.querySelector('#copy-count').textContent=`${nodes.length} عبارة`;for(const item of nodes){const row=document.createElement('div');row.className='copy-row';row.dataset.searchText=item.text.toLocaleLowerCase();const label=document.createElement('label');label.textContent=`عبارة ${nodes.indexOf(item)+1} · ${item.text.slice(0,36)}`;const textarea=document.createElement('textarea');textarea.value=settings.texts[item.key]??item.text;textarea.setAttribute('aria-label',`تعديل: ${item.text.slice(0,70)}`);textarea.addEventListener('input',()=>{settings.texts[item.key]=textarea.value;item.node.textContent=textarea.value;syncLinkedContent(item.node,textarea.value);row.dataset.searchText=`${item.text} ${textarea.value}`.toLocaleLowerCase();adminStatus.textContent='فيه تعديلات غير محفوظة.'});row.append(label,textarea);list.append(row)}document.querySelector('#copy-filter').addEventListener('input',event=>{const query=event.target.value.trim().toLocaleLowerCase();document.querySelectorAll('.copy-row').forEach(row=>row.hidden=Boolean(query&&!row.dataset.searchText.includes(query)))});}
async function compressImage(file){const bitmap=await createImageBitmap(file);const scale=Math.min(1,1200/Math.max(bitmap.width,bitmap.height));const canvas=document.createElement('canvas');canvas.width=Math.round(bitmap.width*scale);canvas.height=Math.round(bitmap.height*scale);canvas.getContext('2d').drawImage(bitmap,0,0,canvas.width,canvas.height);bitmap.close();return canvas.toDataURL('image/webp',.82)}
document.querySelectorAll('[data-image-setting]').forEach(input=>input.addEventListener('change',async()=>{const file=input.files?.[0];if(!file)return;try{const key=input.dataset.imageSetting;const data=await compressImage(file);settings.images[key]=data;document.querySelector(`[data-preview="${key}"]`).src=data;const target=document.querySelector(imageTargets[key]);if(key==='hero'){target.classList.add('has-custom');target.style.backgroundImage=`url("${data}")`}else target.src=data;adminStatus.textContent='تم اختيار الصورة. احفظ التغييرات للاحتفاظ بها.'}catch{notify('ما قدرنا نفتح الصورة. جرّب صورة بصيغة مختلفة.')}}));
function saveSettings(){try{localStorage.setItem(settingsKey,JSON.stringify(settings));adminStatus.textContent='تم حفظ التغييرات على هذا المتصفح.';notify('انحفظت تغييراتك على هذا الجهاز')}catch{adminStatus.textContent='المساحة المتاحة لا تكفي. صغّر الصور أو احذف بعضها.';notify('ما انحفظت التعديلات — الصور تحتاج مساحة أقل')}}
document.querySelector('#admin-save').addEventListener('click',saveSettings);
document.querySelector('#save-settings').addEventListener('click',saveSettings);
document.querySelector('#export-settings').addEventListener('click',()=>{saveSettings();const blob=new Blob([JSON.stringify(settings,null,2)],{type:'application/json'});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='elv-store-settings.json';link.click();URL.revokeObjectURL(link.href)});
document.querySelector('#import-settings').addEventListener('change',async event=>{const file=event.target.files?.[0];if(!file)return;try{const imported=JSON.parse(await file.text());if(!imported||typeof imported!=='object')throw Error('invalid');settings={...settings,...imported,colors:{...defaultColors,...(imported.colors||{})},images:imported.images||{},texts:imported.texts||{}};saveSettings();location.reload()}catch{notify('ملف الإعدادات غير صالح')}finally{event.target.value=''}});
document.querySelector('#reset-settings').addEventListener('click',()=>{if(!confirm('ترجع كل النصوص والصور والألوان للوضع الأصلي؟'))return;localStorage.removeItem(settingsKey);location.reload()});
document.querySelector('#contact-button').addEventListener('click',event=>{if(!settings.whatsapp)return;event.stopImmediatePropagation();const phone=settings.whatsapp.replace(/\D/g,'');if(!/^\d{8,15}$/.test(phone)){notify('تحقق من رقم واتساب ورمز الدولة في لوحة الإدارة');return}window.open(`https://wa.me/${phone}`,'_blank','noopener,noreferrer')},true);
if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){const revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('revealed');revealObserver.unobserve(entry.target)}}),{threshold:.08});document.querySelectorAll('main > section:not(.hero),.footer-main,.promise-inner').forEach(section=>{section.dataset.reveal='';revealObserver.observe(section)})}
