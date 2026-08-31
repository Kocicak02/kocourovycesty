import json, os, re, urllib.request, urllib.error
from pathlib import Path
from html import escape

zone=os.environ['BUNNY_STORAGE_ZONE']; key=os.environ['BUNNY_STORAGE_KEY']
NAME_MAP={'2026_08_Praha-Munich-Zurich':'2026_08_Praha-Munchen-Zurich'}

def bunny(path=''):
    url=f'https://storage.bunnycdn.com/{zone}/'+(path.strip('/')+'/' if path else '')
    req=urllib.request.Request(url,headers={'AccessKey':key,'Accept':'application/json'})
    with urllib.request.urlopen(req) as r:return json.load(r)

def media_files(activity,sub):
    try:data=bunny(f'{activity}/{sub}')
    except urllib.error.HTTPError as e:
        if e.code==404:return []
        raise
    return sorted([x['ObjectName'] for x in data if not x.get('IsDirectory') and x.get('ObjectName')],key=str.lower)

# MEDIA.JS
for item in bunny():
    if not item.get('IsDirectory') or not item.get('ObjectName'):continue
    bname=item['ObjectName']; gname=NAME_MAP.get(bname,bname); folder=Path(gname)
    if not folder.is_dir():continue
    photos=media_files(bname,'FOTO'); videos=media_files(bname,'VIDEO')
    text='// Automaticky generovano z Bunny Storage.\n// Neupravovat rucne.\n\n'
    text+='window.MEDIA_PHOTOS = '+json.dumps(photos,ensure_ascii=False,indent=2)+';\n\n'
    text+='window.MEDIA_VIDEOS = '+json.dumps(videos,ensure_ascii=False,indent=2)+';\n'
    (folder/'media.js').write_text(text,encoding='utf-8')


# HLAVICKA VE VSECH DETAIL.HTML — VZDY JEN TEXT
def fix_detail_header(path):
    html=path.read_text(encoding='utf-8',errors='ignore')
    old=html
    html=re.sub(r'(<a\b[^>]*class=["\'][^"\']*\bbrand\b[^"\']*["\'][^>]*>).*?(</a>)',r'\1Kocourovy cesty\2',html,count=1,flags=re.I|re.S)
    html=re.sub(r'\.brand\s+img\s*\{[^}]*\}','',html,flags=re.I)
    if re.search(r'\.brand\s*\{[^}]*\}',html,flags=re.I):
        html=re.sub(r'\.brand\s*\{[^}]*\}','.brand{font-size:18px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}',html,count=1,flags=re.I)
    if html!=old:
        path.write_text(html,encoding='utf-8')
        print('Hlavicka:',path)
for detail in Path('.').glob('*/detail.html'):
    fix_detail_header(detail)


# PLOVOUCI TLACITKO "SBALIT" VE VSECH DETAIL.HTML
FLOAT_START = '<!-- FLOATING-MEDIA-CLOSE:START -->'
FLOAT_END = '<!-- FLOATING-MEDIA-CLOSE:END -->'

