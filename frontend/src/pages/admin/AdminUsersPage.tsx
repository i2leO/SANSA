import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { User, UserRole } from "@/types";
import { useCallback, useEffect, useState } from "react";

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
  const [role, setRole] = useState<UserRole>(UserRole.STAFF);

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
    if (!username.trim() || !email.trim() || !password.trim()) {
      setError("กรุณากรอก username, email, password");
      return;
    }
    setError(null);
    try {
      await apiClient.post("/auth/register", {
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
      setRole(UserRole.STAFF);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "สร้างผู้ใช้ไม่สำเร็จ"));
    }
  };

  const deactivate = async (id: number) => {
    if (!confirm("Deactivate ผู้ใช้นี้?")) return;
    setError(null);
    try {
      await apiClient.delete(`/auth/users/${id}`);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ปิดผู้ใช้ไม่สำเร็จ"));
    }
  };

  return (
    <AdminLayout title="จัดการผู้ใช้">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">จัดการผู้ใช้</h1>
        <p className="text-gray-600">เมนูนี้ต้องเป็น admin เท่านั้น</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl shadow border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">เพิ่มผู้ใช้</h2>
        <div className="grid md:grid-cols-3 gap-3">
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="username"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg"
          />
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg"
          />
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="full name (optional)"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg"
          />
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="password"
            type="password"
            className="px-4 py-3 border-2 border-gray-200 rounded-lg"
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            className="px-4 py-3 border-2 border-gray-200 rounded-lg"
          >
            <option value={UserRole.STAFF}>staff</option>
            <option value={UserRole.ADMIN}>admin</option>
          </select>
          <button
            onClick={create}
            className="px-5 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            เพิ่มผู้ใช้
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b bg-gray-50 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">รายการผู้ใช้</h2>
          <button onClick={load} className="text-primary-600 hover:text-primary-700 font-medium">
            รีเฟรช
          </button>
        </div>

        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : users.length === 0 ? (
          <div className="p-6 text-gray-600">ไม่พบข้อมูล</div>
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
                {users.map((u) => (
                  <tr key={u.id} className="border-t">
                    <td className="px-4 py-3 font-mono">{u.username}</td>
                    <td className="px-4 py-3">{u.full_name || "-"}</td>
                    <td className="px-4 py-3">{u.role}</td>
                    <td className="px-4 py-3">{u.is_active ? "yes" : "no"}</td>
                    <td className="px-4 py-3 text-right">
                      {u.is_active ? (
                        <button
                          onClick={() => deactivate(u.id)}
                          className="text-red-600 hover:text-red-700 font-medium"
                        >
                          deactivate
                        </button>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
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
