import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { Respondent, Visit } from "@/types";
import * as QRCode from "qrcode";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type OptionalFetchState<T> = {
  data: T | null;
  status: "idle" | "loading" | "ok" | "missing" | "error";
};

type FetchMap = Record<number, OptionalFetchState<unknown>>;
type Change = { previous: number | null; current: number | null; difference: number | null; direction: "increased" | "decreased" | "unchanged" | "unknown" };
type Occurrence = { occurrence_id: number; occurrence_number: number; assessment_date: string | null; visit_type: string; values: Record<string, number | null>; changes_from_previous: Record<string, Change> };

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

function getHttpStatus(err: unknown): number | undefined {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { status?: unknown } };
    const status = anyErr.response?.status;
    return typeof status === "number" ? status : undefined;
  }
  return undefined;
}

export default function AdminRespondentDetailPage() {
  const { respondentCode } = useParams();
  const navigate = useNavigate();

  const [respondent, setRespondent] = useState<Respondent | null>(null);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [occurrences, setOccurrences] = useState<Occurrence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [sansaByVisitId, setSansaByVisitId] = useState<FetchMap>({});
  const [mnaByVisitId, setMnaByVisitId] = useState<FetchMap>({});
  const [biaByVisitId, setBiaByVisitId] = useState<FetchMap>({});

  const [qrUrl, setQrUrl] = useState<string | null>(null);
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [qrError, setQrError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [editing,setEditing]=useState(false);
  const [saving,setSaving]=useState(false);
  const [age,setAge]=useState('');
  const [sex,setSex]=useState('');
  const [phone,setPhone]=useState('');
  const [email,setEmail]=useState('');

  const [qrBusy, setQrBusy] = useState(false);
  const issueQr = async () => {
    if (!respondent || qrBusy) return;
    if (!window.confirm('ออก QR ใหม่จะยกเลิก QR และการเข้าสู่ระบบเดิมของผู้เข้าร่วม ต้องการดำเนินการหรือไม่?')) return;
    setQrBusy(true); setQrError(null); setQrDataUrl(null); setQrUrl(null); setCopyStatus(null);
    try {
      const { data } = await apiClient.post<{secret:string}>(`/participant-auth/respondents/${respondent.id}/qr`);
      const url = `${window.location.origin}/start#qr=${encodeURIComponent(data.secret)}`;
      setQrUrl(url);
      setQrDataUrl(await QRCode.toDataURL(url, { margin: 2, width: 260 }));
    } catch { setQrError('ออก QR ไม่สำเร็จ กรุณาลองใหม่ด้วยบัญชีผู้ดูแลระบบ'); }
    finally { setQrBusy(false); }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const r = await apiClient.get<Respondent>(`/respondents/${respondentCode}`);
        setRespondent(r.data);
        setAge(r.data.age==null?'':String(r.data.age));setSex(r.data.sex||'');setPhone(r.data.phone||'');setEmail(r.data.email||'');

        const v = await apiClient.get<Visit[]>(`/visits/respondent/${r.data.id}`);
        setVisits(v.data);
        const timeline = await apiClient.get<{ occurrences: Occurrence[] }>(`/assessment-history/respondent/${r.data.id}`);
        setOccurrences(timeline.data.occurrences);

        // Preload instrument presence (best-effort)
        const visitIds = v.data.map((x) => x.id);
        const init: FetchMap = {};
        for (const id of visitIds) {
          init[id] = { data: null, status: "loading" };
        }
        setSansaByVisitId(init);
        setMnaByVisitId(init);
        setBiaByVisitId(init);

        await Promise.all(
          visitIds.map(async (visitId) => {
            const fetchOne = async (path: string, setter: Dispatch<SetStateAction<FetchMap>>) => {
              try {
                const res = await apiClient.get<unknown>(path);
                setter((prev) => ({ ...prev, [visitId]: { data: res.data, status: "ok" } }));
              } catch (e: unknown) {
                const status = getHttpStatus(e) === 404 ? "missing" : "error";
                setter((prev) => ({ ...prev, [visitId]: { data: null, status } }));
              }
            };

            await Promise.all([
              fetchOne(`/sansa/visit/${visitId}`, setSansaByVisitId),
              fetchOne(`/mna/visit/${visitId}`, setMnaByVisitId),
              fetchOne(`/bia/visit/${visitId}`, setBiaByVisitId),
            ]);
          }),
        );
      } catch (err: unknown) {
        setError(getErrorDetail(err, "ไม่สามารถโหลดข้อมูลผู้เข้าร่วมได้"));
      } finally {
        setLoading(false);
      }
    };

    if (respondentCode) {
      load();
    }
  }, [respondentCode]);

  const saveRespondent=async()=>{if(!respondent)return;setSaving(true);setError(null);try{const {data}=await apiClient.put<Respondent>(`/respondents/${respondent.id}`,{age:age===''?null:Number(age),sex:sex||null,phone:phone.trim()||null,email:email.trim()||null});setRespondent(data);setEditing(false);}catch(err:unknown){setError(getErrorDetail(err,'บันทึกข้อมูลผู้เข้าร่วมไม่สำเร็จ'));}finally{setSaving(false);}};
  const createOccurrence=async()=>{if(!respondent||saving)return;setSaving(true);setError(null);try{const {data}=await apiClient.post<Visit>(`/visits/respondent/${respondent.id}/next`,{assessment_date:new Date().toISOString().slice(0,10),visit_type:'follow_up'});navigate(`/admin/results/${data.id}`);}catch(err:unknown){setError(getErrorDetail(err,'สร้างรอบการประเมินใหม่ไม่สำเร็จ'));setSaving(false);}};
  const deleteRespondent=async()=>{if(!respondent||!confirm(`ลบผู้เข้าร่วม ${respondent.respondent_code} หรือไม่? ข้อมูลจะถูกซ่อนจากระบบ`))return;setSaving(true);try{await apiClient.delete(`/respondents/${respondent.id}`);navigate('/admin/respondents');}catch(err:unknown){setError(getErrorDetail(err,'ลบผู้เข้าร่วมไม่สำเร็จ'));setSaving(false);}};

  return (
    <AdminLayout title="รายละเอียดผู้เข้าร่วม">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">รายละเอียดผู้เข้าร่วม</h1>
          <p className="text-gray-600">
            รหัส: <span className="font-mono font-semibold">{respondentCode}</span>
          </p>
        </div>
        <button
          onClick={() => navigate("/admin/respondents")}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← กลับรายการ
        </button>
      </div>

      {loading ? (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-200 text-gray-600">
          กำลังโหลด...
        </div>
      ) : error ? (
        <div className="bg-white rounded-xl shadow p-6 border border-red-200 text-red-700">
          {error}
        </div>
      ) : !respondent ? (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-200 text-gray-600">
          ไม่พบข้อมูล
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow p-6 border border-gray-200 mb-6">
            <div className="flex items-center justify-between gap-3 mb-5"><h2 className="text-lg font-semibold">ข้อมูลผู้เข้าร่วม</h2><div><button onClick={()=>setEditing(value=>!value)} className="text-primary-700 font-medium">{editing?'ยกเลิก':'แก้ไข'}</button><button onClick={deleteRespondent} disabled={saving} className="ml-4 text-red-600 font-medium disabled:opacity-50">ลบ</button></div></div>
            {editing?<><div className="grid md:grid-cols-2 gap-4"><label className="text-sm">อายุ<input type="number" min="0" max="150" className="sansa-search mt-1" value={age} onChange={e=>setAge(e.target.value)} /></label><label className="text-sm">เพศ<select className="sansa-search mt-1" value={sex} onChange={e=>setSex(e.target.value)}><option value="">ไม่ระบุ</option><option value="male">ชาย</option><option value="female">หญิง</option></select></label><label className="text-sm">โทรศัพท์<input className="sansa-search mt-1" value={phone} onChange={e=>setPhone(e.target.value)} /></label><label className="text-sm">อีเมล<input type="email" className="sansa-search mt-1" value={email} onChange={e=>setEmail(e.target.value)} /></label></div><button onClick={saveRespondent} disabled={saving} className="sansa-primary-button mt-5">{saving?'กำลังบันทึก…':'บันทึกการแก้ไข'}</button></>:<div className="grid md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-500">อายุ</div>
                <div className="font-semibold">{respondent.age ?? "-"}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">เพศ</div>
                <div className="font-semibold">{respondent.sex ?? "-"}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">ติดต่อ</div>
                <div className="font-semibold">{respondent.email || respondent.phone || "-"}</div>
              </div>
            </div>}
          </div>

          <div className="bg-white rounded-xl shadow p-6 border border-gray-200 mb-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-800">QR ส่วนตัวสำหรับเข้าสู่ระบบ</h2>
                <p className="text-sm text-gray-600">
                  QR เป็นรหัสลับ เก็บรักษาไว้เป็นส่วนตัว ออกใหม่จะยกเลิก QR เดิม
                </p>

                <button type="button" onClick={issueQr} disabled={qrBusy} className="sansa-primary-button mt-4">{qrBusy ? 'กำลังออก QR…' : 'ออก / เปลี่ยน QR ส่วนตัว'}</button>
                <p className="text-xs text-slate-500 mt-2">ดาวน์โหลดหลังออก QR ก่อนออกจากหน้านี้ ระบบไม่เก็บรหัสลับฉบับอ่านได้</p>

                {qrUrl && (
                  <div className="mt-3">
                    <div className="text-xs text-gray-500 mb-1">ลิงก์</div>
                    <div className="text-xs text-gray-500">ลิงก์ลับสำหรับผู้เข้าร่วม</div>
                    <div className="mt-2 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={async () => {
                          if (!qrUrl) return;
                          try {
                            await navigator.clipboard.writeText(qrUrl);
                            setCopyStatus("คัดลอกลิงก์แล้ว");
                          } catch {
                            setCopyStatus("คัดลอกไม่สำเร็จ (อาจไม่อนุญาต clipboard)");
                          }
                        }}
                        className="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm font-medium"
                      >
                        คัดลอกลิงก์
                      </button>

                      {qrDataUrl && (
                        <a
                          href={qrDataUrl}
                          download={`respondent_${respondentCode}_qr.png`}
                          className="px-3 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 text-sm font-medium"
                        >
                          ดาวน์โหลด QR
                        </a>
                      )}

                      {copyStatus && <div className="text-sm text-gray-600">{copyStatus}</div>}
                    </div>
                  </div>
                )}
              </div>

              <div className="shrink-0">
                {qrDataUrl ? (
                  <img
                    src={qrDataUrl}
                    alt="QR code"
                    className="w-[220px] h-[220px] rounded-lg border border-gray-200 bg-white"
                  />
                ) : qrError ? (
                  <div className="w-[220px] rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                    {qrError}
                  </div>
                ) : (
                  <div className="w-[220px] h-[220px] rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
                    กดออก QR เพื่อสร้างรหัสส่วนตัว
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden mb-6">
            <div className="px-6 py-4 border-b bg-gray-50 flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-gray-800">แนวโน้มการติดตามของผู้เข้าร่วมคนเดิม</h2><p className="text-sm text-gray-600">จำนวนผู้เข้าร่วมยังเป็น 1 คน แต่มีรอบการประเมินลูกได้หลายรอบ</p></div><button onClick={createOccurrence} disabled={saving} className="sansa-primary-button">เพิ่มรอบการประเมิน</button></div>
            {occurrences.length<2?<p className="p-6 text-gray-600">ยังไม่มีรอบก่อนหน้าสำหรับเปรียบเทียบ</p>:<div className="overflow-x-auto"><table className="min-w-full text-sm"><thead><tr className="bg-white"><th className="px-4 py-3 text-left">รอบ</th><th className="px-4 py-3 text-left">วันที่</th>{[["mna_total","MNA"],["weight_kg","น้ำหนัก"],["bmi","BMI"],["waist_circumference_cm","รอบเอว"],["body_fat_percentage","% ไขมัน"]].map(([,label])=><th key={label} className="px-4 py-3 text-left">{label}</th>)}</tr></thead><tbody>{occurrences.map(o=><tr key={o.occurrence_id} className="border-t"><td className="px-4 py-3 font-bold">{o.occurrence_number}</td><td className="px-4 py-3">{o.assessment_date??'—'}</td>{["mna_total","weight_kg","bmi","waist_circumference_cm","body_fat_percentage"].map(key=>{const change=o.changes_from_previous[key];const marker=change?.direction==='increased'?'เพิ่มขึ้น':change?.direction==='decreased'?'ลดลง':change?.direction==='unchanged'?'เท่าเดิม':'';return <td key={key} className="px-4 py-3"><b>{o.values[key]??'—'}</b>{marker&&<span className="block text-xs text-slate-500">{marker}{change.difference!=null?` (${change.difference>0?'+':''}${change.difference.toFixed(2)})`:''}</span>}</td>})}</tr>)}</tbody></table></div>}
          </div>

          <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-800">รอบการประเมิน</h2>
            </div>

            {visits.length === 0 ? (
              <div className="p-6 text-gray-600">ยังไม่มี visit</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-white">
                    <tr>
                      <th className="text-left px-4 py-3 text-gray-700">รอบ / ID</th>
                      <th className="text-left px-4 py-3 text-gray-700">วันที่</th>
                      <th className="text-left px-4 py-3 text-gray-700">SANSA</th>
                      <th className="text-left px-4 py-3 text-gray-700">MNA</th>
                      <th className="text-left px-4 py-3 text-gray-700">BIA</th>
                      <th className="text-right px-4 py-3 text-gray-700">เปิดผล</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visits.map((v) => {
                      const sansa = sansaByVisitId[v.id];
                      const mna = mnaByVisitId[v.id];
                      const bia = biaByVisitId[v.id];

                      const badge = (s?: OptionalFetchState<unknown>) => {
                        if (!s || s.status === "idle" || s.status === "loading")
                          return "กำลังเช็ก...";
                        if (s.status === "ok") return "มี";
                        if (s.status === "missing") return "ไม่มี";
                        return "ผิดพลาด";
                      };

                      const badgeClass = (s?: OptionalFetchState<unknown>) => {
                        if (!s || s.status === "idle" || s.status === "loading")
                          return "bg-gray-100 text-gray-700";
                        if (s.status === "ok") return "bg-green-100 text-green-800";
                        if (s.status === "missing") return "bg-yellow-50 text-yellow-800";
                        return "bg-red-50 text-red-800";
                      };

                      return (
                        <tr key={v.id} className="border-t">
                          <td className="px-4 py-3"><b>รอบ {v.visit_number}</b><span className="block font-mono text-xs text-slate-500">ID {v.id}</span></td>
                          <td className="px-4 py-3">{v.visit_date}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded ${badgeClass(sansa)}`}>
                              {badge(sansa)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded ${badgeClass(mna)}`}>
                              {badge(mna)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded ${badgeClass(bia)}`}>
                              {badge(bia)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button
                              onClick={() => navigate(`/admin/results/${v.id}`)}
                              className="text-primary-600 hover:text-primary-700 font-medium"
                            >
                              SANSA Result →
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </AdminLayout>
  );
}
