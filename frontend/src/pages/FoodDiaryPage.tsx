import apiClient from "@/lib/api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

const schema = z.object({
  entry_time: z.string().optional(),
  meal_type: z.enum(["breakfast", "morning_snack", "lunch", "afternoon_snack", "dinner", "before_bed", "other"]),
  menu_name: z.string().min(1, "กรุณาระบุชื่ออาหาร"),
  portion_description: z.string().optional(),
  description: z.string().optional(),
});
type FormData = z.infer<typeof schema>;
type Entry = FormData & { id:number; entry_date:string; photos:Array<{id:number;file_path:string;original_filename:string}> };

const today = () => new Date().toISOString().slice(0, 10);
const shiftDate = (value:string, amount:number) => {
  const date = new Date(`${value}T12:00:00`);
  date.setDate(date.getDate() + amount);
  return date.toISOString().slice(0, 10);
};
const meals = [
  {key:"breakfast", icon:"🌅", label:"มื้อเช้า"},
  {key:"lunch", icon:"☀️", label:"มื้อกลางวัน"},
  {key:"dinner", icon:"🌙", label:"มื้อเย็น"},
] as const;
const snackFor:Record<string,{key:FormData["meal_type"];label:string}> = {
  breakfast:{key:"morning_snack",label:"เพิ่มของว่างเช้า"},
  lunch:{key:"afternoon_snack",label:"เพิ่มของว่างบ่าย"},
};

