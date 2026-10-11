import apiClient from "@/lib/api";
import { FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function ParticipantWaistPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [waist, setWaist] = useState("");
  const [unit, setUnit] = useState<"cm" | "inch">("cm");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const inputValue = Number(waist);
    const value = unit === "cm" ? inputValue : inputValue * 2.54;
    if (!Number.isFinite(value) || value < 40 || value > 200) {
      setError("กรุณาตรวจสอบค่าที่กรอกอีกครั้ง (40–200 ซม. หรือ 15.7–78.7 นิ้ว)");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await apiClient.put(`/bia/visit/${visitId}/waist`, {
        waist_input_value: inputValue,
        waist_input_unit: unit,
        waist_circumference_cm: Number(value.toFixed(2)),
      });
      navigate(`/result/${visitId}`, { replace: true });
    } catch (err: unknown) {
      const failure = err as { response?: { data?: { detail?: string } } };
      setError(failure.response?.data?.detail || "บันทึกเส้นรอบเอวไม่สำเร็จ กรุณาลองใหม่");
    } finally {
      setBusy(false);
    }
  };

  const changeUnit = (nextUnit: "cm" | "inch") => {
    if (nextUnit === unit) return;
    const current = Number(waist);
    if (Number.isFinite(current) && waist !== "") {
      const converted = nextUnit === "inch" ? current / 2.54 : current * 2.54;
      setWaist(converted.toFixed(1));
    }
    setUnit(nextUnit);
    setError("");
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
            วิธีการวัดเส้นรอบเอวที่ถูกต้อง คือ ใช้สายวัดรอบเอวระดับสะดือ ให้อยู่ในแนวขนานกับพื้น และไม่รัดแน่นหรือหลวมจนเกินไป
          </div>
          <form onSubmit={submit} className="mt-6">
            <fieldset className="mb-4"><legend className="text-lg font-semibold text-slate-800">หน่วย</legend><div className="mt-2 grid grid-cols-2 gap-2">{(["cm", "inch"] as const).map(value => <button key={value} type="button" onClick={() => changeUnit(value)} className={`rounded-xl border-2 px-4 py-3 font-bold ${unit === value ? "border-teal-600 bg-teal-50 text-teal-800" : "border-slate-200"}`}>{value === "cm" ? "เซนติเมตร" : "นิ้ว"}</button>)}</div></fieldset>
            <label htmlFor="waist" className="block text-lg font-semibold text-slate-800">เส้นรอบเอว ({unit === "cm" ? "ซม." : "นิ้ว"})</label>
            <div className="mt-2 flex overflow-hidden rounded-xl border-2 border-slate-300 focus-within:border-teal-600">
              <input id="waist" inputMode="decimal" type="number" min={unit === "cm" ? 40 : 15.7} max={unit === "cm" ? 200 : 78.7} step="0.1" required value={waist} onChange={(event) => setWaist(event.target.value)} className="min-w-0 flex-1 px-4 py-4 text-xl outline-none" placeholder={unit === "cm" ? "เช่น 85.5" : "เช่น 33.7"} />
              <span className="flex items-center bg-slate-100 px-4 font-semibold text-slate-600">{unit === "cm" ? "ซม." : "นิ้ว"}</span>
            </div>
            {error && <p role="alert" className="mt-3 text-red-700">{error}</p>}
            <button disabled={busy} className="sansa-primary-button mt-6 w-full py-4 text-lg">{busy ? "กำลังบันทึก…" : "บันทึกและดูผลประเมิน"}</button>
          </form>
        </section>
      </div>
    </main>
  );
}
