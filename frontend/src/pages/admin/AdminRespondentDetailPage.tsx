import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { Respondent, Visit } from "@/types";
import * as QRCode from "qrcode";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type OptionalFetchState<T> = {
  data: T | null;
  status: "idle" | "loading" | "ok" | "missing" | "error";
};

type FetchMap = Record<number, OptionalFetchState<unknown>>;

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

function getHttpStatus(err: unknown): number | undefined {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { status?: unknown } };
    const status = anyErr.response?.status;
    return typeof status === "number" ? status : undefined;
  }
  return undefined;
}

export default function AdminRespondentDetailPage() {
  const { respondentCode } = useParams();
  const navigate = useNavigate();

  const [respondent, setRespondent] = useState<Respondent | null>(null);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [sansaByVisitId, setSansaByVisitId] = useState<FetchMap>({});
  const [mnaByVisitId, setMnaByVisitId] = useState<FetchMap>({});
  const [biaByVisitId, setBiaByVisitId] = useState<FetchMap>({});

  const [qrUrl, setQrUrl] = useState<string | null>(null);
  const [qrDataUrl, setQrDataUrl] = useState<string | null>(null);
  const [qrError, setQrError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!respondentCode) return;

    const url = `${window.location.origin}/sansa/${encodeURIComponent(respondentCode)}`;
    setQrUrl(url);
    setQrDataUrl(null);
    setQrError(null);
    setCopyStatus(null);

    let cancelled = false;
    const toDataURLFn: ((text: string, opts?: unknown) => Promise<string>) | undefined = (
      QRCode as unknown as { toDataURL?: (text: string, opts?: unknown) => Promise<string> }
    ).toDataURL;

    if (!toDataURLFn) {
      setQrError("ไม่สามารถสร้าง QR ได้ (ไม่พบฟังก์ชัน toDataURL)");
      return;
    }

    toDataURLFn(url, { margin: 1, width: 220 })
      .then((data) => {
        if (!cancelled) setQrDataUrl(data);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        const message =
          typeof e === "object" &&
          e !== null &&
          "message" in e &&
          typeof (e as { message: unknown }).message === "string"
            ? (e as { message: string }).message
            : "สร้าง QR ไม่สำเร็จ";
        setQrError(message);
      });

    return () => {
      cancelled = true;
    };
  }, [respondentCode]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const r = await apiClient.get<Respondent>(`/respondents/${respondentCode}`);
        setRespondent(r.data);

        const v = await apiClient.get<Visit[]>(`/visits/respondent/${r.data.id}`);
        setVisits(v.data);

        // Preload instrument presence (best-effort)
        const visitIds = v.data.map((x) => x.id);
        const init: FetchMap = {};
        for (const id of visitIds) {
          init[id] = { data: null, status: "loading" };
        }
        setSansaByVisitId(init);
        setMnaByVisitId(init);
        setBiaByVisitId(init);

        await Promise.all(
          visitIds.map(async (visitId) => {
            const fetchOne = async (path: string, setter: Dispatch<SetStateAction<FetchMap>>) => {
              try {
                const res = await apiClient.get<unknown>(path);
                setter((prev) => ({ ...prev, [visitId]: { data: res.data, status: "ok" } }));
              } catch (e: unknown) {
                const status = getHttpStatus(e) === 404 ? "missing" : "error";
                setter((prev) => ({ ...prev, [visitId]: { data: null, status } }));
              }
            };

            await Promise.all([
              fetchOne(`/sansa/visit/${visitId}`, setSansaByVisitId),
              fetchOne(`/mna/visit/${visitId}`, setMnaByVisitId),
              fetchOne(`/bia/visit/${visitId}`, setBiaByVisitId),
            ]);
          }),
        );
      } catch (err: unknown) {
        setError(getErrorDetail(err, "ไม่สามารถโหลดข้อมูลผู้เข้าร่วมได้"));
      } finally {
        setLoading(false);
      }
    };

    if (respondentCode) {
      load();
    }
  }, [respondentCode]);

  return (
    <AdminLayout title="รายละเอียดผู้เข้าร่วม">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">รายละเอียดผู้เข้าร่วม</h1>
          <p className="text-gray-600">
            รหัส: <span className="font-mono font-semibold">{respondentCode}</span>
          </p>
        </div>
        <button
          onClick={() => navigate("/admin/respondents")}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          ← กลับรายการ
        </button>
      </div>

      {loading ? (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-200 text-gray-600">
          กำลังโหลด...
        </div>
      ) : error ? (
        <div className="bg-white rounded-xl shadow p-6 border border-red-200 text-red-700">
          {error}
        </div>
      ) : !respondent ? (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-200 text-gray-600">
          ไม่พบข้อมูล
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow p-6 border border-gray-200 mb-6">
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-gray-500">อายุ</div>
                <div className="font-semibold">{respondent.age ?? "-"}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">เพศ</div>
                <div className="font-semibold">{respondent.sex ?? "-"}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">ติดต่อ</div>
                <div className="font-semibold">{respondent.email || respondent.phone || "-"}</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-6 border border-gray-200 mb-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-800">QR สำหรับผู้เข้าร่วมเดิม</h2>
                <p className="text-sm text-gray-600">
                  สแกนเพื่อเข้าแบบประเมินได้ทันที (ใช้ได้หลังมี visit ครั้งแรกแล้ว)
                </p>

                {visits.length === 0 && (
                  <div className="mt-3 text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg p-3">
                    ยังไม่มี visit แต่สามารถดาวน์โหลด QR ได้เลย
                    (ผู้ใช้สแกนแล้วจะเริ่มทำครั้งแรกได้ทันที)
                  </div>
                )}

                {qrUrl && (
                  <div className="mt-3">
                    <div className="text-xs text-gray-500 mb-1">ลิงก์</div>
                    <div className="font-mono text-xs break-all text-gray-800">{qrUrl}</div>
                    <div className="mt-2 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={async () => {
                          if (!qrUrl) return;
                          try {
                            await navigator.clipboard.writeText(qrUrl);
                            setCopyStatus("คัดลอกลิงก์แล้ว");
                          } catch {
                            setCopyStatus("คัดลอกไม่สำเร็จ (อาจไม่อนุญาต clipboard)");
                          }
                        }}
                        className="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm font-medium"
                      >
                        คัดลอกลิงก์
                      </button>

                      {qrDataUrl && (
                        <a
                          href={qrDataUrl}
                          download={`respondent_${respondentCode}_qr.png`}
                          className="px-3 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 text-sm font-medium"
                        >
                          ดาวน์โหลด QR
                        </a>
                      )}

                      {copyStatus && <div className="text-sm text-gray-600">{copyStatus}</div>}
                    </div>
                  </div>
                )}
              </div>

              <div className="shrink-0">
                {qrDataUrl ? (
                  <img
                    src={qrDataUrl}
                    alt="QR code"
                    className="w-[220px] h-[220px] rounded-lg border border-gray-200 bg-white"
                  />
                ) : qrError ? (
                  <div className="w-[220px] rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                    {qrError}
                  </div>
                ) : (
                  <div className="w-[220px] h-[220px] rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
                    กำลังสร้าง QR...
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-800">Visits</h2>
            </div>

            {visits.length === 0 ? (
              <div className="p-6 text-gray-600">ยังไม่มี visit</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-white">
                    <tr>
                      <th className="text-left px-4 py-3 text-gray-700">Visit ID</th>
                      <th className="text-left px-4 py-3 text-gray-700">วันที่</th>
                      <th className="text-left px-4 py-3 text-gray-700">SANSA</th>
                      <th className="text-left px-4 py-3 text-gray-700">MNA</th>
                      <th className="text-left px-4 py-3 text-gray-700">BIA</th>
                      <th className="text-right px-4 py-3 text-gray-700">เปิดผล</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visits.map((v) => {
                      const sansa = sansaByVisitId[v.id];
                      const mna = mnaByVisitId[v.id];
                      const bia = biaByVisitId[v.id];

                      const badge = (s?: OptionalFetchState<unknown>) => {
                        if (!s || s.status === "idle" || s.status === "loading")
                          return "กำลังเช็ก...";
                        if (s.status === "ok") return "มี";
                        if (s.status === "missing") return "ไม่มี";
                        return "ผิดพลาด";
                      };

                      const badgeClass = (s?: OptionalFetchState<unknown>) => {
                        if (!s || s.status === "idle" || s.status === "loading")
                          return "bg-gray-100 text-gray-700";
                        if (s.status === "ok") return "bg-green-100 text-green-800";
                        if (s.status === "missing") return "bg-yellow-50 text-yellow-800";
                        return "bg-red-50 text-red-800";
                      };

                      return (
                        <tr key={v.id} className="border-t">
                          <td className="px-4 py-3 font-mono">{v.id}</td>
                          <td className="px-4 py-3">{v.visit_date}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded ${badgeClass(sansa)}`}>
                              {badge(sansa)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded ${badgeClass(mna)}`}>
                              {badge(mna)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded ${badgeClass(bia)}`}>
                              {badge(bia)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button
                              onClick={() => navigate(`/admin/results/${v.id}`)}
                              className="text-primary-600 hover:text-primary-700 font-medium"
                            >
                              SANSA Result →
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </AdminLayout>
  );
}
