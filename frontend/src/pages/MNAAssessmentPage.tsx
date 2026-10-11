import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import apiClient from '@/lib/api';

type Item = { letter: string; field: string; label: string; options: { value: string; label: string; score: number | string }[] };
type CurrentMNAResult = {
  available: boolean;
  source: 'imported_scores' | 'recorded_answers';
  has_raw_answers: boolean;
  has_item_scores: boolean;
  screening_total: string | number | null;
  assessment_total: string | number | null;
  total: string | number | null;
  category: string | null;
  category_code: string | null;
  category_label: string | null;
  integrity_status: 'verified' | 'partial' | 'missing';
  issues: string[];
};
type SavedAssessment = {
  mna_screen_total: string | number | null;
  mna_total: string | number | null;
  scoring_version_id: number;
  history_requires_review: boolean;
  source_dataset: string;
  answer_capture_mode: 'score_only' | 'raw_answers';
  current_result: CurrentMNAResult | null;
};

export default function MNAAssessmentPage({ staffMode = false, embedded = false, onSaved }: { staffMode?: boolean; embedded?: boolean; onSaved?: () => void }) {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [items, setItems] = useState<Item[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [recordId, setRecordId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const [filling, setFilling] = useState(false);
  const [fillNotice, setFillNotice] = useState('');
  const [history, setHistory] = useState<SavedAssessment | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(''); setSaved(false); setFillNotice('');
    setItems([]); setAnswers({}); setRecordId(null);
    setHistory(null);
    const load = async () => {
      try {
        const [definition, record] = await Promise.all([
          apiClient.get<{ items: Item[] }>('/mna/definition'),
          apiClient.get(`/mna/visit/${visitId}`).catch(e => {
            if (e.response?.status === 404) return null;
            throw e;
          }),
        ]);
        if (!active) return;
        setItems(definition.data.items);
        setRecordId(record?.data.id ?? null);
        setHistory(record?.data ?? null);
        setAnswers(Object.fromEntries(definition.data.items.map(item => [item.field, record?.data[item.field] ?? ''])));
      } catch { if (active) setError('โหลดแบบประเมินไม่สำเร็จ กรุณาลองใหม่'); }
      finally { if (active) setLoading(false); }
    };
    void load();
    return () => { active = false; };
  }, [visitId]);

  const selected = items.map(item => item.options.find(option => option.value === answers[item.field]));
  const complete = items.length === 18 && selected.every(Boolean);
  const screeningComplete = items.length === 18 && selected.slice(0, 6).every(Boolean);
  const editingStarted = selected.some(Boolean);
  const sum = (start: number, end: number) => selected.slice(start, end).reduce((total, option) => total + Number(option?.score ?? 0), 0);

  const fillFromBia = async () => {
    setFilling(true); setFillNotice('');
    try {
      const { data } = await apiClient.get<{ answers: Record<string, string> }>(`/mna/visit/${visitId}/bia-suggestions`);
      setAnswers(previous => ({ ...previous, ...data.answers }));
      setSaved(false);
      setFillNotice(`เติมได้ ${Object.keys(data.answers).length} จาก 3 ข้อ จาก BIA ที่บันทึกแล้ว กรุณาตรวจสอบก่อนบันทึก MNA; ช่องที่ไม่มีค่าจะไม่ถูกเปลี่ยน`);
    } catch { setFillNotice('เติมค่าไม่ได้ กรุณาตรวจว่ามีการบันทึก BIA แล้ว'); }
    finally { setFilling(false); }
  };

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!complete) {
      const answered = selected.filter(Boolean).length;
      setError(`กรุณาตอบแบบประเมิน MNA ให้ครบ 18 ข้อก่อนบันทึก (ตอบแล้ว ${answered} ข้อ)`);
      return;
    }
    if (saving || history?.history_requires_review) return;
    setSaving(true); setError('');
    try {
      const response = recordId !== null
        ? await apiClient.put(`/mna/${recordId}`, answers)
        : await apiClient.post('/mna', { visit_id: Number(visitId), ...answers });
      setRecordId(response.data.id);
      setHistory(response.data);
      setSaved(true);
      if (embedded) onSaved?.();
      else navigate(staffMode ? `/admin/results/${visitId}` : `/bia/${visitId}`);
    } catch (e: unknown) {
      const detail = (e as { response?: { data?: { detail?: unknown } } }).response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'บันทึกไม่สำเร็จ ข้อมูลในฟอร์มยังอยู่ กรุณาตรวจสอบและลองใหม่');
    } finally { setSaving(false); }
  };

  return <div className={embedded ? '' : 'mx-auto max-w-4xl p-6'}>
    {!embedded && <button type="button" onClick={() => navigate(-1)} className="mb-5 text-primary-700">← กลับ</button>}
    <h2 className="text-2xl font-bold">ผลและการบันทึก MNA</h2>
    {saved && <p role="status" className="my-3 text-emerald-700">บันทึก MNA แล้ว</p>}
    {error && <p role="alert" className="my-4 rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}
    {history?.current_result?.available && <div className="my-4 rounded-2xl border border-emerald-200 bg-emerald-50/60 p-5 text-slate-800">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><p className="font-bold text-emerald-900">ผล MNA ปัจจุบัน</p><p className="mt-1 text-2xl font-bold">{history.current_result.category_label ?? 'มีคะแนน MNA แล้ว'}</p></div>
        <span className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-emerald-800">{history.current_result.source === 'imported_scores' ? 'ข้อมูลนำเข้า revised4' : 'คำตอบที่เจ้าหน้าที่บันทึก'}</span>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <p>คัดกรอง A–F<strong className="block text-2xl">{history.current_result.screening_total ?? '—'} / 14</strong></p>
        <p>ประเมิน G–R<strong className="block text-2xl">{history.current_result.assessment_total ?? '—'} / 16</strong></p>
        <p>คะแนนรวม<strong className="block text-2xl">{history.current_result.total ?? '—'} / 30</strong></p>
      </div>
      {history.current_result.source === 'imported_scores' && <p className="mt-4 rounded-xl bg-blue-50 p-3 text-sm text-blue-950">ผลนี้คำนวณและแสดงจากคะแนนรายข้อที่มีอยู่ใน revised4 ไม่ต้องบันทึก MNA ซ้ำ ข้อมูลต้นทางไม่มีตัวเลือกคำตอบดิบ A–R จึงไม่เติมคำตอบย้อนหลังให้เอง</p>}
      {history.current_result.integrity_status !== 'verified' && <p role="alert" className="mt-3 text-sm text-amber-800">ข้อมูลคะแนนปัจจุบันแสดงได้ แต่มีจุดที่ต้องตรวจสอบ: {history.current_result.issues.join(', ') || 'คะแนนรายข้อไม่ครบ'}</p>}
      {history.history_requires_review && <p role="alert" className="mt-2 text-amber-800">ข้อมูลเดิมต้องให้ผู้ดูแลตรวจสอบเวอร์ชันคะแนนก่อน จึงยังแก้ไขรายการนี้ไม่ได้</p>}
    </div>}
    {loading ? <p>กำลังโหลด...</p> : items.length > 0 && <form onSubmit={save} noValidate>
      <div className="my-6 rounded-2xl border p-5">
        <p className="font-bold">บันทึกคำตอบใหม่หรือแก้ไขผลปัจจุบัน</p>
        {!editingStarted ? <p className="mt-2 text-sm text-slate-600">แบบฟอร์มนี้ใช้เมื่อเจ้าหน้าที่ต้องการบันทึกคำตอบ A–R ใหม่ ผล MNA ปัจจุบันด้านบนจะไม่เปลี่ยนจนกว่าจะตอบครบและกดบันทึก</p> : <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <p className="text-sm text-slate-500 sm:col-span-3">ผลคำนวณจากคำตอบที่กำลังกรอก (ยังไม่บันทึก)</p>
          <p>คะแนนคัดกรอง (A–F)<strong className="block text-2xl">{screeningComplete ? sum(0, 6) : '—'} / 14</strong></p>
          <p>คะแนนรวม<strong className="block text-2xl">{complete ? sum(0, 18) : '—'} / 30</strong></p>
          <p>ตอบแล้ว {selected.filter(Boolean).length} จาก 18 ข้อ</p>
        </div>}
      </div>
      {items.map((item, index) => <div key={item.field}>
        {(index === 0 || index === 6) && <h2 className="mt-6 text-xl font-bold">{index === 0 ? 'ส่วนคัดกรอง A–F' : 'ส่วนประเมิน G–R'}</h2>}
        <fieldset disabled={saving || history?.history_requires_review} className="my-4 border-b py-4">
          <legend className="font-semibold">{item.letter}. {item.label}</legend>
          {answers[item.field] && !selected[index] && <p className="my-2 text-amber-800">คำตอบเดิมใช้รูปแบบเก่า กรุณาตรวจและเลือกคำตอบที่ถูกต้อง</p>}
          <div className="mt-3 flex flex-wrap gap-3">{item.options.map(option => <label key={option.value} className={`cursor-pointer rounded-xl border p-3 ${answers[item.field] === option.value ? 'border-primary-600 bg-primary-50' : 'bg-white'}`}>
            <input type="radio" required name={item.field} value={option.value} checked={answers[item.field] === option.value} onChange={() => { setSaved(false); setAnswers(previous => ({ ...previous, [item.field]: option.value })); }} className="mr-2" />
            {option.label} <span className="ml-3 text-gray-500">{option.score}</span>
          </label>)}</div>
        </fieldset>
      </div>)}
      {fillNotice && <p role="status" className="my-3 text-slate-600">{fillNotice}</p>}
      <div className="mt-5 flex flex-wrap justify-end gap-3">
        <button type="button" disabled={saving || filling || history?.history_requires_review} onClick={() => void fillFromBia()} className="rounded-xl border border-primary-700 px-5 py-3 font-semibold text-primary-700 disabled:opacity-50">{filling ? 'กำลังเติมค่า...' : 'เติม F, Q, R จากค่า BIA'}</button>
        <button disabled={saving || filling || history?.history_requires_review} className="sansa-primary-button disabled:opacity-50">{saving ? 'กำลังบันทึก...' : 'บันทึก MNA'}</button>
      </div>
    </form>}
  </div>;
}
