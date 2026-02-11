import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { Facility } from "@/types";
import { useCallback, useEffect, useState } from "react";

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

export default function AdminFacilitiesAdminPage() {
  const [items, setItems] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [phone, setPhone] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<Facility[]>("/facilities", {
        params: { include_inactive: true },
      });
      setItems(res.data);
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ไม่สามารถโหลดข้อมูลศูนย์บริการได้"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = async () => {
    if (!name.trim()) {
      setError("กรุณากรอกชื่อศูนย์บริการ");
      return;
    }
    setError(null);
    try {
      await apiClient.post("/facilities", {
        name: name.trim(),
        address: address.trim() || null,
        phone: phone.trim() || null,
        is_active: true,
      });
      setName("");
      setAddress("");
      setPhone("");
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "เพิ่มศูนย์บริการไม่สำเร็จ"));
    }
  };

  return (
    <AdminLayout title="ศูนย์บริการสุขภาพ">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">ศูนย์บริการสุขภาพ</h1>
        <p className="text-gray-600">รายการศูนย์บริการจากฐานข้อมูล</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl shadow border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">เพิ่มศูนย์บริการ (แบบขั้นต่ำ)</h2>
        <div className="grid md:grid-cols-3 gap-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="ชื่อศูนย์บริการ"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          />
          <input
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="ที่อยู่ (ไม่บังคับ)"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          />
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="โทร (ไม่บังคับ)"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          />
        </div>
        <div className="mt-4">
          <button
            onClick={create}
            className="px-5 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            เพิ่มศูนย์บริการ
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b bg-gray-50 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">รายการศูนย์บริการ</h2>
          <button onClick={load} className="text-primary-600 hover:text-primary-700 font-medium">
            รีเฟรช
          </button>
        </div>

        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : items.length === 0 ? (
          <div className="p-6 text-gray-600">ยังไม่มีข้อมูล</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-white">
                <tr>
                  <th className="text-left px-4 py-3 text-gray-700">ชื่อ</th>
                  <th className="text-left px-4 py-3 text-gray-700">ที่อยู่</th>
                  <th className="text-left px-4 py-3 text-gray-700">โทร</th>
                  <th className="text-left px-4 py-3 text-gray-700">สถานะ</th>
                </tr>
              </thead>
              <tbody>
                {items.map((f) => (
                  <tr key={f.id} className="border-t">
                    <td className="px-4 py-3 font-semibold">{f.name}</td>
                    <td className="px-4 py-3 text-gray-600">{f.address || "-"}</td>
                    <td className="px-4 py-3 text-gray-600">{f.phone || "-"}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded ${f.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-700"}`}
                      >
                        {f.is_active ? "เปิดใช้งาน" : "ปิด"}
                      </span>
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
