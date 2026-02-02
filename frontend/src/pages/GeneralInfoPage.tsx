import apiClient from "@/lib/api";
import { Respondent, VisitCreate } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

// Complete General Information Schema - 10 fields from Page 2
const generalInfoSchema = z.object({
  status: z.enum(["elderly", "caregiver"]).optional(), // ผู้สูงอายุ/ผู้ดูแล
  age: z.number().min(0).max(150).optional(),
  sex: z.enum(["male", "female"]).optional(),
  education_level: z.string().optional(),
  marital_status: z.string().optional(),
  monthly_income: z.string().optional(),
  income_sources: z.array(z.string()).optional(), // Multiple selections
  chronic_diseases: z
    .object({
      diseases: z.array(z.string()),
      other: z.string().optional(),
    })
    .optional(),
  living_arrangement: z.string().optional(),
});

type GeneralInfoForm = z.infer<typeof generalInfoSchema>;

export default function GeneralInfoPage() {
  const { respondentCode } = useParams<{ respondentCode: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [respondent, setRespondent] = useState<Respondent | null>(null);
  const [incomeSourcesChecked, setIncomeSourcesChecked] = useState<string[]>([]);
  const [chronicDiseasesChecked, setChronicDiseasesChecked] = useState<string[]>([]);
  const [chronicDiseasesOther, setChronicDiseasesOther] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<GeneralInfoForm>({
    resolver: zodResolver(generalInfoSchema),
  });

  useEffect(() => {
    const fetchRespondent = async () => {
      try {
        const response = await apiClient.get<Respondent>(`/respondents/${respondentCode}`);
        setRespondent(response.data);

        // Pre-fill form if data exists
        if (response.data.status)
          setValue("status", response.data.status as "elderly" | "caregiver");
        if (response.data.age) setValue("age", response.data.age);
        if (response.data.sex) setValue("sex", response.data.sex as "male" | "female");
        if (response.data.education_level)
          setValue("education_level", response.data.education_level);
        if (response.data.marital_status) setValue("marital_status", response.data.marital_status);
        if (response.data.monthly_income) setValue("monthly_income", response.data.monthly_income);
        if (response.data.income_sources) {
          setValue("income_sources", response.data.income_sources);
          setIncomeSourcesChecked(response.data.income_sources);
        }
        if (response.data.chronic_diseases) {
          setValue("chronic_diseases", response.data.chronic_diseases);
          setChronicDiseasesChecked(response.data.chronic_diseases.diseases || []);
          setChronicDiseasesOther(response.data.chronic_diseases.other || "");
        }
        if (response.data.living_arrangement)
          setValue("living_arrangement", response.data.living_arrangement);
      } catch (err) {
        setError("ไม่สามารถโหลดข้อมูลผู้ตอบได้");
      }
    };

    if (respondentCode) {
      fetchRespondent();
    }
  }, [respondentCode, setValue]);

  const handleIncomeSourceChange = (source: string, checked: boolean) => {
    const updated = checked
      ? [...incomeSourcesChecked, source]
      : incomeSourcesChecked.filter((s) => s !== source);
    setIncomeSourcesChecked(updated);
    setValue("income_sources", updated);
  };

  const handleChronicDiseaseChange = (disease: string, checked: boolean) => {
    const updated = checked
      ? [...chronicDiseasesChecked, disease]
      : chronicDiseasesChecked.filter((d) => d !== disease);
    setChronicDiseasesChecked(updated);
    setValue("chronic_diseases", {
      diseases: updated,
      other: chronicDiseasesOther,
    });
  };

  const onSubmit = async (data: GeneralInfoForm) => {
    setLoading(true);
    setError(null);

    try {
      // Update respondent info
      if (respondent) {
        await apiClient.put(`/respondents/${respondent.id}`, data);
      }

      // Check if visit exists, if not create one
      try {
        const visitsResponse = await apiClient.get(`/visits/respondent/${respondent!.id}`);
        if (visitsResponse.data.length === 0) {
          // Create visit only if none exists
          const visitData: VisitCreate = {
            respondent_id: respondent!.id,
            visit_number: 1,
            visit_date: new Date().toISOString().split("T")[0],
            visit_type: "baseline",
          };
          await apiClient.post("/visits", visitData);
        }
      } catch (visitErr) {
        // If checking visits fails, try to create one anyway
        console.log("Could not check existing visits, creating new one");
      }

      // Navigate to SANSA form
      navigate(`/sansa/${respondentCode}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "ไม่สามารถบันทึกข้อมูลได้");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center">
              <span className="text-3xl">📋</span>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-800">ข้อมูลทั่วไป</h1>
              <p className="text-gray-600 mt-1">General Information</p>
            </div>
          </div>
          <div className="border-t border-gray-200 pt-4 mt-4">
            <p className="text-gray-700">
              รหัสผู้เข้าร่วม:{" "}
              <span className="font-mono font-bold text-blue-600 text-xl">{respondentCode}</span>
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-5 bg-red-50 border-l-4 border-red-500 rounded-lg">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl shadow-xl p-8">
          <div className="space-y-8">
            {/* 1. Status - สถานะ */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                1. สถานะ <span className="text-red-500">*</span>
              </label>
              <div className="space-y-2">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer">
                  <input
                    type="radio"
                    value="elderly"
                    {...register("status")}
                    className="w-5 h-5 text-blue-600"
                  />
                  <span className="ml-3 text-gray-700 font-medium">ผู้สูงอายุ</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer">
                  <input
                    type="radio"
                    value="caregiver"
                    {...register("status")}
                    className="w-5 h-5 text-blue-600"
                  />
                  <span className="ml-3 text-gray-700 font-medium">ผู้ดูแลผู้สูงอายุ</span>
                </label>
              </div>
            </div>

            {/* 2. Age - อายุ */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                2. อายุ (ปี) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                {...register("age", { valueAsNumber: true })}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="กรอกอายุของท่าน"
              />
              {errors.age && <p className="mt-2 text-sm text-red-600">{errors.age.message}</p>}
            </div>

            {/* 3. Sex - เพศ */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                3. เพศ <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer">
                  <input
                    type="radio"
                    value="male"
                    {...register("sex")}
                    className="w-5 h-5 text-blue-600"
                  />
                  <span className="ml-3 text-gray-700 font-medium">ชาย</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer">
                  <input
                    type="radio"
                    value="female"
                    {...register("sex")}
                    className="w-5 h-5 text-blue-600"
                  />
                  <span className="ml-3 text-gray-700 font-medium">หญิง</span>
                </label>
              </div>
            </div>

            {/* 4. Education Level - ระดับการศึกษา */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">4. ระดับการศึกษา</label>
              <select
                {...register("education_level")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                <option value="no_education">ไม่ได้เรียนหนังสือ</option>
                <option value="primary">ประถมศึกษา</option>
                <option value="secondary">มัธยมศึกษา</option>
                <option value="vocational">ปวช./ปวส.</option>
                <option value="bachelor">ปริญญาตรี</option>
                <option value="graduate">สูงกว่าปริญญาตรี</option>
              </select>
            </div>

            {/* 5. Marital Status - สถานภาพการสมรส */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                5. สถานภาพการสมรส
              </label>
              <select
                {...register("marital_status")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                <option value="single">โสด</option>
                <option value="married">สมรส</option>
                <option value="divorced">หย่าร้าง</option>
                <option value="widowed">หม้าย</option>
              </select>
            </div>

            {/* 6. Monthly Income - รายได้ต่อเดือน */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                6. รายได้ต่อเดือน (บาท)
              </label>
              <select
                {...register("monthly_income")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                <option value="under_5k">น้อยกว่า 5,000</option>
                <option value="5k_10k">5,000 - 10,000</option>
                <option value="10k_20k">10,000 - 20,000</option>
                <option value="over_20k">มากกว่า 20,000</option>
              </select>
            </div>

            {/* 7. Income Sources - แหล่งรายได้ (Multiple) */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                7. แหล่งรายได้ (เลือกได้มากกว่า 1 ข้อ)
              </label>
              <div className="space-y-2">
                {["เงินเดือน/ค่าจ้าง", "เงินบำนาญ", "ลูกหลานให้", "ดอกเบี้ยเงินฝาก", "อื่นๆ"].map(
                  (source) => (
                    <label
                      key={source}
                      className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={incomeSourcesChecked.includes(source)}
                        onChange={(e) => handleIncomeSourceChange(source, e.target.checked)}
                        className="w-5 h-5 text-blue-600 rounded"
                      />
                      <span className="ml-3 text-gray-700 font-medium">{source}</span>
                    </label>
                  )
                )}
              </div>
            </div>

            {/* 8. Chronic Diseases - โรคประจำตัว (Multiple + Other) */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                8. โรคประจำตัว (เลือกได้มากกว่า 1 ข้อ)
              </label>
              <div className="space-y-2">
                {["เบาหวาน", "ความดันโลหิตสูง", "ไขมันในเลือดสูง", "โรคหัวใจ", "ไม่มี"].map(
                  (disease) => (
                    <label
                      key={disease}
                      className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={chronicDiseasesChecked.includes(disease)}
                        onChange={(e) => handleChronicDiseaseChange(disease, e.target.checked)}
                        className="w-5 h-5 text-blue-600 rounded"
                      />
                      <span className="ml-3 text-gray-700 font-medium">{disease}</span>
                    </label>
                  )
                )}
                <div className="mt-3">
                  <label className="block text-gray-700 mb-2">อื่นๆ (ระบุ)</label>
                  <input
                    type="text"
                    value={chronicDiseasesOther}
                    onChange={(e) => {
                      setChronicDiseasesOther(e.target.value);
                      setValue("chronic_diseases", {
                        diseases: chronicDiseasesChecked,
                        other: e.target.value,
                      });
                    }}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
                    placeholder="โปรดระบุ..."
                  />
                </div>
              </div>
            </div>

            {/* 9. Living Arrangement - ท่านอาศัยอยู่กับ */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                9. ท่านอาศัยอยู่กับ
              </label>
              <select
                {...register("living_arrangement")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                <option value="alone">อยู่คนเดียว</option>
                <option value="with_spouse">อยู่กับคู่สมรส</option>
                <option value="with_children">อยู่กับลูกหลาน</option>
                <option value="with_relatives">อยู่กับญาติ</option>
              </select>
            </div>
          </div>

          {/* Buttons */}
          <div className="mt-10 flex gap-4">
            <button
              type="button"
              onClick={() => navigate("/")}
              className="flex-1 py-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 font-bold text-lg transition-colors"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 font-bold text-lg transition-all shadow-lg"
            >
              {loading ? "กำลังบันทึก..." : "ดำเนินการต่อ →"}
            </button>
          </div>
        </form>

        {/* Progress Indicator */}
        <div className="mt-8 text-center text-gray-600">
          <p className="text-sm">ขั้นตอนที่ 1 จาก 3 | ข้อมูลทั่วไป</p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full"
              style={{ width: "33%" }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
