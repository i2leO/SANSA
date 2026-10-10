import TableControls from '@/components/TableControls';
import useTableRows from '@/components/useTableRows';
import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { AdminCreatePanel, AdminListHeader, AdminPageHeader } from "@/pages/admin/AdminPageUI";
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
  const [mapLink,setMapLink]=useState("");
  const [description,setDescription]=useState("");
  const [phone, setPhone] = useState("");
  const [editingId,setEditingId]=useState<number|null>(null);
  const [busyId,setBusyId]=useState<number|null>(null);
  const [isActive,setIsActive]=useState(true);

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
      const payload={
        name: name.trim(),
        address: address.trim() || null,
        phone: phone.trim() || null,
        map_link: /^https?:\/\//i.test(mapLink) ? mapLink : null,
        description: description.trim() || null,
        is_active: isActive,
      };
      if(editingId) await apiClient.put(`/facilities/${editingId}`,payload); else await apiClient.post("/facilities",payload);
      setName("");
      setAddress("");
      setPhone("");setMapLink("");setDescription("");
      setEditingId(null);setIsActive(true);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "เพิ่มศูนย์บริการไม่สำเร็จ"));
    }
  };
  const edit=(item:Facility)=>{setEditingId(item.id);setName(item.name);setAddress(item.address||'');setPhone(item.phone||'');setMapLink(item.map_link||'');setDescription(item.description||'');setIsActive(item.is_active);window.scrollTo({top:0,behavior:'smooth'});};
  const remove=async(item:Facility)=>{if(!confirm(`ลบศูนย์บริการ “${item.name}” หรือไม่?`))return;setBusyId(item.id);setError(null);try{await apiClient.delete(`/facilities/${item.id}`);await load();}catch(err:unknown){setError(getErrorDetail(err,'ลบศูนย์บริการไม่สำเร็จ'));}finally{setBusyId(null);}};

  const table = useTableRows(items);

  return (
    <AdminLayout title="ศูนย์บริการสุขภาพ">
      <AdminPageHeader icon="facilities" title="ศูนย์บริการสุขภาพ" description="จัดการข้อมูลศูนย์บริการสุขภาพที่แสดงแก่ผู้ใช้งาน" />

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <AdminCreatePanel title={editingId?"แก้ไขศูนย์บริการ":"เพิ่มศูนย์บริการ"} defaultOpen={Boolean(editingId)}>
        <p className="text-sm text-slate-500 mb-4">ข้อมูลที่เปิดใช้งานจะแสดงในหน้าศูนย์บริการสำหรับประชาชน</p>
        <div className="grid md:grid-cols-3 gap-3">
          <label className="text-sm font-medium">ชื่อศูนย์บริการ *<input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="เช่น ศูนย์บริการสาธารณสุข 1"
            title="ชื่อเต็มของศูนย์บริการที่จะแสดงแก่ผู้ใช้งาน"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          /></label>
          <label className="text-sm font-medium">ที่อยู่<input
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="เลขที่ ถนน เขต จังหวัด (ไม่บังคับ)"
            title="ที่อยู่สำหรับให้ผู้ใช้งานเดินทางไปยังศูนย์บริการ"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          /></label>
          <label className="text-sm font-medium">โทรศัพท์<input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="เช่น 02-123-4567 (ไม่บังคับ)"
            title="หมายเลขสำหรับติดต่อศูนย์บริการ"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-100"
          /></label>
        </div>
        <label className="block mt-4 text-sm font-medium">รายละเอียด<textarea value={description} onChange={e=>setDescription(e.target.value)} placeholder="เช่น เวลาทำการและบริการที่มี" title="ข้อมูลเพิ่มเติมที่เป็นประโยชน์ต่อผู้ใช้" className="sansa-search mt-2" rows={2} /></label>
        <label className="block mt-4 text-sm font-medium">ลิงก์แผนที่ (https://)<input type="url" value={mapLink} onChange={e=>setMapLink(e.target.value)} placeholder="เช่น https://maps.google.com/..." title="วางลิงก์ตำแหน่งจาก Google Maps ที่ขึ้นต้นด้วย https://" className="sansa-search mt-2" /></label>
        <label className="flex items-center gap-2 mt-4 text-sm font-medium"><input type="checkbox" checked={isActive} onChange={e=>setIsActive(e.target.checked)} /> เปิดใช้งานและแสดงหน้าเว็บไซต์</label>
        <div className="mt-4">
          <button
            onClick={create}
            className="px-5 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            {editingId?'บันทึกการแก้ไข':'เพิ่มศูนย์บริการ'}
          </button>
          {editingId&&<button className="ml-3 px-5 py-3 border rounded-lg" onClick={()=>{setEditingId(null);setName('');setAddress('');setPhone('');setMapLink('');setDescription('');setIsActive(true);}}>ยกเลิก</button>}
        </div>
      </AdminCreatePanel>

      <div className="sansa-panel overflow-hidden mt-6">
        <AdminListHeader title="รายการศูนย์บริการ" total={items.length} onRefresh={load} />

        <TableControls {...table.controls} />
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
                  <th className="text-right px-4 py-3 text-gray-700">จัดการ</th>
                </tr>
              </thead>
              <tbody>
                {table.rows.map((f) => (
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
                    <td className="px-4 py-3 text-right whitespace-nowrap"><button onClick={()=>edit(f)} className="text-primary-700 font-medium">แก้ไข</button><button disabled={busyId===f.id} onClick={()=>remove(f)} className="ml-4 text-red-600 font-medium disabled:opacity-50">ลบ</button></td>
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