FLOAT_BLOCK = r"""
<!-- FLOATING-MEDIA-CLOSE:START -->
<style>
#floatingMediaClose{
  position:fixed;
  right:24px;
  bottom:24px;
  z-index:99999;
  display:none;
  align-items:center;
  gap:8px;
  border:1px solid #111;
  background:#111;
  color:#f5f3ee;
  padding:12px 16px;
  font:700 11px Arial,Helvetica,sans-serif;
  letter-spacing:.09em;
  text-transform:uppercase;
  cursor:pointer;
  box-shadow:0 5px 20px rgba(0,0,0,.18);
}
#floatingMediaClose.visible{display:flex}
#floatingMediaClose:hover{background:#f5f3ee;color:#111}
@media(max-width:600px){
  #floatingMediaClose{
    right:14px;
    bottom:14px;
    padding:11px 14px;
  }
}
</style>

<button id="floatingMediaClose" type="button" aria-label="Sbalit otevřená média">
  ↑ Sbalit
</button>

<script>
(()=>{
  const btn=document.getElementById('floatingMediaClose');
  if(!btn)return;

  function state(){
    const photos=document.getElementById('photosPanel') || document.getElementById('photoPanel');
    const videos=document.getElementById('videosPanel') || document.getElementById('videoPanel');

    if(photos && photos.classList.contains('open')){
      return {
        panel:photos,
        tile:document.getElementById('photosTile') || document.querySelector('.media-tile[onclick*="togglePhotos"]')
      };
    }

    if(videos && videos.classList.contains('open')){
      return {
        panel:videos,
        tile:document.getElementById('videosTile') || document.querySelector('.media-tile[onclick*="toggleVideos"]')
      };
    }

    const generic=document.querySelector('.media-panel.open');
    if(generic){
      return {
        panel:generic,
        tile:null
      };
    }

    return null;
  }

  function refresh(){
    btn.classList.toggle('visible',!!state());
  }

  btn.addEventListener('click',()=>{
    const s=state();
    if(!s)return;

    const target=s.tile || s.panel;

    // Kdyz existuje puvodni dlazdice Fotky/Videa,
    // pouzijeme jeji vlastni click handler, aby vse zustalo synchronizovane.
    if(s.tile){
      s.tile.click();
    }else{
      s.panel.classList.remove('open');
    }

    btn.classList.remove('visible');

    setTimeout(()=>{
      target.scrollIntoView({
        behavior:'smooth',
        block:'center'
      });
    },40);
  });

  // Sleduje rozbaleni/sbaleni bez ohledu na to, jaky detail ho provedl.
  const observer=new MutationObserver(refresh);
  observer.observe(document.body,{
    subtree:true,
    attributes:true,
    attributeFilter:['class']
  });

  document.addEventListener('click',()=>setTimeout(refresh,0));
  refresh();
})();
</script>
<!-- FLOATING-MEDIA-CLOSE:END -->
"""

def add_floating_media_close(path):
    html = path.read_text(encoding='utf-8', errors='ignore')

    # Pri opakovanem behu nejdriv odstranit starsi verzi bloku.
    if FLOAT_START in html and FLOAT_END in html:
        before = html.split(FLOAT_START,1)[0]
        after = html.split(FLOAT_END,1)[1]
        html = before + after

    if '</body>' in html:
        html = html.replace('</body>', FLOAT_BLOCK + '\n</body>', 1)
        path.write_text(html, encoding='utf-8')
        print('Plovouci Sbalit:', path)

for detail in Path('.').glob('*/detail.html'):
    add_floating_media_close(detail)


# LIGHTBOX GALERIE FOTEK VE VSECH DETAIL.HTML
LIGHTBOX_START = '<!-- PHOTO-LIGHTBOX:START -->'
LIGHTBOX_END = '<!-- PHOTO-LIGHTBOX:END -->'

