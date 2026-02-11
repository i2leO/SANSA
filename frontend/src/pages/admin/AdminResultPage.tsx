import apiClient from "@/lib/api";
import AdminLayout from "@/pages/admin/AdminLayout";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

interface SANSAResult {
  id: number;
  screening_total: number;
  diet_total: number;
  total_score: number;
  result_level: string;
  completed_at: string;
}

function getErrorDetail(err: unknown, fallback: string) {
  if (typeof err === "object" && err !== null) {
    const anyErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = anyErr.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  return fallback;
}

export default function AdminResultPage() {
  const { visitId } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState<SANSAResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const response = await apiClient.get<SANSAResult>(`/sansa/visit/${visitId}`);
        setResult(response.data);
      } catch (err: unknown) {
        setError(getErrorDetail(err, "ไม่สามารถโหลดผลการประเมินได้"));
      } finally {
        setLoading(false);
      }
    };

    if (visitId) {
      fetchResult();
    }
  }, [visitId]);

  const getResultColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case "normal":
      case "ปกติ":
        return "from-green-500 to-teal-600";
      case "at-risk":
      case "เสี่ยง":
        return "from-yellow-500 to-orange-600";
      case "malnourished":
      case "ขาดสารอาหาร":
        return "from-red-500 to-pink-600";
      default:
        return "from-gray-500 to-gray-600";
    }
  };

  const getResultEmoji = (level: string) => {
    switch (level?.toLowerCase()) {
      case "normal":
      case "ปกติ":
        return "✅";
      case "at-risk":
      case "เสี่ยง":
        return "⚠️";
      case "malnourished":
      case "ขาดสารอาหาร":
        return "⚠️";
      default:
        return "📊";
    }
  };

  const getRecommendation = (level: string) => {
    switch (level?.toLowerCase()) {
      case "normal":
      case "ปกติ":
        return "สถานะโภชนาการอยู่ในเกณฑ์ดี ควรรักษาพฤติกรรมการกินอาหารและการใช้ชีวิตที่ดีต่อไป";
      case "at-risk":
      case "เสี่ยง":
        return "มีความเสี่ยงต่อภาวะทุพโภชนาการ แนะนำให้ปรับปรุงพฤติกรรมการกินอาหาร และปรึกษานักโภชนาการหรือแพทย์";
      case "malnourished":
      case "ขาดสารอาหาร":
        return "อาจมีภาวะทุพโภชนาการ ควรปรึกษานักโภชนาการหรือแพทย์โดยเร็วเพื่อรับคำแนะนำที่เหมาะสม";
      default:
        return "ผลการประเมินได้รับการบันทึกเรียบร้อยแล้ว";
    }
  };

  return (
    <AdminLayout title={`ผลการประเมิน (Visit ${visitId ?? "-"})`}>
      {loading ? (
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center">
            <div className="text-6xl mb-4">⏳</div>
            <p className="text-xl text-gray-600">กำลังโหลดผลการประเมิน...</p>
          </div>
        </div>
      ) : error || !result ? (
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md">
          <div className="text-6xl mb-4 text-center">❌</div>
          <h1 className="text-2xl font-bold text-red-600 mb-4 text-center">เกิดข้อผิดพลาด</h1>
          <p className="text-gray-600 mb-6 text-center">{error}</p>
          <button
            onClick={() => navigate("/admin/respondents")}
            className="w-full py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 font-semibold"
          >
            กลับไปหน้ารายการผู้เข้าร่วม
          </button>
        </div>
      ) : (
        <div className="max-w-4xl">
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-sm text-gray-600">Visit ID</div>
                <div className="font-mono font-semibold text-gray-800">{visitId}</div>
              </div>
              <button
                onClick={() => navigate("/admin/respondents")}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                กลับไปรายการผู้เข้าร่วม →
              </button>
            </div>

            <div className="text-center mt-6">
              <div className="text-7xl mb-4">{getResultEmoji(result.result_level)}</div>
              <h1 className="text-4xl font-bold text-primary-700 mb-2">ผลการประเมิน SANSA</h1>
              <p className="text-gray-600">มุมมองสำหรับเจ้าหน้าที่/แอดมิน</p>
            </div>
          </div>

          <div
            className={`bg-gradient-to-br ${getResultColor(
              result.result_level,
            )} rounded-2xl shadow-xl p-8 mb-6 text-white`}
          >
            <h2 className="text-3xl font-bold mb-6 text-center">คะแนน</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-6 text-center">
                <div className="text-5xl font-bold mb-2">{result.screening_total}</div>
                <div className="text-sm opacity-90">คะแนนคัดกรอง</div>
              </div>

              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-6 text-center">
                <div className="text-5xl font-bold mb-2">{result.diet_total}</div>
                <div className="text-sm opacity-90">คะแนนพฤติกรรม</div>
              </div>

              <div className="bg-white/20 backdrop-blur-sm rounded-xl p-6 text-center">
                <div className="text-5xl font-bold mb-2">{result.total_score}</div>
                <div className="text-sm opacity-90">คะแนนรวม</div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 text-center">
              <div className="text-2xl font-bold text-gray-800 mb-2">
                สถานะโภชนาการ: <span className="text-gray-900">{result.result_level}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-start gap-4">
              <div className="text-4xl">💡</div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-primary-700 mb-3">คำแนะนำ</h3>
                <p className="text-gray-700 text-lg leading-relaxed">
                  {getRecommendation(result.result_level)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
