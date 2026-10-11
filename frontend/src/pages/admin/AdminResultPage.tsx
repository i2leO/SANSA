import apiClient from "@/lib/api";
import { demographicOptions, displayResearchValue, sansaQuestions } from "@/lib/researchLabels";
import MNAAssessmentPage from "@/pages/MNAAssessmentPage";
import BIAMeasurementPage from "@/pages/BIAMeasurementPage";
import AdminLayout from "@/pages/admin/AdminLayout";
import { Fragment, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type Row = Record<string, unknown>;
type Load = { data: Row | null; status: "loading" | "ok" | "missing" | "error" };

type InstrumentQuestion = { number: number; field: string; label: string; domain: string; options: { value: string; label: string; score: number }[] };
type MNAQuestion = { letter: string; field: string; label: string; options: { value: string; label: string; score: number | string }[] };
type AssessmentRevision = { id: number; instrument: string; revision_number: number; action_type: string; snapshot: Row; changed_by: number | null; change_reason: string | null; is_current: boolean; recorded_at: string };
const fallbackQuestions: InstrumentQuestion[] = sansaQuestions.map(([field, label], index) => ({
  number: index + 1,
  field,
  label,
  domain: index < 4 ? "screening" : index < 7 ? "d1" : index < 13 ? "d2" : "d3",
  options: [],
}));
const sexLabel = demographicOptions.sex;
const statusLabel = demographicOptions.status;
const predictionLabel: Row = { UNDER: "เสี่ยงขาด", NORMAL: "ปกติ", OVER: "เสี่ยงเกิน/เกิน" };
const questionGroups: Record<number, string> = {
  0: 'คัดกรองเบื้องต้น (ข้อมูลประกอบ ไม่ใช้ใน Model 3)',
  4: 'พฤติกรรมการกินพื้นฐาน D1 (ข้อมูลประกอบ ไม่ใช้ใน Model 3)',
  7: 'ธงโภชนาการ D2',
  13: 'พฤติกรรมหวานและมัน D3',
};
const scoreColor = (value: unknown) => {
  const score = Number(value);
  if (score === 0) return 'text-blue-700';
  if (score === 4) return 'text-orange-700';
  return 'text-emerald-700';
};
const scoreBucketLabel = (question: InstrumentQuestion, score: unknown) => {
  const numericScore = Number(score);
  if (!Number.isFinite(numericScore)) return "—";
  const labels = [...new Set(question.options.filter(option => Number(option.score) === numericScore).map(option => option.label))];
  return labels.length > 0 ? `กลุ่ม ${numericScore} คะแนน: ${labels.join(" / ")}` : "ไม่พบกลุ่มคำตอบนี้ในนิยามที่อนุมัติ";
};
const show = (row: Row | null, key: string) => {
  const value = row?.[key]; return value === null || value === undefined || value === "" ? "-" : String(value);
};
const percent = (value: unknown) => value == null ? "—" : `${(Number(value) * 100).toFixed(1)}%`;
const predictionText = (value: unknown) => String(predictionLabel[String(value)] ?? value ?? "รอข้อมูลครบ");
const integrityMessages: Record<string, string> = {
  missing_raw_answers: "ข้อมูลเดิมไม่มีคำตอบดิบครบ 16 ข้อ จึงยังยืนยันคะแนนตามเกณฑ์ 0/2/4 ไม่ได้",
  invalid_raw_answers: "พบคำตอบที่ไม่อยู่ในนิยามแบบประเมิน 0/2/4 ที่อนุมัติ",
  score_definition_mismatch: "คะแนนที่บันทึกไว้ไม่ตรงกับคำตอบตามนิยาม 0/2/4 กรุณาตรวจสอบก่อนใช้ผล",
  scoring_version_mismatch: "ข้อมูลชุดนี้ไม่ได้บันทึกด้วยนิยาม 0/2/4 เวอร์ชันที่เปิดใช้งาน",
  missing_prediction_scores: "คะแนน D2 หรือ D3 ไม่ครบ จึงยังคำนวณ Model 3 ไม่ได้",
  missing_bia: "ยังไม่มีข้อมูล BIA สำหรับ Visit นี้",
  ambiguous_bia: "พบข้อมูล BIA มากกว่าหนึ่งชุด จึงไม่เลือกชุดใดโดยอัตโนมัติ",
  missing_age: "ยังไม่มีอายุสำหรับคำนวณ Model 3",
  missing_waist: "ยังไม่มีรอบเอวสำหรับคำนวณ Model 3",
  invalid_waist: "ค่ารอบเอวไม่ถูกต้อง",
  missing_reference_inputs: "ข้อมูล BMI หรือเปอร์เซ็นต์ไขมันยังไม่ครบสำหรับผลอ้างอิง",
};
function OptionalSection({ state, children, missing }: { state: Load; children: React.ReactNode; missing: string }) {
  if (state.status === "loading") return <p className="p-4 text-slate-500">กำลังโหลด...</p>;
  if (state.status === "error") return <p className="rounded-xl bg-red-50 p-4 text-red-700">โหลดข้อมูลส่วนนี้ไม่สำเร็จ</p>;
  if (!state.data) return <p className="rounded-xl bg-slate-50 p-4 text-slate-500">{missing}</p>;
  return <>{children}</>;
}

export default function AdminResultPage() {
  const { visitId } = useParams(); const navigate = useNavigate();
  const blank: Load = { data: null, status: "loading" };
  const [visit,setVisit]=useState<Row|null>(null),[person,setPerson]=useState<Row|null>(null);
  const [sansa,setSansa]=useState<Load>(blank),[bia,setBia]=useState<Load>(blank),[mna,setMna]=useState<Load>(blank);
  const [questions, setQuestions] = useState<InstrumentQuestion[]>(fallbackQuestions);
  const [mnaQuestions, setMnaQuestions] = useState<MNAQuestion[]>([]);
  const [revisions, setRevisions] = useState<AssessmentRevision[]>([]);
  const [definitionWarning, setDefinitionWarning] = useState<string | null>(null);
  const [error,setError]=useState<string|null>(null);
  const [revision, setRevision] = useState(0);
  const refreshResults = () => setRevision(value => value + 1);

  useEffect(() => {
    if (!visitId) return;
    let active = true;
    setError(null); setVisit(null); setPerson(null);
    setSansa({ data: null, status: 'loading' }); setBia({ data: null, status: 'loading' }); setMna({ data: null, status: 'loading' });
    setRevisions([]);
    const optional = async (path: string, set: (value: Load) => void) => {
      try {
        const response = await apiClient.get<Row>(path);
        if (active) set({ data: response.data, status: 'ok' });
      } catch (e: unknown) {
        if (active) set({ data: null, status: (e as { response?: { status?: number } }).response?.status === 404 ? 'missing' : 'error' });
      }
    };
    const loadPerson = async () => {
      try {
        const response = await apiClient.get<Row>(`/visits/${visitId}`);
        if (!active) return;
        setVisit(response.data);
        const respondent = await apiClient.get<Row>(`/respondents/id/${response.data.respondent_id}`);
        if (active) setPerson(respondent.data);
      } catch { if (active) setError('โหลดข้อมูลผู้เข้าร่วมไม่สำเร็จ'); }
    };
    const loadDefinition = async () => {
      try {
        const response = await apiClient.get<{ questions: InstrumentQuestion[] }>("/sansa/definition");
        if (active && response.data.questions.length === 16) {
          setQuestions(response.data.questions);
          setDefinitionWarning(null);
        }
      } catch {
        if (active) {
          setQuestions(fallbackQuestions);
          setDefinitionWarning('กำลังใช้หัวข้อสำรอง เนื่องจาก backend ยังไม่ได้โหลดนิยามแบบประเมินที่อนุมัติ');
        }
      }
    };
    const loadMnaDefinition = async () => {
      try {
        const response = await apiClient.get<{ items: MNAQuestion[] }>("/mna/definition");
        if (active) setMnaQuestions(response.data.items);
      } catch {
        if (active) setMnaQuestions([]);
      }
    };
    const loadRevisions = async () => {
      try { const response = await apiClient.get<AssessmentRevision[]>(`/assessment-history/visit/${visitId}/revisions`); if (active) setRevisions(response.data); }
      catch { if (active) setRevisions([]); }
    };
    void Promise.all([loadPerson(), loadDefinition(), loadMnaDefinition(), loadRevisions(), optional(`/sansa/visit/${visitId}`, setSansa), optional(`/bia/visit/${visitId}`, setBia), optional(`/mna/visit/${visitId}`, setMna)]);
    return () => { active = false; };
  }, [visitId, revision]);

  const revised=sansa.data?.revised as {domain_scores?:Row;prediction?:Row;reference?:Row;verified_024?:boolean;issues?:string[];missing_answer_fields?:string[]} | undefined;
  const prediction=revised?.prediction; const domains=revised?.domain_scores;
  const isRevised4ScoreOnly = sansa.data?.source_dataset === "revised4" && sansa.data?.answer_capture_mode === "score_only";
  const resultIssues=(revised?.issues??[]).map(code=>integrityMessages[code]??`ต้องตรวจสอบข้อมูล: ${code}`);
  const anchors=[["calculation","ผลการคำนวณ"],["bia","บันทึก BIA"],["mna","บันทึก MNA"],["general","ข้อมูลทั่วไป"],["answers","คำตอบ SANSA"],["mna-answers","คำตอบ MNA"],["history","ประวัติการแก้ไข"]];
  return <AdminLayout title="รายละเอียดการประเมิน"><main className="mx-auto max-w-5xl space-y-5 text-slate-800">
    <button onClick={()=>navigate('/admin/respondents')} className="font-semibold text-slate-600">‹ รายชื่อทั้งหมด</button>
    {error&&<p className="rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}

    <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
      <div className="flex items-start gap-5"><div className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-xl font-bold text-emerald-700">ID</div><div className="min-w-0 flex-1"><p className="text-sm font-medium text-slate-500">รหัสผู้เข้าร่วม</p><h1 className="break-all font-mono text-3xl font-bold">{show(person,'respondent_code')}</h1><p className="mt-1 text-lg text-slate-600">{show(person,'age')} ปี · {String(sexLabel[show(person,'sex')]??show(person,'sex'))} · {String(statusLabel[show(person,'status')]??show(person,'status'))}</p><p className="text-slate-500">Visit {visitId} · ประเมินเมื่อ {show(visit,'visit_date')}</p></div></div>
      {resultIssues.length>0&&<div className="mt-6 rounded-2xl border border-amber-300 bg-amber-50 p-5 text-amber-950"><p className="font-bold">ข้อมูลส่วนที่ยังไม่สมบูรณ์</p><ul className="mt-2 list-disc space-y-1 pl-5">{resultIssues.map(message=><li key={message}>{message}</li>)}</ul></div>}
      <div className="mt-7 rounded-2xl border-l-[6px] border-blue-600 bg-blue-50/50 p-6"><p className="text-lg">ผลทำนาย SANSA Model 3</p><p className="mt-1 text-4xl font-bold text-blue-700">{predictionText(prediction?.predicted_group)}</p><div className="mt-5 flex flex-wrap gap-x-12 gap-y-2"><span>เสี่ยงขาด <b>{percent(prediction?.p_under)}</b></span><span>ปกติ <b>{percent(prediction?.p_normal)}</b></span><span>เสี่ยงเกิน/เกิน <b>{percent(prediction?.p_over)}</b></span></div>{revised?.verified_024&&<p className="mt-4 text-sm font-semibold text-emerald-700">ตรวจสอบข้อมูลและคะแนนครบตามนิยาม 0/2/4 แล้ว</p>}</div>
    </section>

    <nav className="sticky top-0 z-10 flex gap-2 overflow-x-auto rounded-2xl border bg-white p-2 shadow-sm">{anchors.map(([id,label])=><a key={id} href={`#${id}`} className="whitespace-nowrap rounded-xl px-4 py-3 font-bold text-slate-600 hover:bg-emerald-50 hover:text-emerald-800">{label}</a>)}</nav>

    <section id="calculation" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm"><h2 className="text-2xl font-bold">ตัวแปรในสมการทำนาย</h2><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[["D2",show(domains??null,'d2_total'),"/ 20 ธงโภชนาการ 6 ข้อ"],["D3",show(domains??null,'d3_total'),"/ 12 หวาน มัน 3 ข้อ"],["wc_cm",show(bia.data,'waist_circumference_cm'),"ซม. รอบเอว"],["AgeGroup01",show(prediction??null,'age_group01'),"กลุ่มอายุ"],["D1",show(domains??null,'d1_total'),"ข้อมูลประกอบ ไม่ใช้ใน Model 3"]].map(([label,value,note])=><div key={label} className="rounded-2xl border border-emerald-100 p-5"><b className="text-emerald-700">{label}</b><p className="text-4xl font-bold">{value}</p><p className="text-slate-500">{note}</p></div>)}</div>{prediction&&<p className="mt-5 text-slate-600">L_Over = {show(prediction,'l_over')} &nbsp; L_Normal = {show(prediction,'l_normal')}</p>}<div className="mt-5 grid gap-4 border-t pt-5 sm:grid-cols-2"><div><span className="text-slate-500">ผล SANSA</span><p className="text-xl font-bold text-blue-700">{prediction?predictionText(prediction.predicted_group):'รอข้อมูล'}</p></div><div><span className="text-slate-500">เกณฑ์อ้างอิง (BMI + %ไขมัน)</span><p className="text-xl font-bold">{revised?.reference?predictionText(revised.reference.nutrition_reference):'รอข้อมูล BIA'}</p></div></div></section>

    <section id="bia" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm"><BIAMeasurementPage staffMode embedded onSaved={refreshResults} /></section>

    <section id="mna" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm"><MNAAssessmentPage staffMode embedded onSaved={refreshResults} /></section>

    <section id="general" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm"><h2 className="text-2xl font-bold">ข้อมูลทั่วไป</h2><div className="mt-5 grid gap-x-8 gap-y-5 sm:grid-cols-2">{[["สถานะผู้ตอบ",String(statusLabel[show(person,'status')]??show(person,'status'))],["อายุ / เพศ",`${show(person,'age')} ปี / ${String(sexLabel[show(person,'sex')]??show(person,'sex'))}`],["ระดับการศึกษา",displayResearchValue('education_level', person?.education_level)],["สถานภาพสมรส",displayResearchValue('marital_status', person?.marital_status)],["รายได้ต่อเดือน",displayResearchValue('monthly_income', person?.monthly_income)],["แหล่งรายได้",displayResearchValue('income_sources', person?.income_sources)],["โรคประจำตัว",displayResearchValue('chronic_diseases', person?.chronic_diseases)],["อาศัยอยู่กับ",displayResearchValue('living_arrangement', person?.living_arrangement)],["เบอร์โทรศัพท์",show(person,'phone')]].map(([label,value])=><div key={label} className="border-b border-emerald-100 pb-3"><p className="text-slate-500">{label}</p><p className="text-lg font-bold">{value}</p></div>)}</div></section>

    <section id="answers" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
      <h2 className="text-2xl font-bold">ข้อมูลรายข้อ SANSA</h2>
      {definitionWarning&&<p className="mt-3 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">{definitionWarning}</p>}
      {isRevised4ScoreOnly&&<div className="mt-3 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-950">
        <p className="font-bold">ชุดข้อมูล revised4 เก็บคะแนนรายข้อ แต่ไม่ได้เก็บตัวเลือกดิบที่ผู้เข้าร่วมกด</p>
        <p className="mt-1">ระบบจะแสดงกลุ่มคำตอบ 0/2/4 ตามตารางในไฟล์ EDIT SANSA ONLINE จากคะแนนต้นทาง โดยไม่กล่าวอ้างว่าเป็นตัวเลือกย่อยใดตัวเลือกหนึ่งเมื่อหลายคำตอบได้คะแนนเท่ากัน</p>
      </div>}
      {!isRevised4ScoreOnly&&revised?.missing_answer_fields&&revised.missing_answer_fields.length>0&&<p className="mt-3 rounded-xl bg-amber-50 p-3 text-sm text-amber-900">ข้อมูลการประเมินขาดคำตอบดิบ {revised.missing_answer_fields.length} ข้อ จึงไม่สามารถยืนยันคะแนนตามนิยาม 0/2/4 ได้</p>}
      <OptionalSection state={sansa} missing="ยังไม่มีข้อมูล SANSA">
        <div className="mt-5 overflow-x-auto rounded-xl border"><table className="w-full min-w-[780px] text-left"><thead className="bg-slate-50 text-slate-600"><tr><th className="w-16 p-4">ข้อ</th><th className="p-4">ข้อคำถามตามไฟล์ EDIT</th><th className="p-4">{isRevised4ScoreOnly ? "ผลตามกลุ่มคะแนนในไฟล์ EDIT" : "ตัวเลือกที่ผู้เข้าร่วมตอบ"}</th><th className="w-28 p-4 text-right">คะแนน</th></tr></thead><tbody className="divide-y">{questions.map((question,i)=>{const raw=sansa.data?.[question.field];const score=show(sansa.data,`q${question.number}_score`);const answer=isRevised4ScoreOnly?scoreBucketLabel(question,score):question.options.find(option=>option.value===raw)?.label??displayResearchValue(question.field,raw);return <Fragment key={question.field}>{questionGroups[i]&&<tr className="bg-emerald-50/60"><td colSpan={4} className="p-4 font-bold text-emerald-800">{questionGroups[i]}</td></tr>}<tr><td className="p-4 align-top">{question.number}</td><td className="p-4 align-top">{question.label}</td><td className="p-4 align-top font-medium">{answer}</td><td className={`p-4 text-right align-top font-bold ${revised?.verified_024?scoreColor(sansa.data?.[`q${question.number}_score`]):"text-slate-400"}`}>{score}</td></tr></Fragment>})}</tbody></table></div>
      </OptionalSection>
    </section>
    <section id="mna-answers" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
      <h2 className="text-2xl font-bold">คำตอบ MNA รายข้อ A–R</h2>
      <OptionalSection state={mna} missing="ยังไม่มีข้อมูล MNA">
        {mnaQuestions.length !== 18 ? (
          <p className="mt-4 rounded-xl bg-red-50 p-4 text-red-700">โหลดนิยามคำตอบ MNA ไม่สำเร็จ</p>
        ) : (
          <div className="mt-5 overflow-x-auto rounded-xl border">
            <table className="w-full min-w-[760px] text-left">
              <thead className="bg-slate-50 text-slate-600"><tr><th className="w-16 p-4">ข้อ</th><th className="p-4">รายการ</th><th className="p-4">คำตอบที่บันทึก</th><th className="w-28 p-4 text-right">คะแนน</th></tr></thead>
              <tbody className="divide-y">
                {mnaQuestions.map((question, index) => {
                  const raw = mna.data?.[question.field];
                  const scoreField = index < 6 ? `mna_s${index + 1}` : `mna_a${index - 5}`;
                  const score = show(mna.data, scoreField);
                  const scoreOnly = mna.data?.answer_capture_mode === 'score_only';
                  const answer = scoreOnly
                    ? `ไม่ได้บันทึกคำตอบดิบ (คะแนนต้นทาง ${score})`
                    : question.options.find(option => option.value === raw)?.label ?? displayResearchValue(question.field, raw);
                  return <Fragment key={question.field}>
                    {(index === 0 || index === 6) && <tr className="bg-emerald-50/60"><td colSpan={4} className="p-4 font-bold text-emerald-800">{index === 0 ? 'ส่วนคัดกรอง A–F' : 'ส่วนประเมิน G–R'}</td></tr>}
                    <tr><td className="p-4 font-bold">{question.letter}</td><td className="p-4">{question.label}</td><td className="p-4 font-medium">{answer}</td><td className="p-4 text-right font-bold text-emerald-700">{score}</td></tr>
                  </Fragment>;
                })}
              </tbody>
            </table>
          </div>
        )}
      </OptionalSection>
    </section>
    <section id="history" className="scroll-mt-20 rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
      <h2 className="text-2xl font-bold">ประวัติการบันทึก SANSA / MNA / BIA</h2>
      <p className="mt-2 text-slate-600">แต่ละ revision เป็น snapshot ที่เก็บเพิ่มและไม่เขียนทับข้อมูลก่อนหน้า</p>
      {revisions.length===0?<p className="mt-4 rounded-xl bg-slate-50 p-4 text-slate-500">ข้อมูลเดิมยังไม่มี revision; ระบบจะสร้าง baseline เมื่อมีการแก้ครั้งถัดไป</p>:<div className="mt-5 space-y-4">{revisions.map(revision=><details key={revision.id} className="rounded-xl border p-4" open={revision.is_current}><summary className="cursor-pointer font-bold">{revision.instrument} revision {revision.revision_number} · {revision.action_type} {revision.is_current?'· ปัจจุบัน':''}<span className="ml-3 font-normal text-slate-500">{revision.recorded_at}</span></summary><p className="mt-2 text-sm text-slate-600">ผู้บันทึก: {revision.changed_by??'ระบบ/ข้อมูลนำเข้า'}{revision.change_reason?` · เหตุผล: ${revision.change_reason}`:''}</p><div className="mt-3 grid gap-2 sm:grid-cols-2">{Object.entries(revision.snapshot).map(([key,value])=><div key={key} className="border-b py-2"><span className="text-xs text-slate-500">{key}</span><p className="break-all font-mono text-sm">{value==null?'—':typeof value==='object'?JSON.stringify(value):String(value)}</p></div>)}</div></details>)}</div>}
    </section>
  </main></AdminLayout>;
}