LIGHTBOX_BLOCK = r"""
<!-- PHOTO-LIGHTBOX:START -->
<style>
#photoLightbox{
  position:fixed;
  inset:0;
  z-index:100000;
  display:none;
  align-items:center;
  justify-content:center;
  background:rgba(0,0,0,.92);
  padding:28px 76px;
}
#photoLightbox.open{display:flex}
#photoLightbox img{
  display:block;
  max-width:100%;
  max-height:calc(100vh - 56px);
  width:auto;
  height:auto;
  object-fit:contain;
  user-select:none;
  -webkit-user-drag:none;
}
#photoLightbox button{
  position:absolute;
  border:0;
  background:rgba(0,0,0,.35);
  color:#fff;
  cursor:pointer;
  font-family:Arial,Helvetica,sans-serif;
}
#photoLightbox button:hover{background:rgba(255,255,255,.16)}
#photoLightboxClose{
  right:18px;
  top:14px;
  width:46px;
  height:46px;
  font-size:32px;
  line-height:1;
}
.photoLightboxArrow{
  top:50%;
  transform:translateY(-50%);
  width:54px;
  height:74px;
  font-size:44px;
  line-height:1;
}
#photoLightboxPrev{left:12px}
#photoLightboxNext{right:12px}
#photoLightboxCounter{
  position:absolute;
  left:50%;
  bottom:12px;
  transform:translateX(-50%);
  color:#fff;
  font:600 11px Arial,Helvetica,sans-serif;
  letter-spacing:.08em;
  background:rgba(0,0,0,.38);
  padding:5px 8px;
  pointer-events:none;
}
@media(max-width:700px){
  #photoLightbox{padding:58px 12px 62px}
  .photoLightboxArrow{
    top:auto;
    bottom:8px;
    transform:none;
    width:54px;
    height:46px;
    font-size:36px;
  }
  #photoLightboxPrev{left:10px}
  #photoLightboxNext{right:10px}
  #photoLightboxClose{right:10px;top:8px}
}
</style>

<div id="photoLightbox" role="dialog" aria-modal="true" aria-label="Fotogalerie">
  <button id="photoLightboxClose" type="button" aria-label="Zavřít">×</button>
  <button id="photoLightboxPrev" class="photoLightboxArrow" type="button" aria-label="Předchozí fotka">‹</button>
  <img id="photoLightboxImage" alt="">
  <button id="photoLightboxNext" class="photoLightboxArrow" type="button" aria-label="Další fotka">›</button>
  <div id="photoLightboxCounter"></div>
</div>

<script>
(()=>{
  const box=document.getElementById('photoLightbox');
  const image=document.getElementById('photoLightboxImage');
  const prev=document.getElementById('photoLightboxPrev');
  const next=document.getElementById('photoLightboxNext');
  const close=document.getElementById('photoLightboxClose');
  const counter=document.getElementById('photoLightboxCounter');
  if(!box||!image)return;

  let items=[];
  let index=0;
  let oldOverflow='';

  function photoPanels(){
    const selectors=[
      '#photosPanel',
      '#photoPanel',
      '#photoGallery',
      '.gallery'
    ];

    const found=[];
    selectors.forEach(sel=>{
      document.querySelectorAll(sel).forEach(el=>{
        // Nebereme galerie uvnitr mapy/iframe apod.
        if(el.closest('#photoLightbox'))return;
        if(!found.includes(el))found.push(el);
      });
    });
    return found;
  }

  function photoItems(){
    const result=[];
    photoPanels().forEach(panel=>{
      panel.querySelectorAll('img').forEach(img=>{
        const a=img.closest('a');
        const url=(a&&a.href)||img.currentSrc||img.src;
        if(!url)return;
        if(!result.some(x=>x.url===url)){
          result.push({url:url,alt:img.alt||''});
        }
      });
    });
    return result;
  }

  function clickedGalleryImage(target){
    const img=target.closest('img');
    if(!img)return null;

    // Podpora novych i starsich detailu:
    // photosPanel, photoPanel, photoGallery nebo .photo-card/.gallery.
    const inPhotoArea=
      img.closest('#photosPanel') ||
      img.closest('#photoPanel') ||
      img.closest('#photoGallery') ||
      img.closest('.photo-card') ||
      img.closest('.gallery');

    if(!inPhotoArea)return null;
    if(img.closest('#photoLightbox'))return null;
    return img;
  }

  function render(){
    if(!items.length)return;
    if(index<0)index=items.length-1;
    if(index>=items.length)index=0;
    image.src=items[index].url;
    image.alt=items[index].alt;
    counter.textContent=(index+1)+' / '+items.length;

    if(items.length>1){
      const p=items[(index-1+items.length)%items.length];
      const n=items[(index+1)%items.length];
      const pi=new Image(); pi.src=p.url;
      const ni=new Image(); ni.src=n.url;
    }
  }

  function openAt(url){
    items=photoItems();
    if(!items.length)return;
    const found=items.findIndex(x=>x.url===url);
    index=found>=0?found:0;
    oldOverflow=document.body.style.overflow;
    document.body.style.overflow='hidden';
    box.classList.add('open');
    render();
    close.focus({preventScroll:true});
  }

  function hide(){
    box.classList.remove('open');
    image.removeAttribute('src');
    document.body.style.overflow=oldOverflow;
  }

  document.addEventListener('click',e=>{
    const img=clickedGalleryImage(e.target);
    if(!img)return;

    const a=img.closest('a');
    const url=(a&&a.href)||img.currentSrc||img.src;
    if(!url)return;

    e.preventDefault();
    e.stopPropagation();
    openAt(url);
  },true);

  prev.addEventListener('click',e=>{e.stopPropagation();index--;render()});
  next.addEventListener('click',e=>{e.stopPropagation();index++;render()});
  close.addEventListener('click',hide);
  box.addEventListener('click',e=>{if(e.target===box)hide()});

  document.addEventListener('keydown',e=>{
    if(!box.classList.contains('open'))return;
    if(e.key==='Escape'){e.preventDefault();hide()}
    else if(e.key==='ArrowLeft'){e.preventDefault();index--;render()}
    else if(e.key==='ArrowRight'){e.preventDefault();index++;render()}
  });
})();
</script>
<!-- PHOTO-LIGHTBOX:END -->
"""

