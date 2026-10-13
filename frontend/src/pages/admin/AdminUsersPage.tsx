import TableControls from '@/components/TableControls';
import useTableRows from '@/components/useTableRows';
import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { AdminCreatePanel, AdminListHeader, AdminPageHeader } from "@/pages/admin/AdminPageUI";
import { User, UserRole } from "@/types";
import { useCallback, useEffect, useState } from "react";
import QRCode from "qrcode";
import useAdminListSearch from "@/pages/admin/useAdminListSearch";

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>(UserRole.USER);
  const [editingId,setEditingId]=useState<number|null>(null);
  const [isActive,setIsActive]=useState(true);
  const [busyId,setBusyId]=useState<number|null>(null);
  const [qrPreview,setQrPreview]=useState<{username:string;url:string;dataUrl:string}|null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<User[]>("/auth/users");
      setUsers(res.data);
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ไม่สามารถโหลดรายชื่อผู้ใช้ได้ (ต้องเป็น admin)"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = async () => {
    if ((!editingId && (!username.trim() || !password.trim())) || !email.trim()) {
      setError(editingId?"กรุณากรอก email":"กรุณากรอก username, email, password");
      return;
    }
    setError(null);
    try {
      if(editingId) await apiClient.put(`/auth/users/${editingId}`,{email:email.trim(),full_name:fullName.trim()||null,role,is_active:isActive}); else await apiClient.post("/auth/register", {
        username: username.trim(),
        email: email.trim(),
        password: password,
        full_name: fullName.trim() || null,
        role,
      });
      setUsername("");
      setEmail("");
      setFullName("");
      setPassword("");
      setRole(UserRole.USER);
      setIsActive(true);setEditingId(null);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "สร้างผู้ใช้ไม่สำเร็จ"));
    }
  };
  const edit=(item:User)=>{setEditingId(item.id);setUsername(item.username);setEmail(item.email);setFullName(item.full_name||'');setPassword('');setRole(item.role);setIsActive(item.is_active);window.scrollTo({top:0,behavior:'smooth'});};

  const deactivate = async (id: number) => {
    if (!confirm("Deactivate ผู้ใช้นี้?")) return;
    setError(null);
    setBusyId(id);try {
      await apiClient.delete(`/auth/users/${id}`);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ปิดผู้ใช้ไม่สำเร็จ"));
    } finally {setBusyId(null);}
  };

  const issueQr = async (user: User) => {
    if (!confirm(`ออก QR ใหม่สำหรับ ${user.username} หรือไม่? QR และ session จาก QR เดิมจะถูกยกเลิก`)) return;
    setBusyId(user.id);setError(null);
    try {
      const {data}=await apiClient.post<{secret:string}>(`/participant-auth/users/${user.id}/qr`);
      const url=`${window.location.origin}/login#qr=${encodeURIComponent(data.secret)}`;
      const dataUrl=await QRCode.toDataURL(url,{width:640,margin:2,errorCorrectionLevel:'M'});
      setQrPreview({username:user.username,url,dataUrl});
    } catch (err:unknown) {
      setError(getErrorDetail(err,'ออก QR ไม่สำเร็จ'));
    } finally {setBusyId(null);}
  };

  const [search, setSearch] = useAdminListSearch();
  const table = useTableRows(users, search, setSearch);

  return (
    <AdminLayout title="จัดการผู้ใช้">
      <AdminPageHeader icon="users" title="จัดการผู้ใช้" description="จัดการบัญชีและสิทธิ์ของผู้ดูแลระบบและเจ้าหน้าที่" />

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {qrPreview&&<section className="mb-5 rounded-2xl border border-primary-200 bg-white p-5 shadow">
        <div className="flex flex-col items-center gap-4 sm:flex-row"><img src={qrPreview.dataUrl} alt={`QR สำหรับ ${qrPreview.username}`} className="h-52 w-52 rounded-xl border"/><div><h2 className="text-xl font-bold">QR สำหรับ {qrPreview.username}</h2><p className="mt-2 text-sm text-slate-600">ดาวน์โหลดหรือส่งให้เจ้าของบัญชีผ่านช่องทางที่ปลอดภัย QR เดิมถูกยกเลิกแล้ว</p><div className="mt-4 flex flex-wrap gap-2"><a href={qrPreview.dataUrl} download={`staff_${qrPreview.username}_qr.png`} className="sansa-primary-button">ดาวน์โหลด QR</a><button onClick={()=>navigator.clipboard.writeText(qrPreview.url)} className="rounded-xl border px-4 py-2 font-semibold">คัดลอกลิงก์</button><button onClick={()=>setQrPreview(null)} className="px-4 py-2 text-slate-500">ปิด</button></div></div></div>
      </section>}

      <AdminCreatePanel title={editingId?"แก้ไขผู้ใช้":"เพิ่มผู้ใช้"} defaultOpen={Boolean(editingId)}>
        <p className="text-sm text-slate-500 mb-4">กรอกข้อมูลบัญชีและเลือกสิทธิ์ให้ตรงกับหน้าที่ของผู้ใช้งาน เครื่องหมาย * คือข้อมูลที่ต้องกรอก</p>
        <div className="grid md:grid-cols-3 gap-3">
          <label className="text-sm font-medium">ชื่อบัญชี *<input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="เช่น somchai01"
            title="ชื่อสำหรับใช้เข้าสู่ระบบ ต้องไม่ซ้ำกับบัญชีอื่น"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg"
            disabled={Boolean(editingId)}
          /><span className="block mt-1 text-xs text-slate-500">ใช้เข้าสู่ระบบและต้องไม่ซ้ำ</span></label>
          <label className="text-sm font-medium">อีเมล *<input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="เช่น somchai@example.com"
            title="อีเมลที่ติดต่อได้ของเจ้าของบัญชี"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg"
          /></label>
          <label className="text-sm font-medium">ชื่อที่แสดง<input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="เช่น สมชาย ใจดี (ไม่บังคับ)"
            title="ชื่อที่จะแสดงในระบบ ไม่ใช่ชื่อสำหรับเข้าสู่ระบบ"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg"
          /></label>
          <label className="text-sm font-medium">รหัสผ่าน {!editingId && "*"}<input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={editingId ? "แก้ไขรหัสผ่านไม่ได้จากหน้านี้" : "ตั้งรหัสผ่านสำหรับเข้าสู่ระบบ"}
            autoComplete="new-password"
            title="รหัสลับสำหรับเข้าสู่ระบบ ไม่ควรใช้ร่วมกับระบบอื่น"
            type="password"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg"
            disabled={Boolean(editingId)}
          /></label>
          <label className="text-sm font-medium">ระดับสิทธิ์ *<select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            title="user ใช้งานทั่วไป, staff จัดการงานประเมิน, admin จัดการระบบและบัญชีผู้ใช้"
            className="block w-full mt-1 px-4 py-3 border-2 border-gray-200 rounded-lg"
          >
            <option value={UserRole.USER}>ผู้ใช้งานทั่วไป (user)</option>
            <option value={UserRole.STAFF}>เจ้าหน้าที่ (staff)</option>
            <option value={UserRole.ADMIN}>ผู้ดูแลระบบ (admin)</option>
          </select><span className="block mt-1 text-xs text-slate-500">Admin สามารถจัดการบัญชีผู้ใช้อื่นได้</span></label>
          {editingId&&<label className="flex items-center gap-2 px-4"><input type="checkbox" checked={isActive} onChange={e=>setIsActive(e.target.checked)} /> เปิดใช้งาน</label>}
          <button
            onClick={create}
            title={editingId ? "บันทึกข้อมูลและสิทธิ์ที่แก้ไข" : "สร้างบัญชีผู้ใช้ตามข้อมูลที่กรอก"}
            className="px-5 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            {editingId?'บันทึกการแก้ไข':'เพิ่มผู้ใช้'}
          </button>
          {editingId&&<button className="px-5 py-3 border rounded-lg" onClick={()=>{setEditingId(null);setUsername('');setEmail('');setFullName('');setPassword('');setRole(UserRole.USER);setIsActive(true);}}>ยกเลิก</button>}
        </div>
      </AdminCreatePanel>

      <div className="sansa-panel overflow-hidden mt-6">
        <AdminListHeader title="รายการผู้ใช้" total={users.length} onRefresh={load} />

        <TableControls {...table.controls} />
        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : table.controls.total === 0 ? (
          <div className="p-6 text-gray-600">{search ? `ไม่พบบัญชีที่ตรงกับ “${search}”` : "ไม่พบข้อมูล"}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-white">
                <tr>
                  <th className="text-left px-4 py-3 text-gray-700">username</th>
                  <th className="text-left px-4 py-3 text-gray-700">ชื่อ</th>
                  <th className="text-left px-4 py-3 text-gray-700">role</th>
                  <th className="text-left px-4 py-3 text-gray-700">active</th>
                  <th className="text-right px-4 py-3 text-gray-700">action</th>
                </tr>
              </thead>
              <tbody>
                {table.rows.map((u) => (
                  <tr key={u.id} className="border-t">
                    <td className="px-4 py-3 font-mono">{u.username}</td>
                    <td className="px-4 py-3">{u.full_name || "-"}</td>
                    <td className="px-4 py-3">{u.role}</td>
                    <td className="px-4 py-3">{u.is_active ? "yes" : "no"}</td>
                    <td className="px-4 py-3 text-right">
                      {u.is_active ? (
                        <><button title="แก้ไขอีเมล ชื่อ สิทธิ์ และสถานะบัญชี" onClick={()=>edit(u)} className="text-primary-700 font-medium">แก้ไข</button>{u.role!==UserRole.USER&&<button title="ออก QR ส่วนตัวสำหรับเข้าสู่ระบบ" disabled={busyId===u.id} onClick={()=>issueQr(u)} className="ml-4 text-teal-700 font-medium disabled:opacity-50">ออก QR</button>}<button title="ระงับบัญชีนี้ไม่ให้เข้าสู่ระบบ" disabled={busyId===u.id} onClick={() => deactivate(u.id)} className="ml-4 text-red-600 hover:text-red-700 font-medium disabled:opacity-50">ปิดใช้งาน</button></>
                      ) : (
                        <button onClick={()=>edit(u)} className="text-primary-700 font-medium">แก้ไข/เปิดใช้งาน</button>
                      )}
                    </td>
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
