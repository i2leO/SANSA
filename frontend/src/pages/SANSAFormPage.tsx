import apiClient from "@/lib/api";
import QuestionImage from "@/components/QuestionImage";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm, type UseFormRegister } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

const fields = [
  "q1_weight_change", "q2_food_intake", "q3_daily_activities", "q4_chronic_disease",
  "q5_meals_per_day", "q6_portion_size", "q7_food_texture", "q8_rice_starch",
  "q9_protein", "q10_milk", "q11_fruits", "q12_vegetables", "q13_water",
  "q14_sweet_drinks", "q15_cooking_method", "q16_oil_coconut",
] as const;

const sansaSchema = z.object(Object.fromEntries(fields.map((field) => [field, z.string().min(1)])) as {
  [K in (typeof fields)[number]]: z.ZodString;
});
type SANSAForm = z.infer<typeof sansaSchema>;

type InstrumentOption = { value: string; label: string; score: number };
type InstrumentQuestion = {
  number: number;
  field: (typeof fields)[number];
  label: string;
  domain: "screening" | "d1" | "d2" | "d3";
  included_in_model: boolean;
  options: InstrumentOption[];
};
type InstrumentDefinition = {
  definition_version: string;
  source: string;
  questions: InstrumentQuestion[];
};

function Question({ question, register }: {
  question: InstrumentQuestion;
  register: UseFormRegister<SANSAForm>;
}) {
  const useRadio = question.number <= 4;
  return (
    <div className="mb-8">
      <label className="block text-gray-800 font-bold text-lg mb-3">
        {question.number}. {question.label}
      </label>
      {question.number >= 5 && <QuestionImage number={question.number} alt={question.label} />}
      {useRadio ? (
        <div className="space-y-2">
          {question.options.map((option) => (
            <label key={option.value} className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-green-400 cursor-pointer">
              <input type="radio" value={option.value} {...register(question.field)} className="w-5 h-5 text-green-600" />
              <span className="ml-3 text-gray-700">{option.label}</span>
            </label>
          ))}
        </div>
      ) : (
        <select {...register(question.field)} className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl">
          <option value="">เลือก...</option>
          {question.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      )}
    </div>
  );
}

export default function SANSAFormPage() {
  const { respondentCode } = useParams();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [definition, setDefinition] = useState<InstrumentDefinition | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit } = useForm<SANSAForm>({ resolver: zodResolver(sansaSchema) });

  useEffect(() => {
    let active = true;
    apiClient.get<InstrumentDefinition>("/sansa/definition")
      .then(({ data }) => { if (active) setDefinition(data); })
      .catch(() => { if (active) setError("โหลดนิยามแบบประเมินไม่สำเร็จ กรุณาแจ้งเจ้าหน้าที่"); });
    return () => { active = false; };
  }, []);

  const onSubmit = async (data: SANSAForm) => {
    setSaving(true);
    setError(null);
    try {
      const { data: respondent } = await apiClient.get(`/respondents/${respondentCode}`);
      const { data: visits } = await apiClient.get(`/visits/respondent/${respondent.id}`);
      let visit = visits[0];
      if (!visit) {
        const response = await apiClient.post("/visits", {
          respondent_id: respondent.id,
          visit_number: 1,
          visit_date: new Date().toISOString().split("T")[0],
          visit_type: "baseline",
        });
        visit = response.data;
      }
      try {
        await apiClient.post("/sansa", { visit_id: visit.id, ...data });
      } catch (requestError: unknown) {
        const detail = (requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail || "";
        if (detail.toLowerCase().includes("already exists")) {
          throw new Error("รอบนี้มีแบบประเมิน SANSA แล้ว คำตอบที่กรอกครั้งนี้ยังไม่ได้บันทึก กรุณาเปิดผลเดิมหรือติดต่อเจ้าหน้าที่เพื่อแก้ไข");
        }
        throw requestError;
      }
      navigate(`/bia/${visit.id}`);
    } catch (requestError: unknown) {
      const detail = (requestError as { response?: { data?: { detail?: unknown } } }).response?.data?.detail;
      setError(typeof detail === "string" ? detail : requestError instanceof Error ? requestError.message : "ไม่สามารถบันทึกข้อมูลได้");
    } finally {
      setSaving(false);
    }
  };

  const screening = definition?.questions.filter((question) => question.domain === "screening") ?? [];
  const sections = [
    { domain: "d1", title: "ส่วนที่ 2: พฤติกรรมการกินทั่วไป (D1)", note: "เก็บเพื่อวิเคราะห์และรายงาน ไม่ใช้ใน Model 3" },
    { domain: "d2", title: "ส่วนที่ 3: พฤติกรรมการกินตามธงโภชนาการ (D2)", note: "ใช้เป็นตัวแปรใน Model 3" },
    { domain: "d3", title: "ส่วนที่ 4: พฤติกรรมหวานและมัน (D3)", note: "ใช้เป็นตัวแปรใน Model 3" },
  ] as const;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100 py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-600 rounded-2xl flex items-center justify-center"><span className="text-3xl">🥗</span></div>
            <div><h1 className="text-4xl font-bold text-gray-800">แบบประเมิน SANSA</h1><p className="text-gray-600 mt-1">Self-administered Nutrition Screening and Assessment</p></div>
          </div>
          <div className="border-t border-gray-200 pt-4 mt-4"><p className="text-gray-700">รหัสผู้เข้าร่วม: <span className="font-mono font-bold text-green-600 text-xl">{respondentCode}</span></p></div>
        </div>

        {error && <div className="mb-6 p-5 bg-red-50 border-l-4 border-red-500 rounded-lg"><p className="text-red-700 font-medium">{error}</p></div>}
        {!definition && !error && <div className="bg-white rounded-2xl shadow-xl p-8 text-gray-600">กำลังโหลดแบบประเมิน...</div>}

        {definition && <form onSubmit={handleSubmit(onSubmit, () => setError("กรุณาตอบแบบประเมินให้ครบทั้ง 16 ข้อ"))} className="space-y-6">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-green-700 mb-6 pb-3 border-b-2 border-green-200">ส่วนที่ 1: คัดกรอง (Screening)</h2>
            {screening.map((question) => <Question key={question.field} question={question} register={register} />)}
          </div>
          {sections.map(section => <div key={section.domain} className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-green-700">{section.title}</h2>
            <p className="mb-6 mt-2 border-b-2 border-green-200 pb-3 text-slate-600">{section.note}</p>
            {definition.questions.filter(question => question.domain === section.domain).map(question => <Question key={question.field} question={question} register={register} />)}
          </div>)}
          <div className="bg-white rounded-2xl shadow-xl p-6"><div className="flex gap-4">
            <button type="button" onClick={() => navigate(-1)} className="flex-1 py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-bold text-lg">← ย้อนกลับ</button>
            <button type="submit" disabled={saving} className="flex-1 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl hover:from-green-700 hover:to-teal-700 disabled:from-gray-400 disabled:to-gray-400 font-bold text-lg shadow-lg">{saving ? "กำลังบันทึก..." : "ดำเนินการต่อ →"}</button>
          </div></div>
        </form>}

        <div className="mt-8 text-center text-gray-600"><p className="text-sm">ขั้นตอนที่ 2 จาก 3 | แบบประเมิน SANSA</p><div className="mt-2 w-full bg-gray-200 rounded-full h-2"><div className="bg-gradient-to-r from-green-600 to-teal-600 h-2 rounded-full" style={{ width: "66%" }} /></div></div>
      </div>
    </div>
  );
}
