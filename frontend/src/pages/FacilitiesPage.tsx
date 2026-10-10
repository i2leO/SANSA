import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';
import { Facility } from '@/types';
import PublicLayout from '@/components/PublicLayout';

function mapUrl(item: Facility) {
  if (item.map_link && /^https?:\/\//i.test(item.map_link)) return item.map_link;
  if (item.latitude != null && item.longitude != null) return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${item.latitude},${item.longitude}`)}`;
  return null;
}
function mapEmbedUrl(item: Facility) {
  const query=item.address || item.name;
  return `https://www.google.com/maps?q=${encodeURIComponent(query)}&output=embed`;
}
export default function FacilitiesPage() {
  const [items,setItems]=useState<Facility[]>([]);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState(false);
  const [search,setSearch]=useState('');
  const [selectedId,setSelectedId]=useState<number|null>(null);
  useEffect(()=>{let active=true;apiClient.get<Facility[]>('/facilities').then(r=>{if(active)setItems(r.data);}).catch(()=>{if(active)setError(true);}).finally(()=>{if(active)setLoading(false);});return()=>{active=false;};},[]);
  const filtered=items.filter(item=>`${item.name} ${item.address || ''}`.toLowerCase().includes(search.toLowerCase()));
  const selected=filtered.find(item=>item.id===selectedId) || filtered[0];
  return <PublicLayout title="สถานบริการสุขภาพ"><section className="sansa-banner p-8 mb-7"><h2 className="relative text-3xl font-bold">🏥 สถานบริการสุขภาพ</h2><p className="relative mt-3">ค้นหาศูนย์บริการสาธารณสุขใกล้บ้าน</p></section>
    <input aria-label="ค้นหาสถานบริการ" className="sansa-search mb-6" placeholder="ค้นหาชื่อสถานบริการหรือที่อยู่" value={search} onChange={e=>setSearch(e.target.value)} />
    {loading ? <p role="status">กำลังโหลดสถานบริการ…</p> : error ? <p role="alert">โหลดข้อมูลไม่สำเร็จ กรุณาลองใหม่</p> : filtered.length===0 ? <p className="sansa-panel p-8">ไม่พบสถานบริการ</p> : <div className="sansa-facility-layout"><div className="sansa-facility-list">{filtered.map(item=><article key={item.id} className={`sansa-panel sansa-facility-card ${selected?.id===item.id?'selected':''}`}><button type="button" onClick={()=>setSelectedId(item.id)}><span className="sansa-menu-icon sansa-icon-teal" aria-hidden>🏥</span><span><b>{item.name}</b>{item.address&&<small>📍 {item.address}</small>}</span></button><div>{item.phone && /\d/.test(item.phone) && <a href={`tel:${item.phone.replace(/[^+\d]/g,'')}`}>โทร {item.phone}</a>}{mapUrl(item) && <a href={mapUrl(item)!} target="_blank" rel="noopener noreferrer">เปิด Google Maps ↗</a>}</div></article>)}</div>{selected&&<aside className="sansa-panel sansa-map-panel"><div><h2>{selected.name}</h2><p>{selected.address}</p></div><iframe key={selected.id} title={`แผนที่ ${selected.name}`} src={mapEmbedUrl(selected)} loading="lazy" referrerPolicy="no-referrer-when-downgrade" allowFullScreen /></aside>}</div>}
  </PublicLayout>;
}
