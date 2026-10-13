import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { AdminPageHeader } from "@/pages/admin/AdminPageUI";
import { useAuthStore } from "@/stores/authStore";
import { useCallback, useEffect, useMemo, useState } from "react";
import useAdminListSearch from "@/pages/admin/useAdminListSearch";

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
  const [search] = useAdminListSearch();

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
  const isApprovedSansa = selected?.instrument_name === "SANSA" && selected.version_number === "0.2.4-20261008";
  const isLegacySansa = selected?.instrument_name === "SANSA" && !isApprovedSansa;
  const visibleRuleValues = useMemo(() => {
    if (!selected) return [];
    const key = search.trim().toLocaleLowerCase('th');
    if (!key) return selected.rule_values;
    return selected.rule_values.filter(value =>
      `${value.level_code} ${value.level_name} ${value.min_score ?? ''} ${value.max_score ?? ''} ${value.advice_text ?? ''}`.toLocaleLowerCase('th').includes(key),
    );
  }, [search, selected]);

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
      <AdminPageHeader icon="scoring" title="กฎการให้คะแนน" description="ดูและจัดการเกณฑ์คะแนนของแบบประเมินแต่ละเวอร์ชัน" />

      <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-950">
        SANSA ใช้นิยาม 0/2/4 ที่อนุมัติเป็นแหล่งคะแนนกลางเพียงชุดเดียว ส่วนผลลัพธ์ใช้ Model 3 และไม่ใช้ช่วงคะแนนรวมแบบเดิม
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="sansa-panel p-5 mb-6 flex flex-wrap items-center gap-3">
        <div className="text-sm text-gray-600">เลือกเวอร์ชัน:</div>
        <select
          aria-label="เวอร์ชันกฎคะแนน"
          title="เลือกชุดกฎคะแนนที่ต้องการตรวจสอบหรือแก้ไข"
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

      <div className="sansa-panel overflow-hidden">
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
              {user?.role === "admin" && selected.instrument_name !== "SANSA" && (
                <button
                  title="ใช้เวอร์ชันนี้เป็นเกณฑ์หลักสำหรับการประเมินใหม่"
                  onClick={() => activateVersion(selected.id)}
                  className="px-4 py-2 border-2 border-primary-600 text-primary-700 rounded-lg hover:bg-primary-50"
                >
                  ตั้งเป็น active
                </button>
              )}
            </div>

            <div className="overflow-x-auto">
              {isApprovedSansa&&selected.rule_values.length===0&&<p className="p-6 text-slate-600">คะแนนรายข้ออยู่ในนิยาม 0/2/4 กลางและไม่แก้ผ่านตารางช่วงคะแนนหน้านี้</p>}
              {isLegacySansa&&<p className="m-5 rounded-xl bg-amber-50 p-4 text-amber-900">เวอร์ชันเดิมแสดงเพื่อการตรวจสอบประวัติเท่านั้น ไม่สามารถเปิดใช้หรือแก้เป็นเกณฑ์ปัจจุบันได้</p>}
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
                  {visibleRuleValues.map((rv) => (
                    <tr key={rv.id} className="border-t align-top">
                      <td className="px-4 py-3 font-mono">{rv.level_code}</td>
                      <td className="px-4 py-3">
                        <input
                          aria-label={`ชื่อระดับ ${rv.level_code}`}
                          title="ชื่อผลลัพธ์ที่แสดงเมื่อคะแนนอยู่ในช่วงนี้"
                          value={rv.level_name}
                          onChange={(e) => updateLocalValue(rv.id, { level_name: e.target.value })}
                          disabled={user?.role !== "admin" || isLegacySansa}
                          className="w-56 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <input
                          aria-label={`คะแนนต่ำสุด ${rv.level_code}`}
                          title="คะแนนต่ำสุดที่รวมอยู่ในระดับนี้"
                          value={rv.min_score ?? ""}
                          onChange={(e) => updateLocalValue(rv.id, { min_score: e.target.value })}
                          disabled={user?.role !== "admin" || isLegacySansa}
                          className="w-24 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <input
                          aria-label={`คะแนนสูงสุด ${rv.level_code}`}
                          title="คะแนนสูงสุดที่รวมอยู่ในระดับนี้"
                          value={rv.max_score ?? ""}
                          onChange={(e) => updateLocalValue(rv.id, { max_score: e.target.value })}
                          disabled={user?.role !== "admin" || isLegacySansa}
                          className="w-24 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <textarea
                          aria-label={`คำแนะนำ ${rv.level_code}`}
                          title="คำแนะนำที่แสดงแก่ผู้ทำแบบประเมินในระดับนี้"
                          value={rv.advice_text ?? ""}
                          onChange={(e) => updateLocalValue(rv.id, { advice_text: e.target.value })}
                          disabled={user?.role !== "admin" || isLegacySansa}
                          className="w-96 min-h-20 px-3 py-2 border-2 border-gray-200 rounded-lg disabled:bg-gray-50"
                        />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => saveValue(rv.id)}
                          disabled={user?.role !== "admin" || isLegacySansa || savingId !== null}
                          className="text-primary-600 hover:text-primary-700 font-medium disabled:opacity-50"
                        >
                          {savingId === rv.id ? "กำลังบันทึก..." : "บันทึก"}
                        </button>
                      </td>
                    </tr>
                  ))}
                  {visibleRuleValues.length === 0 && search.trim() && <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">ไม่พบกฎคะแนนที่ตรงกับ “{search}”</td></tr>}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
