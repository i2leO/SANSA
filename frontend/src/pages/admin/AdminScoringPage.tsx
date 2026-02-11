import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { useAuthStore } from "@/stores/authStore";
import { useCallback, useEffect, useMemo, useState } from "react";

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

type ScoringValue = {
  id: number;
  level_code: string;
  level_name: string;
  min_score: string | number | null;
  max_score: string | number | null;
  level_order: number;
  advice_text?: string | null;
};

type ScoringVersion = {
  id: number;
  instrument_name: string;
  version_number: string;
  version_name?: string | null;
  description?: string | null;
  is_active: boolean;
  effective_date?: string | null;
  rule_values: ScoringValue[];
};

export default function AdminScoringPage() {
  const { user } = useAuthStore();
  const [versions, setVersions] = useState<ScoringVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<ScoringVersion[]>("/scoring/versions");
      setVersions(res.data);
      setSelectedId((prev) => prev ?? (res.data.length > 0 ? res.data[0].id : null));
    } catch (err: unknown) {
      setError(getErrorDetail(err, "ไม่สามารถโหลดกฎการให้คะแนนได้"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const selected = useMemo(
    () => versions.find((v) => v.id === selectedId) || null,
    [versions, selectedId],
  );

  const updateLocalValue = (valueId: number, patch: Partial<ScoringValue>) => {
    setVersions((prev) =>
      prev.map((ver) => ({
        ...ver,
        rule_values: ver.rule_values.map((rv) => (rv.id === valueId ? { ...rv, ...patch } : rv)),
      })),
    );
  };

  const saveValue = async (valueId: number) => {
    if (user?.role !== "admin") return;

    const value = versions.flatMap((v) => v.rule_values).find((rv) => rv.id === valueId);
    if (!value) return;

    setSavingId(valueId);
    setError(null);
    try {
      await apiClient.put(`/scoring/values/${valueId}`, null, {
        params: {
          min_score: value.min_score === "" ? null : value.min_score,
          max_score: value.max_score === "" ? null : value.max_score,
          level_name: value.level_name,
          advice_text: value.advice_text ?? null,
          level_order: value.level_order,
        },
      });
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "บันทึกไม่สำเร็จ"));
    } finally {
      setSavingId(null);
    }
  };

  const activateVersion = async (versionId: number) => {
    if (user?.role !== "admin") return;
    setError(null);
    try {
      await apiClient.post(`/scoring/versions/${versionId}/activate`);
      await load();
    } catch (err: unknown) {
      setError(getErrorDetail(err, "สลับเวอร์ชันไม่สำเร็จ"));
    }
  };

  return (
    <AdminLayout title="กฎการให้คะแนน">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">กฎการให้คะแนน</h1>
        <p className="text-gray-600">ดู/แก้ไข threshold และคำแนะนำ (เฉพาะ admin)</p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl shadow border border-gray-200 p-4 mb-6 flex flex-wrap items-center gap-3">
        <div className="text-sm text-gray-600">เลือกเวอร์ชัน:</div>
        <select
          value={selectedId ?? ""}
          onChange={(e) => setSelectedId(parseInt(e.target.value))}
          className="px-3 py-2 border-2 border-gray-200 rounded-lg"
        >
          {versions.map((v) => (
            <option key={v.id} value={v.id}>
              {v.instrument_name} v{v.version_number}
              {v.is_active ? " (active)" : ""}
            </option>
          ))}
        </select>
        <button onClick={load} className="text-primary-600 hover:text-primary-700 font-medium">
          รีเฟรช
        </button>
      </div>

      <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-6 text-gray-600">กำลังโหลด...</div>
        ) : !selected ? (
          <div className="p-6 text-gray-600">ไม่พบข้อมูล</div>
        ) : (
          <>
            <div className="px-6 py-4 border-b bg-gray-50 flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold text-gray-800">
                  {selected.instrument_name} v{selected.version_number}
                </div>
                <div className="text-sm text-gray-600">{selected.description || ""}</div>
              </div>
              {user?.role === "admin" && (
                <button
                  onClick={() => activateVersion(selected.id)}
                  className="px-4 py-2 border-2 border-primary-600 text-primary-700 rounded-lg hover:bg-primary-50"
                >
                  ตั้งเป็น active
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-white">
                  <tr>
                    <th className="text-left px-4 py-3 text-gray-700">Level</th>
                    <th className="text-left px-4 py-3 text-gray-700">ชื่อ</th>
                    <th className="text-left px-4 py-3 text-gray-700">Min</th>
                    <th className="text-left px-4 py-3 text-gray-700">Max</th>
                    <th className="text-left px-4 py-3 text-gray-700">Advice</th>
                    <th className="text-right px-4 py-3 text-gray-700">บันทึก</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.rule_values.map((rv) => (
                    <tr key={rv.id} className="border-t align-top">
                      <td className="px-4 py-3 font-mono">{rv.level_code}</td>
                      <td className="px-4 py-3">
                        <input
                          value={rv.level_name}
                          onChange={(e) => updateLocalValue(rv.id, { level_name: e.target.value })}
                          disabled={user?.role !== "admin"}
                          className="w-56 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <input
                          value={rv.min_score ?? ""}
                          onChange={(e) => updateLocalValue(rv.id, { min_score: e.target.value })}
                          disabled={user?.role !== "admin"}
                          className="w-24 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <input
                          value={rv.max_score ?? ""}
                          onChange={(e) => updateLocalValue(rv.id, { max_score: e.target.value })}
                          disabled={user?.role !== "admin"}
                          className="w-24 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <textarea
                          value={rv.advice_text ?? ""}
                          onChange={(e) => updateLocalValue(rv.id, { advice_text: e.target.value })}
                          disabled={user?.role !== "admin"}
                          className="w-96 min-h-20 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => saveValue(rv.id)}
                          disabled={user?.role !== "admin" || savingId !== null}
                          className="text-primary-600 hover:text-primary-700 font-medium disabled:opacity-50"
                        >
                          {savingId === rv.id ? "กำลังบันทึก..." : "บันทึก"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
