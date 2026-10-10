import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import apiClient from '@/lib/api';
import { KnowledgePost } from '@/types';
import PublicLayout from '@/components/PublicLayout';
export default function KnowledgePage() {
  const [params]=useSearchParams();
  const category=params.get('category');
  const slug=params.get('slug');
  const [items,setItems]=useState<KnowledgePost[]>([]);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState(false);
  const [search,setSearch]=useState('');
  useEffect(()=>{let active=true;apiClient.get<KnowledgePost[]>('/knowledge').then(r=>{if(active)setItems(r.data);}).catch(()=>{if(active)setError(true);}).finally(()=>{if(active)setLoading(false);});return()=>{active=false;};},[]);
  const filtered=items.filter(item=>(!category||item.category===category)&&(!slug||item.slug===slug)&&`${item.title} ${item.category || ''}`.toLowerCase().includes(search.toLowerCase()));
  const mission=category==='MISSION';
  return <PublicLayout title={mission?'Mission วันนี้':'ความรู้ด้านโภชนาการ'}><section className="sansa-banner p-8 mb-7"><h2 className="relative text-3xl font-bold">{mission?'✅ Mission วันนี้':'📚 คลังความรู้โภชนาการ'}</h2><p className="relative mt-3">{mission?'เลือกภารกิจง่าย ๆ ที่ทำได้ในวันนี้':'เรียนรู้เรื่องอาหารและสุขภาพ'}</p></section><input aria-label="ค้นหาบทความ" className="sansa-search mb-6" placeholder="ค้นหาหัวข้อหรือหมวดหมู่" value={search} onChange={e=>setSearch(e.target.value)} />
    {loading ? <p role="status">กำลังโหลดบทความ…</p> : error ? <p role="alert">โหลดบทความไม่สำเร็จ กรุณาลองใหม่</p> : filtered.length===0 ? <p className="sansa-panel p-8">ยังไม่มีบทความที่เผยแพร่ตรงกับการค้นหา</p> : <div className="grid md:grid-cols-2 gap-5">{filtered.map(item=><article className="sansa-panel overflow-hidden" key={item.id}>
      {item.featured_image_path && <img src={item.featured_image_path} alt={`ภาพประกอบ ${item.title}`} loading="lazy" className="w-full aspect-[4/5] object-contain bg-slate-50" />}
      <div className="p-7"><span className="text-xs text-primary-700 bg-primary-50 px-3 py-1 rounded-full">{item.category || 'ความรู้โภชนาการ'}</span><h2 className="mt-5 text-xl font-bold">{item.title}</h2>{item.summary && <p className="mt-3 text-slate-500">{item.summary}</p>}
      {item.media_path && <a href={item.media_path} target="_blank" rel="noreferrer" className="sansa-primary-button inline-flex mt-5">{item.media_type === 'pdf' ? 'เปิดเอกสาร PDF' : 'เปิดภาพขนาดเต็ม'}</a>}
      {item.content && <details className="mt-5"><summary className="cursor-pointer font-semibold text-primary-700">อ่านบทความ</summary><div className="mt-4 whitespace-pre-wrap leading-8">{item.content}</div></details>}
      {!item.content && !item.media_path && <p className="mt-4 text-sm text-slate-500">ยังไม่มีเนื้อหาบทความ</p>}</div>
    </article>)}</div>}
  </PublicLayout>;
}
