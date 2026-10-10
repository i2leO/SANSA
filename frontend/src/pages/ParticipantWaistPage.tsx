import apiClient from "@/lib/api";
import { FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function ParticipantWaistPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [waist, setWaist] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const value = Number(waist);
    if (!Number.isFinite(value) || value <= 0 || value > 300) {
      setError("กรุณากรอกเส้นรอบเอวเป็นเซนติเมตรระหว่าง 0 ถึง 300");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await apiClient.put(`/bia/visit/${visitId}/waist`, { waist_circumference_cm: value });
      navigate(`/result/${visitId}`, { replace: true });
    } catch (err: unknown) {
      const failure = err as { response?: { data?: { detail?: string } } };
      setError(failure.response?.data?.detail || "บันทึกเส้นรอบเอวไม่สำเร็จ กรุณาลองใหม่");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-teal-50 via-cyan-50 to-white py-10">
      <div className="mx-auto max-w-xl px-4">
        <section className="rounded-3xl border border-teal-100 bg-white p-7 shadow-xl">
          <div className="text-center">
            <div className="text-5xl" aria-hidden>📏</div>
            <h1 className="mt-4 text-3xl font-bold text-slate-900">วัดเส้นรอบเอว</h1>
            <p className="mt-2 text-slate-600">กรอกเส้นรอบเอวเพื่อใช้คำนวณผลประเมิน SANSA</p>
          </div>
          <div className="mt-6 rounded-2xl bg-teal-50 p-4 text-sm leading-6 text-teal-950">
            วัดบริเวณกึ่งกลางระหว่างชายโครงล่างกับขอบกระดูกสะโพก วางสายวัดให้ขนานกับพื้นและไม่รัดแน่น
          </div>
          <form onSubmit={submit} className="mt-6">
            <label htmlFor="waist" className="block text-lg font-semibold text-slate-800">เส้นรอบเอว (ซม.)</label>
            <div className="mt-2 flex overflow-hidden rounded-xl border-2 border-slate-300 focus-within:border-teal-600">
              <input id="waist" inputMode="decimal" type="number" min="0.1" max="300" step="0.1" required value={waist} onChange={(event) => setWaist(event.target.value)} className="min-w-0 flex-1 px-4 py-4 text-xl outline-none" placeholder="เช่น 85.5" />
              <span className="flex items-center bg-slate-100 px-4 font-semibold text-slate-600">ซม.</span>
            </div>
            {error && <p role="alert" className="mt-3 text-red-700">{error}</p>}
            <button disabled={busy} className="sansa-primary-button mt-6 w-full py-4 text-lg">{busy ? "กำลังบันทึก…" : "บันทึกและดูผลประเมิน"}</button>
          </form>
        </section>
      </div>
    </main>
  );
}
