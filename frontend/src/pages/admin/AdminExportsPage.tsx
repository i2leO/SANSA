import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { useState } from "react";

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

  const exportOne = async (key: string, path: string) => {
    setError(null);
    setLoadingKey(key);
    try {
      const res = await apiClient.get(path, { responseType: "blob" });
      const filename = `${key}_${new Date().toISOString().slice(0, 10)}.csv`;
      downloadBlob(res.data, filename);
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ส่งออกข้อมูลไม่สำเร็จ"));
    } finally {
      setLoadingKey(null);
    }
  };

  const btn = (key: string, label: string, path: string) => (
    <button
      onClick={() => exportOne(key, path)}
      disabled={loadingKey !== null}
      className="w-full text-left p-5 bg-white rounded-xl shadow border-2 border-primary-200 hover:border-primary-400 disabled:opacity-60"
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold text-gray-800">{label}</div>
          <div className="text-sm text-gray-600">{path}</div>
        </div>
        <div className="text-primary-700 font-semibold">
          {loadingKey === key ? "กำลังดาวน์โหลด..." : "ดาวน์โหลด →"}
        </div>
      </div>
    </button>
  );

  return (
    <AdminLayout title="ส่งออกข้อมูล">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">ส่งออกข้อมูล (CSV สำหรับ SPSS)</h1>
        <p className="text-gray-600">ต้องเป็น staff/admin และล็อกอินแล้ว</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {btn("sansa", "Export SANSA", "/exports/sansa.csv")}
        {btn("mna", "Export MNA", "/exports/mna.csv")}
        {btn("bia", "Export BIA", "/exports/bia.csv")}
        {btn("satisfaction", "Export Satisfaction", "/exports/satisfaction.csv")}
        {btn("combined", "Export Combined", "/exports/combined.csv")}
      </div>

      <div className="mt-8 text-sm text-gray-600">
        ถ้าดาวน์โหลดไม่ออก ให้เช็กว่า token ยังไม่หมดอายุ และลองล็อกอินใหม่
      </div>
    </AdminLayout>
  );
}
