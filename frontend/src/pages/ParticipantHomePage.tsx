import apiClient from "@/lib/api";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

interface Respondent { id:number; respondent_code:string }
interface Visit { id:number; visit_date:string }

export default function ParticipantHomePage(){
  const {respondentCode}=useParams();
  const [latestVisit,setLatestVisit]=useState<number|null>(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");
  useEffect(()=>{let active=true;(async()=>{try{
    const respondent=await apiClient.get<Respondent>(`/respondents/${respondentCode}`);
    const visits=await apiClient.get<Visit[]>(`/visits/respondent/${respondent.data.id}`);
    if(active)setLatestVisit(visits.data[0]?.id||null);
  }catch{if(active)setError("โหลดข้อมูลผู้เข้าร่วมไม่สำเร็จ กรุณาสแกน QR ใหม่");}finally{if(active)setLoading(false);}})();return()=>{active=false};},[respondentCode]);

  const code=encodeURIComponent(respondentCode||"");
  const menu=[
    {icon:"🩺",title:"ประเมินภาวะโภชนาการ",detail:"เริ่มหรือทำแบบประเมินต่อ",to:`/general-info/${code}`,tone:"bg-teal-600 text-white"},
    {icon:"📋",title:"ผลและสื่อของฉัน",detail:latestVisit?"ดูผล Mission และความรู้ที่แนะนำ":"ทำแบบประเมินก่อนเพื่อดูผล",to:latestVisit?`/result/${latestVisit}`:`/general-info/${code}`,tone:"bg-white text-slate-900"},
    {icon:"🍽️",title:"บันทึกอาหาร",detail:"บันทึกมื้ออาหารและของว่างประจำวัน",to:`/food-diary/${code}`,tone:"bg-white text-slate-900"},
    {icon:"✅",title:"Mission วันนี้",detail:"ภารกิจโภชนาการที่ทำได้ง่าย",to:"/knowledge?category=MISSION",tone:"bg-white text-slate-900"},
    {icon:"📚",title:"คลังสื่อ SANSA",detail:"ความรู้โภชนาการสำหรับผู้สูงอายุ",to:"/knowledge?category=กินดีวัย 60%2B",tone:"bg-white text-slate-900"},
    {icon:"🚩",title:"ธงโภชนาการผู้สูงอายุ",detail:"ดูสัดส่วนอาหารที่เหมาะสมในแต่ละวัน",to:"/knowledge?slug=nutrition-60plus-11",tone:"bg-white text-slate-900"},
    {icon:"⭐",title:"ประเมินความพึงพอใจ",detail:latestVisit?"บอกความคิดเห็นเพื่อช่วยพัฒนาระบบ":"ทำแบบประเมินก่อนส่งความคิดเห็น",to:latestVisit?`/satisfaction/${latestVisit}`:`/general-info/${code}`,tone:"bg-white text-slate-900"},
    {icon:"🏥",title:"สถานบริการและการติดต่อ",detail:"ค้นหาศูนย์บริการใกล้บ้าน",to:"/facilities",tone:"bg-white text-slate-900"},
  ];
  return <div className="min-h-screen bg-[#f6faf9] pb-24"><main className="mx-auto max-w-2xl px-4 py-7">
    <section className="mb-6 overflow-hidden rounded-3xl bg-gradient-to-br from-teal-600 to-cyan-500 p-7 text-white shadow-lg"><p className="text-sm font-bold text-white/80">🌿 SANSA</p><h1 className="mt-3 text-3xl font-bold">สวัสดีค่ะ</h1><p className="mt-2 text-lg text-white/90">วันนี้ดูแลเรื่องอาหารไปด้วยกันนะคะ</p><p className="mt-5 rounded-xl bg-white/15 px-4 py-2 text-sm">รหัสผู้เข้าร่วม: <strong>{respondentCode}</strong></p></section>
    {error&&<p role="alert" className="mb-4 rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}
    {loading?<p className="text-center text-slate-500">กำลังโหลดข้อมูล…</p>:<div className="grid gap-4 sm:grid-cols-2">{menu.map((item,index)=><Link key={item.title} to={item.to} className={`rounded-3xl border border-slate-200 p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-lg ${item.tone} ${index===0?"sm:col-span-2":""}`}><span className="text-4xl" aria-hidden>{item.icon}</span><h2 className="mt-3 text-xl font-bold">{item.title}</h2><p className={`mt-1 ${index===0?"text-white/85":"text-slate-500"}`}>{item.detail}</p><span className="mt-4 block font-bold">เปิดเมนู →</span></Link>)}</div>}
  </main><nav className="fixed inset-x-0 bottom-0 border-t bg-white/95 px-3 py-2 shadow-lg backdrop-blur"><div className="mx-auto grid max-w-2xl grid-cols-4 gap-1 text-center text-xs"><Link to={`/general-info/${code}`} className="rounded-xl p-2">🩺<span className="block">ประเมิน</span></Link><Link to={`/food-diary/${code}`} className="rounded-xl p-2">🍽️<span className="block">บันทึกอาหาร</span></Link><Link to="/knowledge?category=MISSION" className="rounded-xl p-2">✅<span className="block">Mission</span></Link><Link to="/knowledge" className="rounded-xl p-2">📚<span className="block">คลังสื่อ</span></Link></div></nav></div>;
}
