import TableControls from '@/components/TableControls';
import useTableRows from '@/components/useTableRows';
import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { AdminCreatePanel, AdminListHeader, AdminPageHeader } from "@/pages/admin/AdminPageUI";
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
  const [content,setContent]=useState("");
  const [summary,setSummary]=useState("");
  const [category, setCategory] = useState("");
  const [isPublished, setIsPublished] = useState(false);
  const [editingId,setEditingId]=useState<number|null>(null);
  const [busyId,setBusyId]=useState<number|null>(null);

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
      const payload={
        title: title.trim(),
        content: content.trim() || null,
        summary: summary.trim() || null,
        category: category.trim() || null,
        is_published: isPublished,
      };
      if(editingId) await apiClient.put(`/knowledge/${editingId}`,payload); else await apiClient.post("/knowledge", payload);
      setTitle("");setContent("");setSummary("");
      setCategory("");
      setIsPublished(false);
      setEditingId(null);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "สร้างบทความไม่สำเร็จ"));
    }
  };
  const edit=(post:KnowledgePost)=>{setEditingId(post.id);setTitle(post.title);setContent(post.content||'');setSummary(post.summary||'');setCategory(post.category||'');setIsPublished(post.is_published);window.scrollTo({top:0,behavior:'smooth'});};
  const remove=async(post:KnowledgePost)=>{if(!confirm(`ลบบทความ “${post.title}” หรือไม่?`))return;setBusyId(post.id);setError(null);try{await apiClient.delete(`/knowledge/${post.id}`);if(editingId===post.id){setEditingId(null);setTitle('');setContent('');setSummary('');setCategory('');setIsPublished(false);}await load();}catch(err:unknown){setError(getErrorDetail(err,'ลบบทความไม่สำเร็จ'));}finally{setBusyId(null);}};

  const table = useTableRows(posts);

  return (
    <AdminLayout title="เนื้อหาความรู้">
      <AdminPageHeader icon="knowledge" title="เนื้อหาความรู้" description="จัดการบทความและข้อมูลความรู้สำหรับผู้ใช้งาน" />

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <AdminCreatePanel title={editingId?"แก้ไขบทความ":"เพิ่มบทความ"} defaultOpen={Boolean(editingId)}>
        <p className="text-sm text-slate-500 mb-4">สร้างเนื้อหาความรู้สำหรับผู้ใช้งาน เลือก “เผยแพร่” เมื่อเนื้อหาพร้อมแสดงบนเว็บไซต์</p>
        <div className="grid md:grid-cols-3 gap-3">
          <label className="text-sm font-medium">หัวข้อบทความ *<input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="เช่น อาหารที่เหมาะสำหรับผู้สูงอายุ"
            title="ชื่อบทความที่ผู้ใช้งานจะมองเห็น"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          /></label>
          <label className="text-sm font-medium">หมวดหมู่<input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="เช่น โภชนาการ (ไม่บังคับ)"
            title="ใช้จัดกลุ่มบทความที่มีเนื้อหาใกล้เคียงกัน"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          /></label>
          <label className="flex items-center gap-2 px-4 py-3 border-2 border-gray-200 rounded-lg">
            <input
              type="checkbox"
              checked={isPublished}
              onChange={(e) => setIsPublished(e.target.checked)}
            />
            <span>เผยแพร่</span>
          </label>
        </div>
        <label className="block mt-4 text-sm font-medium">สรุปบทความ<textarea value={summary} onChange={e=>setSummary(e.target.value)} placeholder="เขียนใจความสำคัญสั้น ๆ สำหรับหน้ารายการ" title="ข้อความย่อที่ช่วยให้ผู้ใช้เข้าใจหัวข้อก่อนเปิดอ่าน" className="sansa-search mt-2" rows={2} /></label>
        <label className="block mt-4 text-sm font-medium">เนื้อหาบทความ *<textarea value={content} onChange={e=>setContent(e.target.value)} placeholder="กรอกเนื้อหาที่ต้องการเผยแพร่" title="เนื้อหาฉบับเต็มที่ผู้ใช้งานจะอ่าน" className="sansa-search mt-2" rows={5} /></label>
        <div className="mt-4">
          <button
            onClick={create}
            className="px-5 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            {editingId?'บันทึกการแก้ไข':'เพิ่มบทความ'}
          </button>
          {editingId&&<button className="ml-3 px-5 py-3 border rounded-lg" onClick={()=>{setEditingId(null);setTitle('');setContent('');setSummary('');setCategory('');setIsPublished(false);}}>ยกเลิก</button>}
        </div>
      </AdminCreatePanel>

      <div className="sansa-panel overflow-hidden mt-6">
        <AdminListHeader title="รายการบทความ" total={posts.length} onRefresh={load} />

        <TableControls {...table.controls} />
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
                  <th className="text-left px-4 py-3 text-gray-700">สื่อ</th>
                  <th className="text-left px-4 py-3 text-gray-700">slug</th>
                  <th className="text-right px-4 py-3 text-gray-700">จัดการ</th>
                </tr>
              </thead>
              <tbody>
                {table.rows.map((p) => (
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
                    <td className="px-4 py-3">{p.media_type === 'pdf' ? 'PDF' : p.media_type === 'image' ? 'ภาพ' : '-'}</td>
                    <td className="px-4 py-3 font-mono text-gray-700">{p.slug}</td>
                    <td className="px-4 py-3 text-right whitespace-nowrap"><button onClick={()=>edit(p)} className="text-primary-700 font-medium">แก้ไข</button><button disabled={busyId===p.id} onClick={()=>remove(p)} className="ml-4 text-red-600 font-medium disabled:opacity-50">ลบ</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <TableControls {...table.controls} mode="pagination" />
      </div>
    </AdminLayout>
  );
}
