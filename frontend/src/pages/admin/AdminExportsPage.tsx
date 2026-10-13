import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { AdminPageHeader } from "@/pages/admin/AdminPageUI";
import { useState } from "react";
import useAdminListSearch from "@/pages/admin/useAdminListSearch";

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export default function AdminExportsPage() {
  const [error, setError] = useState<string | null>(null);
  const [loadingKey, setLoadingKey] = useState<string | null>(null);
  const [search] = useAdminListSearch();

  const exportOne = async (key: string, path: string, extension = "csv") => {
    setError(null);
    setLoadingKey(key);
    try {
      const res = await apiClient.get(path, { responseType: "blob" });
      const filename = `${key}_${new Date().toISOString().slice(0, 10)}.${extension}`;
      downloadBlob(res.data, filename);
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ส่งออกข้อมูลไม่สำเร็จ"));
    } finally {
      setLoadingKey(null);
    }
  };

  const btn = (key: string, label: string, path: string, extension = "csv") => (
    <button
      onClick={() => exportOne(key, path, extension)}
      disabled={loadingKey !== null}
      className="sansa-export-card"
    >
      <div className="flex items-center justify-between">
        <span className="sansa-menu-icon sansa-icon-blue" aria-hidden>⇩</span><div className="flex-1">
          <div className="text-lg font-semibold text-gray-800">{label}</div>
          <div className="text-sm text-gray-600">ไฟล์ {extension.toUpperCase()} ตามโครงสร้าง revised4</div>
        </div>
        <div className="sansa-export-action">
          {loadingKey === key ? "กำลังดาวน์โหลด..." : "ดาวน์โหลด →"}
        </div>
      </div>
    </button>
  );
  const exports = [
    ["participant_data", "ข้อมูลผู้เข้าร่วมและ SANSA", "/exports/sansa.csv", "csv"],
    ["prediction", "ผลทำนาย SANSA", "/exports/prediction.csv", "csv"],
    ["bia_mna_staff", "ข้อมูล BIA และ MNA", "/exports/bia.csv", "csv"],
    ["satisfaction", "ความพึงพอใจ", "/exports/satisfaction.csv", "csv"],
    ["sansa_revised4", "ข้อมูลรวมตามต้นแบบ revised4", "/exports/revised4.xlsx", "xlsx"],
    ["assessment_history", "ประวัติการแก้ไข MNA และ BIA", "/exports/assessment-history.csv", "csv"],
  ].filter(item => !search.trim() || item.join(' ').toLocaleLowerCase('th').includes(search.trim().toLocaleLowerCase('th')));

  return (
    <AdminLayout title="ส่งออกข้อมูล">
      <AdminPageHeader icon="exports" title="ส่งออกข้อมูล" description="เลือกชุดข้อมูล CSV ที่ต้องการนำไปวิเคราะห์ใน SPSS" />

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="sansa-export-grid">
        {exports.map(([key, label, path, extension]) => btn(key, label, path, extension))}
      </div>
      {exports.length === 0 && <div className="sansa-panel p-6 text-slate-500">ไม่พบรายการส่งออกที่ตรงกับ “{search}”</div>}

    </AdminLayout>
  );
}
