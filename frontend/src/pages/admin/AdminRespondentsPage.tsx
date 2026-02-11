import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { Respondent } from "@/types";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

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
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return respondents;
    return respondents.filter((r) => r.respondent_code.toLowerCase().includes(q));
  }, [respondents, search]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get<Respondent[]>("/respondents");
        setRespondents(res.data);
      } catch (err: unknown) {
        setError(getErrorDetail(err, "ไม่สามารถโหลดรายชื่อผู้เข้าร่วมได้"));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <AdminLayout title="ผู้เข้าร่วมการประเมิน">
      <div className="flex items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">ผู้เข้าร่วมการประเมิน</h1>
          <p className="text-gray-600">คลิกเพื่อดูรายละเอียดผู้เข้าร่วมและการประเมิน</p>
        </div>
        <button
          onClick={() => navigate("/admin/dashboard")}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← กลับหน้าแดชบอร์ด
        </button>
      </div>

      <div className="bg-white rounded-xl shadow p-4 mb-4 border border-gray-200">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ค้นหารหัสผู้เข้าร่วม (เช่น R001 หรือ RES...)"
          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
        />
      </div>

      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : error ? (
          <div className="p-6 text-red-700">{error}</div>
        ) : filtered.length === 0 ? (
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
                {filtered.map((r) => (
                  <tr key={r.id} className="border-t hover:bg-primary-50/50">
                    <td className="px-4 py-3 font-mono font-semibold">{r.respondent_code}</td>
                    <td className="px-4 py-3">{r.age ?? "-"}</td>
                    <td className="px-4 py-3">{r.sex ?? "-"}</td>
                    <td className="px-4 py-3 text-gray-600">{r.email || r.phone || "-"}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => navigate(`/admin/respondents/${r.respondent_code}`)}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        เปิด →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