export default function FoodDiaryPage(){
  const {respondentCode}=useParams();
  const navigate=useNavigate();
  const [visitId,setVisitId]=useState<number|null>(null);
  const [entries,setEntries]=useState<Entry[]>([]);
  const [selectedDate,setSelectedDate]=useState(today());
  const [editing,setEditing]=useState<Entry|null>(null);
  const [formMeal,setFormMeal]=useState<FormData["meal_type"]>("breakfast");
  const [open,setOpen]=useState(false);
  const [busy,setBusy]=useState(false);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState<string|null>(null);
  const {register,handleSubmit,reset,formState:{errors}}=useForm<FormData>({resolver:zodResolver(schema)});

  const reload=async(id:number)=>{
    const response=await apiClient.get<Entry[]>(`/food-diary/visit/${id}`);
    setEntries(response.data);
  };
  useEffect(()=>{let active=true;(async()=>{try{
    const respondent=await apiClient.get(`/respondents/${respondentCode}`);
    const visits=await apiClient.get(`/visits/respondent/${respondent.data.id}`);
    if(!visits.data.length) throw new Error("ยังไม่มีรอบการประเมินสำหรับผู้ใช้นี้");
    const id=visits.data[0].id; if(!active)return; setVisitId(id); await reload(id);
  }catch(err){if(active)setError(err instanceof Error?err.message:"ไม่สามารถโหลดบันทึกอาหารได้");}finally{if(active)setLoading(false);}})();return()=>{active=false};},[respondentCode]);

  const dayEntries=useMemo(()=>entries.filter(item=>item.entry_date===selectedDate),[entries,selectedDate]);
  const completed=meals.filter(meal=>dayEntries.some(item=>item.meal_type===meal.key)).length;
  const openForm=(meal:FormData["meal_type"],entry?:Entry)=>{
    setFormMeal(meal); setEditing(entry||null);
    reset(entry?{entry_time:entry.entry_time?.slice(0,5)||"",meal_type:entry.meal_type,menu_name:entry.menu_name,portion_description:entry.portion_description||"",description:entry.description||""}:{entry_time:new Date().toTimeString().slice(0,5),meal_type:meal,menu_name:"",portion_description:"",description:""});
    setOpen(true);
  };
  const submit=async(data:FormData)=>{if(!visitId)return;setBusy(true);setError(null);try{
    const payload={...data,meal_type:formMeal,entry_date:selectedDate,visit_id:visitId};
    if(editing) await apiClient.put(`/food-diary/${editing.id}`,payload); else await apiClient.post("/food-diary",payload);
    await reload(visitId); setOpen(false); setEditing(null);
  }catch{setError("บันทึกรายการไม่สำเร็จ กรุณาลองใหม่");}finally{setBusy(false);}};
  const remove=async(id:number)=>{if(!confirm("ลบรายการอาหารนี้หรือไม่?"))return;try{await apiClient.delete(`/food-diary/${id}`);setEntries(items=>items.filter(item=>item.id!==id));}catch{setError("ลบรายการไม่สำเร็จ");}};
  const copyYesterday=async(meal:string)=>{if(!visitId)return;const source=entries.filter(item=>item.entry_date===shiftDate(selectedDate,-1)&&item.meal_type===meal);if(!source.length)return;setBusy(true);try{for(const item of source){await apiClient.post("/food-diary",{visit_id:visitId,entry_date:selectedDate,entry_time:item.entry_time,meal_type:item.meal_type,menu_name:item.menu_name,description:item.description,portion_description:item.portion_description});}await reload(visitId);}catch{setError("คัดลอกรายการจากเมื่อวานไม่สำเร็จ");}finally{setBusy(false);}};

  if(loading)return <div className="min-h-screen grid place-items-center bg-[#f7faf9] text-xl">กำลังโหลดบันทึกอาหาร…</div>;
  return <div className="min-h-screen bg-[#f7faf9] pb-20">
    <div className="mx-auto max-w-2xl px-4 py-6">
      <div className="mb-5 flex items-center justify-between"><div><p className="text-sm font-semibold text-teal-700">SANSA</p><h1 className="text-3xl font-bold text-slate-900">บันทึกอาหาร</h1></div><button onClick={()=>navigate("/")} className="rounded-xl border bg-white px-4 py-2 text-slate-600">หน้าหลัก</button></div>
      {error&&<div role="alert" className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}
      <section className="mb-5 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between gap-3"><button aria-label="วันก่อนหน้า" onClick={()=>setSelectedDate(shiftDate(selectedDate,-1))} className="h-12 w-12 rounded-full bg-slate-100 text-3xl">‹</button><div className="text-center"><p className="font-bold text-teal-700">{selectedDate===today()?"วันนี้":"วันที่เลือก"}</p><p className="text-lg font-semibold">{new Date(`${selectedDate}T12:00:00`).toLocaleDateString("th-TH",{weekday:"long",day:"numeric",month:"long",year:"numeric"})}</p></div><button aria-label="วันถัดไป" disabled={selectedDate>=today()} onClick={()=>setSelectedDate(shiftDate(selectedDate,1))} className="h-12 w-12 rounded-full bg-slate-100 text-3xl disabled:opacity-30">›</button></div>
        <label className="mx-auto mt-4 block w-fit cursor-pointer rounded-xl border border-teal-200 px-4 py-2 font-semibold text-teal-700">📅 เลือกวันอื่น<input type="date" max={today()} value={selectedDate} onChange={e=>setSelectedDate(e.target.value)} className="sr-only"/></label>
      </section>
      <section className="mb-5 rounded-3xl bg-teal-700 p-5 text-white"><p className="text-lg font-bold">บันทึกแล้ว {completed} จาก 3 มื้อหลัก</p><div className="mt-4 grid grid-cols-3 gap-2">{meals.map(meal=><div key={meal.key} className={`rounded-xl p-2 text-center text-sm ${dayEntries.some(i=>i.meal_type===meal.key)?"bg-white text-teal-800":"bg-white/15"}`}>{dayEntries.some(i=>i.meal_type===meal.key)?"✓ ":""}{meal.label}</div>)}</div></section>
      <div className="space-y-5">{meals.map(meal=>{const current=dayEntries.filter(i=>i.meal_type===meal.key);const yesterday=entries.filter(i=>i.entry_date===shiftDate(selectedDate,-1)&&i.meal_type===meal.key);const snack=snackFor[meal.key];return <section key={meal.key} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-3"><span className="text-3xl">{meal.icon}</span><div><h2 className="text-xl font-bold">{meal.label}</h2><p className="text-sm text-slate-500">{current.length?`${current.length} รายการ`:"ยังไม่ได้บันทึก"}</p></div></div>
        <div className="space-y-3">{current.map(item=><div key={item.id} className="flex items-center gap-3 rounded-2xl bg-slate-50 p-4"><span className="text-2xl">🍽️</span><button onClick={()=>openForm(meal.key,item)} className="min-w-0 flex-1 text-left"><strong className="block truncate text-lg">{item.menu_name}</strong><span className="text-sm text-slate-500">{item.portion_description||"ไม่ระบุปริมาณ"}{item.entry_time?` · ${item.entry_time.slice(0,5)} น.`:""} · แก้ไข ›</span></button><button aria-label="ลบรายการ" onClick={()=>remove(item.id)} className="rounded-lg p-2 text-red-600">ลบ</button></div>)}</div>
        <button onClick={()=>openForm(meal.key)} className="mt-4 w-full rounded-2xl bg-teal-600 py-3 font-bold text-white">＋ เพิ่มอาหาร</button>
        {yesterday.length>0&&<button disabled={busy} onClick={()=>copyYesterday(meal.key)} className="mt-3 w-full rounded-2xl border border-teal-200 bg-teal-50 p-3 text-left font-semibold text-teal-800">↻ กินเหมือนเมื่อวาน <span className="block truncate text-sm font-normal text-teal-700">{yesterday.map(i=>i.menu_name).join(", ")}</span></button>}
        {snack&&<button onClick={()=>openForm(snack.key)} className="mt-3 w-full rounded-2xl border border-dashed border-slate-300 py-3 font-semibold text-slate-600">＋ {snack.label}</button>}
        {snack&&dayEntries.filter(i=>i.meal_type===snack.key).map(item=><button key={item.id} onClick={()=>openForm(item.meal_type,item)} className="mt-3 w-full rounded-2xl bg-amber-50 p-3 text-left"><strong>{item.menu_name}</strong><span className="ml-2 text-sm text-slate-500">ของว่าง · แก้ไข ›</span></button>)}
      </section>})}</div>
    </div>
    {open&&<div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 sm:items-center sm:p-4"><div className="max-h-[92vh] w-full max-w-lg overflow-y-auto rounded-t-3xl bg-white p-6 shadow-2xl sm:rounded-3xl"><div className="mb-5 flex justify-between"><h2 className="text-2xl font-bold">{editing?"แก้ไขรายการอาหาร":"เพิ่มรายการอาหาร"}</h2><button onClick={()=>setOpen(false)} className="text-2xl" aria-label="ปิด">×</button></div><form onSubmit={handleSubmit(submit)} className="space-y-4">
      <div><label className="mb-1 block font-bold">ชื่ออาหาร *</label><input {...register("menu_name")} placeholder="เช่น ข้าวต้ม โจ๊ก นมจืด" className="w-full rounded-xl border-2 border-slate-200 p-3 text-lg"/>{errors.menu_name&&<p className="text-red-600">{errors.menu_name.message}</p>}</div>
      <div className="grid grid-cols-2 gap-3"><div><label className="mb-1 block font-bold">ปริมาณ</label><input {...register("portion_description")} placeholder="เช่น 1 ชาม" className="w-full rounded-xl border-2 border-slate-200 p-3"/></div><div><label className="mb-1 block font-bold">เวลา</label><input type="time" {...register("entry_time")} className="w-full rounded-xl border-2 border-slate-200 p-3"/></div></div>
      <div><label className="mb-1 block font-bold">รายละเอียดเพิ่มเติม</label><textarea {...register("description")} placeholder="ส่วนประกอบหรือวิธีปรุง (ถ้ามี)" className="w-full rounded-xl border-2 border-slate-200 p-3" rows={3}/></div>
      <input type="hidden" {...register("meal_type")} value={formMeal}/>
      <div className="grid grid-cols-2 gap-3 pt-2"><button type="button" onClick={()=>setOpen(false)} className="rounded-xl border-2 py-3 font-bold">ยกเลิก</button><button disabled={busy} type="submit" className="rounded-xl bg-teal-600 py-3 font-bold text-white disabled:opacity-50">{busy?"กำลังบันทึก…":"บันทึก"}</button></div>
    </form></div></div>}
  </div>;
}
