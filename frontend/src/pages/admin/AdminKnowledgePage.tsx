import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { KnowledgePost } from "@/types";
import { useCallback, useEffect, useState } from "react";

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

export default function AdminKnowledgePage() {
  const [posts, setPosts] = useState<KnowledgePost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [isPublished, setIsPublished] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<KnowledgePost[]>("/knowledge", {
        params: { include_unpublished: true },
      });
      setPosts(res.data);
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ไม่สามารถโหลดบทความได้"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = async () => {
    if (!title.trim()) {
      setError("กรุณากรอกหัวข้อ");
      return;
    }
    setError(null);
    try {
      await apiClient.post("/knowledge", {
        title: title.trim(),
        category: category.trim() || null,
        is_published: isPublished,
      });
      setTitle("");
      setCategory("");
      setIsPublished(false);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "สร้างบทความไม่สำเร็จ"));
    }
  };

  return (
    <AdminLayout title="เนื้อหาความรู้">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">เนื้อหาความรู้</h1>
        <p className="text-gray-600">รายการบทความจากฐานข้อมูล</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl shadow border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">เพิ่มบทความ (แบบขั้นต่ำ)</h2>
        <div className="grid md:grid-cols-3 gap-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="หัวข้อ"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          />
          <input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="หมวดหมู่ (ไม่บังคับ)"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          />
          <label className="flex items-center gap-2 px-4 py-3 border-2 border-gray-200 rounded-lg">
            <input
              type="checkbox"
              checked={isPublished}
              onChange={(e) => setIsPublished(e.target.checked)}
            />
            <span>เผยแพร่</span>
          </label>
        </div>
        <div className="mt-4">
          <button
            onClick={create}
            className="px-5 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            เพิ่มบทความ
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b bg-gray-50 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">รายการบทความ</h2>
          <button onClick={load} className="text-primary-600 hover:text-primary-700 font-medium">
            รีเฟรช
          </button>
        </div>

        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : posts.length === 0 ? (
          <div className="p-6 text-gray-600">ยังไม่มีบทความ</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-white">
                <tr>
                  <th className="text-left px-4 py-3 text-gray-700">หัวข้อ</th>
                  <th className="text-left px-4 py-3 text-gray-700">หมวดหมู่</th>
                  <th className="text-left px-4 py-3 text-gray-700">สถานะ</th>
                  <th className="text-left px-4 py-3 text-gray-700">slug</th>
                </tr>
              </thead>
              <tbody>
                {posts.map((p) => (
                  <tr key={p.id} className="border-t">
                    <td className="px-4 py-3 font-semibold">{p.title}</td>
                    <td className="px-4 py-3">{p.category || "-"}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded ${p.is_published ? "bg-green-100 text-green-800" : "bg-yellow-50 text-yellow-800"}`}
                      >
                        {p.is_published ? "เผยแพร่" : "ร่าง"}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-gray-700">{p.slug}</td>
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