def add_photo_lightbox(path):
    html=path.read_text(encoding='utf-8',errors='ignore')

    # Pri opakovanem behu nejdriv odstranit starsi verzi lightboxu.
    if LIGHTBOX_START in html and LIGHTBOX_END in html:
        before=html.split(LIGHTBOX_START,1)[0]
        after=html.split(LIGHTBOX_END,1)[1]
        html=before+after

    if '</body>' in html:
        html=html.replace('</body>',LIGHTBOX_BLOCK+'\n</body>',1)
        path.write_text(html,encoding='utf-8')
        print('Foto lightbox:',path)

for detail in Path('.').glob('*/detail.html'):
    add_photo_lightbox(detail)

# CARD.JSON
cards=[]
for cp in Path('.').glob('*/card.json'):
    folder=cp.parent
    if not (folder/'detail.html').exists():continue
    try:d=json.loads(cp.read_text(encoding='utf-8'))
    except Exception as e:
        print('Chyba',cp,e);continue
    title=str(d.get('title','')).strip()
    if not title:continue
    cards.append({'folder':folder.name,'title':title,'date':str(d.get('date','')).strip(),'type':str(d.get('type','')).strip(),'image':str(d.get('image','')).strip()})
cards.sort(key=lambda x:x['folder'],reverse=True)

# ROUTES Z EXISTUJÍCÍCH track*.js

def load_qgis_js(path):
    s=path.read_text(encoding='utf-8',errors='ignore')
    m=re.search(r'=\s*(\{.*\})\s*;?\s*$',s,re.S)
    if not m:return None
    try:return json.loads(m.group(1))
    except:return None

def geom_lines(g):
    if not g:return []
    t=g.get('type'); c=g.get('coordinates')
    if t=='LineString':return [c]
    if t=='MultiLineString':return c or []
    if t=='GeometryCollection':
        out=[]
        for gg in g.get('geometries',[]):out.extend(geom_lines(gg))
        return out
    return []

def geo_lines(d):
    if not d:return []
    t=d.get('type')
    if t=='FeatureCollection':
        out=[]
        for f in d.get('features',[]):out.extend(geom_lines(f.get('geometry')))
        return out
    if t=='Feature':return geom_lines(d.get('geometry'))
    return geom_lines(d)

def reduce_line(line,max_points=1800):
    clean=[]
    for p in line or []:
        if isinstance(p,list) and len(p)>=2 and isinstance(p[0],(int,float)) and isinstance(p[1],(int,float)) and -180<=p[0]<=180 and -90<=p[1]<=90:
            clean.append([round(p[0],6),round(p[1],6)])
    if len(clean)<=max_points:return clean
    step=(len(clean)-1)/(max_points-1)
    out=[]
    for i in range(max_points):
        p=clean[round(i*step)]
        if not out or p!=out[-1]:out.append(p)
    return out

routes=[]
for card in cards:
    folder=Path(card['folder']); lines=[]
    candidates=sorted([p for p in folder.rglob('*.js') if p.name.lower().startswith('track') and not p.name.lower().startswith('track_points')],key=lambda p:str(p).lower())
    for p in candidates:
        d=load_qgis_js(p)
        for line in geo_lines(d):
            r=reduce_line(line)
            if len(r)>=2:lines.append(r)
    if lines:
        routes.append({'folder':card['folder'],'title':card['title'],'date':card['date'],'type':card['type'],'lines':lines})
        print('Mapa:',card['folder'],len(lines),'useku')
    else:print('Mapa:',card['folder'],'bez tracku')

