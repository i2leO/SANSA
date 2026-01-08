import apiClient from "@/lib/api";
import { RespondentCreate } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

const respondentSchema = z.object({
  respondent_code: z.string().optional(),
});

type RespondentForm = z.infer<typeof respondentSchema>;

export default function RespondentStartPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"new" | "existing">("new");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RespondentForm>({
    resolver: zodResolver(respondentSchema),
  });

  const handleNewRespondent = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.post<RespondentCreate>("/respondents", {});
      const respondentCode = response.data.respondent_code;
      navigate(`/general-info/${respondentCode}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "ไม่สามารถสร้างรหัสผู้เข้าร่วมได้");
    } finally {
      setLoading(false);
    }
  };

  const handleExistingRespondent = async (data: RespondentForm) => {
    if (!data.respondent_code) {
      setError("กรุณาใส่รหัสผู้เข้าร่วม");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Check if code exists
      const response = await apiClient.post("/respondents/check-code", {
        code: data.respondent_code,
      });

      if (response.data.exists) {
        navigate(`/general-info/${data.respondent_code}`);
      } else {
        setError("ไม่พบรหัสผู้เข้าร่วม กรุณาตรวจสอบและลองอีกครั้ง");
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "ไม่สามารถตรวจสอบรหัสผู้เข้าร่วมได้");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-primary-700 mb-2">เริ่มต้นใช้งาน</h1>
          <p className="text-gray-600">เลือกวิธีการเริ่มการประเมินของคุณ</p>
        </div>

        {/* Mode Selection */}
        <div className="max-w-2xl mx-auto">
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <button
              onClick={() => setMode("new")}
              className={`p-6 rounded-xl border-4 transition-all ${
                mode === "new"
                  ? "border-primary-600 bg-primary-50 shadow-lg"
                  : "border-gray-300 bg-white hover:border-primary-400"
              }`}
            >
              <div className="text-4xl mb-2">✨</div>
              <h3 className="text-xl font-semibold mb-2">ผู้เข้าร่วมใหม่</h3>
              <p className="text-gray-600 text-sm">สร้างรหัสไม่ระบุตัวตนใหม่เพื่อเริ่มการประเมิน</p>
            </button>

            <button
              onClick={() => setMode("existing")}
              className={`p-6 rounded-xl border-4 transition-all ${
                mode === "existing"
                  ? "border-primary-600 bg-primary-50 shadow-lg"
                  : "border-gray-300 bg-white hover:border-primary-400"
              }`}
            >
              <div className="text-4xl mb-2">🔑</div>
              <h3 className="text-xl font-semibold mb-2">ผู้เข้าร่วมเดิม</h3>
              <p className="text-gray-600 text-sm">ใช้รหัสผู้เข้าร่วมที่มีอยู่แล้ว</p>
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {/* New Participant */}
          {mode === "new" && (
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-primary-200">
              <h2 className="text-2xl font-semibold mb-4 text-primary-800">สร้างรหัสใหม่</h2>
              <p className="text-gray-600 mb-6">
                คลิกปุ่มด้านล่างเพื่อสร้างรหัสผู้เข้าร่วมแบบไม่ระบุตัวตน
                กรุณาบันทึกรหัสนี้ไว้สำหรับใช้งานในอนาคต
              </p>
              <button
                onClick={handleNewRespondent}
                disabled={loading}
                className="w-full py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold text-lg transition-colors shadow-md hover:shadow-lg"
              >
                {loading ? "กำลังสร้างรหัส..." : "สร้างรหัสของฉัน"}
              </button>
            </div>
          )}

          {/* Existing Participant */}
          {mode === "existing" && (
            <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-primary-200">
              <h2 className="text-2xl font-semibold mb-4 text-primary-800">ใส่รหัสของคุณ</h2>
              <form onSubmit={handleSubmit(handleExistingRespondent)} className="space-y-6">
                <div>
                  <label className="block text-gray-700 font-medium mb-2">รหัสผู้เข้าร่วม</label>
                  <input
                    type="text"
                    {...register("respondent_code")}
                    placeholder="เช่น RESABC12345"
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 uppercase"
                  />
                  {errors.respondent_code && (
                    <p className="mt-1 text-sm text-red-600">{errors.respondent_code.message}</p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold text-lg transition-colors shadow-md hover:shadow-lg"
                >
                  {loading ? "กำลังตรวจสอบ..." : "ดำเนินการต่อ"}
                </button>
              </form>
            </div>
          )}

          {/* Back Button */}
          <div className="mt-8 text-center">
            <button
              onClick={() => navigate("/")}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              ← กลับไปหน้าหลัก
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
