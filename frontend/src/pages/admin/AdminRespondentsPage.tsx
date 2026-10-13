import TableControls from '@/components/TableControls';
import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { AdminCreatePanel, AdminListHeader, AdminPageHeader } from "@/pages/admin/AdminPageUI";
import { Respondent } from "@/types";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useAdminListSearch from "@/pages/admin/useAdminListSearch";

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

export default function AdminRespondentsPage() {
  const navigate = useNavigate();
  const [respondents, setRespondents] = useState<Respondent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useAdminListSearch();
  const [refreshKey,setRefreshKey]=useState(0);

  const [page,setPage]=useState(0);
  const [size,setSize]=useState(10);
  const [total,setTotal]=useState(0);
  const [creating,setCreating]=useState(false);
  const openRespondent = (respondentCode: string) => {
    navigate(`/admin/respondents/${respondentCode}`);
  };
  const createRespondent=async()=>{setCreating(true);try {const {data}=await apiClient.post<Respondent>('/respondents',{});navigate(`/admin/respondents/${data.respondent_code}`);}catch {setError('สร้างผู้เข้าร่วมไม่สำเร็จ');}finally {setCreating(false);}};

  useEffect(() => {
    let active=true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get<Respondent[]>("/respondents", {params:{skip:page*size,limit:size,search}});
        if(active){setRespondents(res.data);setTotal(Number(res.headers["x-total-count"] || 0));}
      } catch (err: unknown) {
        if(active)setError(getErrorDetail(err, "ไม่สามารถโหลดรายชื่อผู้เข้าร่วมได้"));
      } finally {
        if(active)setLoading(false);
      }
    };
    void load();
    return()=>{active=false;};
  }, [page,size,search,refreshKey]);

  return (
    <AdminLayout title="ผู้เข้าร่วมการประเมิน">
      <AdminPageHeader icon="respondents" title="ผู้เข้าร่วมการประเมิน" description="จัดการข้อมูลผู้เข้าร่วม การประเมิน และ QR Code สำหรับเข้าใช้งาน" />
      <AdminCreatePanel title="เพิ่มผู้เข้าร่วมเพื่อออก QR"><p className="text-sm text-slate-500 mb-4">ระบบจะสร้างรหัสผู้เข้าร่วมใหม่ จากนั้นคุณสามารถออก QR Code ที่หน้ารายละเอียดได้</p><button className="sansa-primary-button" onClick={createRespondent} disabled={creating}>{creating?'กำลังสร้าง…':'สร้างผู้เข้าร่วม'}</button></AdminCreatePanel>
      <div className="sansa-panel overflow-hidden mt-6">
        <AdminListHeader title="รายชื่อผู้เข้าร่วม" total={total} onRefresh={()=>setRefreshKey(value=>value+1)} />
        <TableControls search={search} onSearch={s=>{setSearch(s);setPage(0);}} page={page} onPage={setPage} size={size} onSize={n=>{setSize(n);setPage(0);}} total={total} />
        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : error ? (
          <div className="p-6 text-red-700">{error}</div>
        ) : respondents.length === 0 ? (
          <div className="p-6 text-gray-600">ไม่พบข้อมูล</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 text-gray-700">รหัส</th>
                  <th className="text-left px-4 py-3 text-gray-700">อายุ</th>
                  <th className="text-left px-4 py-3 text-gray-700">เพศ</th>
                  <th className="text-left px-4 py-3 text-gray-700">อีเมล/โทร</th>
                  <th className="text-right px-4 py-3 text-gray-700">ดูรายละเอียด</th>
                </tr>
              </thead>
              <tbody>
                {respondents.map((r) => (
                  <tr
                    key={r.id}
                    role="link"
                    tabIndex={0}
                    aria-label={`เปิดรายละเอียดผู้เข้าร่วม ${r.respondent_code}`}
                    onClick={() => openRespondent(r.respondent_code)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        openRespondent(r.respondent_code);
                      }
                    }}
                    className="group cursor-pointer border-t transition-colors hover:bg-primary-50/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary-500"
                  >
                    <td className="px-4 py-3 font-mono font-semibold">{r.respondent_code}</td>
                    <td className="px-4 py-3">{r.age ?? "-"}</td>
                    <td className="px-4 py-3">{r.sex ?? "-"}</td>
                    <td className="px-4 py-3 text-gray-600">{r.email || r.phone || "-"}</td>
                    <td className="px-4 py-3 text-right">
                      <span className="inline-flex font-medium text-primary-600 transition-transform group-hover:translate-x-0.5 group-hover:text-primary-700">
                        เปิด →
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <TableControls search={search} onSearch={s=>{setSearch(s);setPage(0);}} page={page} onPage={setPage} size={size} onSize={n=>{setSize(n);setPage(0);}} total={total} mode="pagination" />
      </div>
    </AdminLayout>
  );
}