Path('generated-routes.js').write_text('// Automaticky generovano z existujicich aktivit.\nwindow.ALL_ROUTES = '+json.dumps(routes,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# KARTY
cards_html=[]
for c in cards:
    img=f'<img class="card-image" src="{escape(c["image"])}" alt="">' if c['image'] else ''
    typ=f'<div class="card-type">{escape(c["type"])}</div>' if c['type'] else ''
    cards_html.append(f'''<a class="card" href="/{escape(c['folder'])}/detail.html">{img}<div class="card-content">{typ}<div class="card-title">{escape(c['title'])}</div><div class="card-bottom"><span>{escape(c['date'])}</span><span>Otevřít →</span></div></div></a>''')

home_cards='\n'.join(cards_html[:3])

index=f'''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kocourovy cesty</title><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"><style>
:root{{--bg:#f5f3ee;--text:#111;--muted:#777;--line:#d9d5cc;--card:#ebe7df}}*{{box-sizing:border-box}}html,body{{margin:0;background:var(--bg);color:var(--text);font-family:Arial,Helvetica,sans-serif}}a{{color:inherit;text-decoration:none}}header{{display:flex;align-items:center;justify-content:space-between;padding:28px 42px;border-bottom:1px solid var(--line)}}.brand{{font-size:18px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}}nav{{font-size:13px;text-transform:uppercase;letter-spacing:.08em}}main{{max-width:1400px;margin:auto;padding:42px}}.head{{display:flex;justify-content:space-between;align-items:end;margin-bottom:18px}}.head h1,.head h2{{margin:0;font-size:14px;text-transform:uppercase;letter-spacing:.12em}}.head span{{font-size:12px;color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.card{{display:flex;flex-direction:column;min-height:390px;background:var(--card);overflow:hidden;transition:transform .18s ease}}.card:hover{{transform:translateY(-3px)}}.card-image{{width:100%;height:250px;object-fit:contain;display:block}}.card-content{{display:flex;flex:1;flex-direction:column;padding:22px}}.card-type{{margin-bottom:8px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}}.card-title{{font-size:24px;font-weight:700;line-height:1.08}}.card-bottom{{margin-top:auto;padding-top:24px;display:flex;justify-content:space-between;gap:15px;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}}.map-section{{margin-top:58px}}.toolbar{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}}.filter{{border:1px solid var(--line);background:transparent;padding:8px 12px;font:inherit;font-size:10px;text-transform:uppercase;letter-spacing:.09em;cursor:pointer}}.filter.active{{background:#111;color:var(--bg);border-color:#111}}#all-map{{height:540px;border:1px solid var(--line);background:var(--card)}}.popup-title{{font-size:16px;font-weight:700}}.popup-meta{{margin-top:5px;color:#777;font-size:11px;text-transform:uppercase}}.popup-link{{display:inline-block;margin-top:12px;font-size:11px;font-weight:700;text-transform:uppercase}}footer{{max-width:1400px;margin:auto;padding:34px 42px 50px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}}@media(max-width:900px){{header{{padding:20px}}main{{padding:24px 20px}}.grid{{grid-template-columns:1fr}}#all-map{{height:460px}}}}@media(max-width:560px){{#all-map{{height:390px}}}}
</style></head><body><header><a class="brand" href="/">Kocourovy cesty</a><nav><a href="/archiv.html">Archiv</a></nav></header><main><section><div class="head"><h1>Poslední aktivity</h1><span>{len(cards)} aktivit</span></div><div class="grid">{home_cards}</div></section><section class="map-section"><div class="head"><h2>Kde jsem byl</h2><span id="map-count"></span></div><div class="toolbar" id="toolbar"></div><div id="all-map"></div></section></main><footer>Kocourovy cesty</footer><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script src="/generated-routes.js"></script><script>
(()=>{{const routes=window.ALL_ROUTES||[],count=document.getElementById('map-count'),bar=document.getElementById('toolbar');count.textContent=routes.length+' aktivit na mapě';const map=L.map('all-map',{{scrollWheelZoom:false}});L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:19,attribution:'&copy; OpenStreetMap contributors'}}).addTo(map);const items=[],bounds=L.latLngBounds();const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');const routeColor=type=>{{const t=String(type||'').trim().toUpperCase();if(t.includes('CYKLIST'))return '#2e7d32';if(t.includes('BĚH')||t.includes('BEH'))return '#c62828';if(t.includes('BĚŽ')||t.includes('BEZ'))return '#1565c0';if(t.includes('LYŽ')||t.includes('LYZ'))return '#6a1b9a';if(t.includes('TÚRA')||t.includes('TURA'))return '#ef6c00';return '#111'}};routes.forEach(r=>{{const color=routeColor(r.type);const g=L.featureGroup();let hoverTimer=null;const highlightGroup=()=>{{if(hoverTimer){{clearTimeout(hoverTimer);hoverTimer=null}}g.eachLayer(layer=>{{if(layer.setStyle)layer.setStyle({{color:color,weight:5,opacity:1}});if(layer.bringToFront)layer.bringToFront()}})}};const resetGroup=()=>{{hoverTimer=setTimeout(()=>{{g.eachLayer(layer=>{{if(layer.setStyle)layer.setStyle({{color:color,weight:2.5,opacity:.78}})}});hoverTimer=null}},80)}};(r.lines||[]).forEach(line=>{{const pts=line.map(p=>[p[1],p[0]]);if(pts.length<2)return;const l=L.polyline(pts,{{color:color,weight:2.5,opacity:.78}});l.on('mouseover',highlightGroup);l.on('mouseout',resetGroup);l.bindPopup(`<div class="popup-title">${{esc(r.title)}}</div><div class="popup-meta">${{esc(r.type)}}${{r.type&&r.date?' · ':''}}${{esc(r.date)}}</div><a class="popup-link" href="/${{encodeURIComponent(r.folder)}}/detail.html">Zobrazit aktivitu →</a>`);l.addTo(g)}});if(g.getLayers().length){{g.addTo(map);const b=g.getBounds();if(b.isValid())bounds.extend(b);items.push({{r,g}})}}}});if(bounds.isValid())map.fitBounds(bounds,{{padding:[25,25]}});else map.setView([49.8,15.4],6);const norm=s=>String(s||'').trim().toUpperCase();const types=[...new Set(routes.map(r=>norm(r.type)).filter(Boolean))].sort();[{{label:'Vše',value:''}},...types.map(t=>({{label:t,value:t}}))].forEach((f,i)=>{{const b=document.createElement('button');b.className='filter'+(i===0?' active':'');b.type='button';b.textContent=f.label;b.dataset.type=f.value;b.onclick=()=>{{items.forEach(x=>{{const show=!f.value||norm(x.r.type)===f.value;if(show&&!map.hasLayer(x.g))x.g.addTo(map);if(!show&&map.hasLayer(x.g))map.removeLayer(x.g)}});document.querySelectorAll('.filter').forEach(x=>x.classList.toggle('active',x.dataset.type===f.value))}};bar.appendChild(b)}})}})();
</script></body></html>'''
Path('index.html').write_text(index,encoding='utf-8')

rows=[]
for c in cards:
    rows.append(f'''<a class="trip" href="/{escape(c['folder'])}/detail.html"><div class="date">{escape(c['date'])}</div><div><div class="trip-type">{escape(c['type'])}</div><div class="name">{escape(c['title'])}</div></div><div class="arrow">→</div></a>''')
archive='''<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Archiv — Kocourovy cesty</title><style>:root{--bg:#f5f3ee;--text:#111;--muted:#777;--line:#d9d5cc}*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--text);font-family:Arial,Helvetica,sans-serif}a{color:inherit;text-decoration:none}header{display:flex;align-items:center;justify-content:space-between;padding:28px 42px;border-bottom:1px solid var(--line)}.brand{font-size:18px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}nav{font-size:13px;text-transform:uppercase;letter-spacing:.08em}main{max-width:1400px;margin:auto;padding:42px}h1{margin:0 0 36px;font-size:14px;text-transform:uppercase;letter-spacing:.12em}.trip{display:grid;grid-template-columns:120px 1fr auto;gap:25px;align-items:center;padding:25px 0;border-top:1px solid var(--line)}.trip:last-child{border-bottom:1px solid var(--line)}.date{color:var(--muted);font-size:12px}.trip-type{margin-bottom:5px;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.09em}.name{font-size:24px;font-weight:700}.arrow{font-size:20px}@media(max-width:700px){header{padding:20px}main{padding:24px 20px}.trip{grid-template-columns:1fr auto}.date{grid-column:1/-1}}</style></head><body><header><a class="brand" href="/">Kocourovy cesty</a><nav><a href="/archiv.html">Archiv</a></nav></header><main><h1>Archiv cest</h1>'''+''.join(rows)+'''</main></body></html>'''
Path('archiv.html').write_text(archive,encoding='utf-8')
print(f'Hotovo: {len(cards)} aktivit, {len(routes)} aktivit na mape.')
