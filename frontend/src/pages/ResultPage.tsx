import apiClient from "@/lib/api";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

interface ParticipantResult { predicted_group: string | null; ready: boolean; }
interface KnowledgeItem { id: number; slug: string; title: string; summary?: string | null; featured_image_path?: string | null; media_path?: string | null; }

const groupLabel = (group: string | null) => ({ UNDER: "ขาด/เสี่ยงขาด", NORMAL: "ปกติ", OVER: "เสี่ยงเกิน/เกิน" }[group || ""] || "กำลังรอข้อมูล");
const recommendationSlugs: Record<string, { missions: string[]; knowledge: string[] }> = {
  UNDER: { missions: ["nutrition-mission-07", "nutrition-mission-10", "nutrition-mission-09"], knowledge: ["nutrition-60plus-01", "nutrition-60plus-06", "nutrition-60plus-02"] },
  NORMAL: { missions: ["nutrition-mission-01", "nutrition-mission-05", "nutrition-mission-06"], knowledge: ["nutrition-60plus-11", "nutrition-60plus-13", "nutrition-60plus-14"] },
  OVER: { missions: ["nutrition-mission-02", "nutrition-mission-03", "nutrition-mission-08"], knowledge: ["nutrition-60plus-09", "nutrition-60plus-07", "nutrition-60plus-08"] },
};

export default function ResultPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState<ParticipantResult | null>(null);
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [resultResponse, knowledgeResponse] = await Promise.all([
          apiClient.post<ParticipantResult>(`/sansa/visit/${visitId}/participant-result`),
          apiClient.get<KnowledgeItem[]>("/knowledge"),
        ]);
        if (active) { setResult(resultResponse.data); setKnowledge(knowledgeResponse.data); }
      } catch (err: unknown) {
        const failure = err as { response?: { data?: { detail?: string } } };
        if (active) setError(failure.response?.data?.detail || "ไม่สามารถโหลดผลการประเมินได้");
      } finally { if (active) setLoading(false); }
    };
    if (visitId) void load();
    return () => { active = false; };
  }, [visitId]);

  if (loading) return <main className="min-h-screen grid place-items-center bg-teal-50"><p className="text-xl text-slate-600">กำลังคำนวณผลการประเมิน…</p></main>;
  if (error || !result) return <main className="min-h-screen grid place-items-center bg-teal-50 px-4"><section className="max-w-md rounded-3xl bg-white p-8 text-center shadow-xl"><h1 className="text-2xl font-bold text-red-700">ยังแสดงผลไม่ได้</h1><p className="mt-3 text-slate-600">{error || "ไม่พบผลการประเมิน"}</p><button onClick={() => navigate(`/bia/${visitId}`)} className="sansa-primary-button mt-6 w-full">กลับไปกรอกเส้นรอบเอว</button></section></main>;

  const group = result.predicted_group || "";
  const selected = recommendationSlugs[group];
  const missions = selected ? selected.missions.map(slug => knowledge.find(item => item.slug === slug)).filter((item): item is KnowledgeItem => Boolean(item)) : [];
  const reading = selected ? selected.knowledge.map(slug => knowledge.find(item => item.slug === slug)).filter((item): item is KnowledgeItem => Boolean(item)) : [];
  const openMedia = (item: KnowledgeItem) => item.media_path && window.open(item.media_path, "_blank", "noopener,noreferrer");

  return <main className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-cyan-50 py-8"><div className="mx-auto max-w-4xl px-4">
    <section className="rounded-3xl bg-white p-8 text-center shadow-xl"><h1 className="text-4xl font-bold text-teal-800">ผลการประเมิน SANSA</h1><p className="mt-2 text-slate-600">ขอบคุณที่ทำแบบประเมินครบถ้วน</p></section>
    <section className="mt-6 rounded-3xl border border-teal-100 bg-white p-8 text-center shadow-xl" aria-label="ผล SANSA Model 3"><p className="text-lg font-semibold text-teal-700">ผล SANSA Model 3</p>{result.ready ? <h2 className="mt-4 text-5xl font-bold text-slate-900">{groupLabel(group)}</h2> : <><h2 className="mt-4 text-3xl font-bold text-amber-700">ข้อมูลยังไม่ครบ</h2><button onClick={() => navigate(`/bia/${visitId}`)} className="sansa-primary-button mt-6">กรอกเส้นรอบเอว</button></>}</section>
    {result.ready && (missions.length > 0 || reading.length > 0) && <section className="mt-6 rounded-3xl border border-teal-100 bg-white p-6 shadow-xl" aria-label="คำแนะนำเฉพาะบุคคล">
      {missions.length > 0 && <><h3 className="mb-3 text-xl font-bold">Mission วันนี้</h3><div className="grid gap-4 sm:grid-cols-3">{missions.map(item => <button key={item.id} onClick={() => openMedia(item)} className="overflow-hidden rounded-2xl border border-teal-100 bg-teal-50 text-left hover:shadow-lg">{item.featured_image_path && <img src={item.featured_image_path} alt="" className="aspect-square w-full object-cover" />}<span className="block p-4"><strong className="block text-lg text-teal-900">{item.title.replace("MISSION วันนี้: ", "")}</strong><span className="mt-1 block text-sm text-slate-600">{item.summary}</span></span></button>)}</div></>}
      {reading.length > 0 && <><h3 className="mb-3 mt-7 text-xl font-bold">อ่านเพิ่มเติม</h3><div className="grid gap-4 sm:grid-cols-2">{reading.slice(0, 2).map(item => <button key={item.id} onClick={() => openMedia(item)} className="flex items-center gap-4 rounded-2xl border border-slate-200 p-3 text-left hover:border-teal-400">{item.featured_image_path && <img src={item.featured_image_path} alt="" className="h-24 w-24 rounded-xl object-cover" />}<strong className="text-lg">{item.title}</strong></button>)}</div></>}
    </section>}
    <div className="mt-6 grid gap-3 sm:grid-cols-2"><button onClick={() => navigate(`/satisfaction/${visitId}`)} className="sansa-primary-button py-4">ประเมินความพึงพอใจ</button><button onClick={() => navigate("/")} className="rounded-xl border-2 border-teal-700 py-4 font-bold text-teal-800">กลับหน้าหลัก</button></div>
  </div></main>;
}
