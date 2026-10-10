import apiClient from "@/lib/api";
import { chronicDiseaseOptions, demographicOptions, incomeSourceOptions } from "@/lib/researchLabels";
import { Respondent, VisitCreate } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

// Complete General Information Schema - 10 fields from Page 2
const generalInfoSchema = z.object({
  status: z.enum(["elderly", "caregiver"]),
  age: z.number({ invalid_type_error: "กรุณากรอกอายุ" }).min(60, "อายุต้องไม่น้อยกว่า 60 ปี").max(150),
  sex: z.enum(["male", "female"]),
  education_level: z.enum(["no_education", "primary", "secondary", "vocational", "bachelor", "graduate"]),
  marital_status: z.enum(["single", "married", "widowed", "divorced"]),
  monthly_income: z.enum(["under_10k", "10k_20k", "20k_30k", "over_30k"]),
  income_sources: z.array(z.enum(["old_age", "pension", "spouse", "children", "work"])),
  chronic_diseases: z
    .object({
      diseases: z.array(z.enum(["dm", "ht", "dlp", "ckd", "ca"])),
      other: z.string(),
    })
    ,
  living_arrangement: z.enum(["alone", "with_spouse", "with_friends", "with_family"]),
});

type GeneralInfoForm = z.infer<typeof generalInfoSchema>;
type IncomeSource = GeneralInfoForm["income_sources"][number];
type ChronicDisease = GeneralInfoForm["chronic_diseases"]["diseases"][number];

export default function GeneralInfoPage() {
  const { respondentCode } = useParams<{ respondentCode: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [respondent, setRespondent] = useState<Respondent | null>(null);
  const [incomeSourcesChecked, setIncomeSourcesChecked] = useState<IncomeSource[]>([]);
  const [chronicDiseasesChecked, setChronicDiseasesChecked] = useState<ChronicDisease[]>([]);
  const [chronicDiseasesOther, setChronicDiseasesOther] = useState("");
  const [incomeAnswered, setIncomeAnswered] = useState(false);
  const [diseaseAnswered, setDiseaseAnswered] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<GeneralInfoForm>({
    resolver: zodResolver(generalInfoSchema),
    defaultValues: { income_sources: [], chronic_diseases: { diseases: [], other: "" } },
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
        if (response.data.education_level && response.data.education_level in demographicOptions.education_level)
          setValue("education_level", response.data.education_level as GeneralInfoForm["education_level"]);
        if (response.data.marital_status && response.data.marital_status in demographicOptions.marital_status)
          setValue("marital_status", response.data.marital_status as GeneralInfoForm["marital_status"]);
        if (response.data.monthly_income && response.data.monthly_income in demographicOptions.monthly_income)
          setValue("monthly_income", response.data.monthly_income as GeneralInfoForm["monthly_income"]);
        if (response.data.income_sources) {
          const sources = response.data.income_sources.filter((item): item is IncomeSource => item in incomeSourceOptions);
          setValue("income_sources", sources);
          setIncomeSourcesChecked(sources);
          setIncomeAnswered(true);
        }
        if (response.data.chronic_diseases) {
          const diseases = Array.isArray(response.data.chronic_diseases.diseases)
            ? response.data.chronic_diseases.diseases.filter((item): item is ChronicDisease => typeof item === "string" && item in chronicDiseaseOptions)
            : [];
          const other =
            typeof response.data.chronic_diseases.other === "string"
              ? response.data.chronic_diseases.other
              : "";
          setValue("chronic_diseases", { diseases, other });
          setChronicDiseasesChecked(diseases);
          setChronicDiseasesOther(other);
          setDiseaseAnswered(true);
        }
        if (response.data.living_arrangement && response.data.living_arrangement in demographicOptions.living_arrangement)
          setValue("living_arrangement", response.data.living_arrangement as GeneralInfoForm["living_arrangement"]);
      } catch (err) {
        setError("ไม่สามารถโหลดข้อมูลผู้ตอบได้");
      }
    };

    if (respondentCode) {
      fetchRespondent();
    }
  }, [respondentCode, setValue]);

  const handleIncomeSourceChange = (source: IncomeSource, checked: boolean) => {
    setIncomeAnswered(true);
    const updated = checked
      ? [...incomeSourcesChecked, source]
      : incomeSourcesChecked.filter((s) => s !== source);
    setIncomeSourcesChecked(updated);
    setValue("income_sources", updated);
  };

  const handleChronicDiseaseChange = (disease: ChronicDisease, checked: boolean) => {
    setDiseaseAnswered(true);
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
    if (!incomeAnswered || !diseaseAnswered) {
      setError("กรุณาตอบแหล่งรายได้และโรคประจำตัว โดยเลือก ‘ไม่มี’ หากไม่มีข้อมูลในส่วนนั้น");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      // Update respondent info
      if (respondent) {
        await apiClient.put(`/respondents/${respondent.id}/profile`, data);
      }

      // Create a first visit only after the complete profile was accepted.
      const visitsResponse = await apiClient.get(`/visits/respondent/${respondent!.id}`);
      if (visitsResponse.data.length === 0) {
        const visitData: VisitCreate = {
          respondent_id: respondent!.id,
          visit_number: 1,
          visit_date: new Date().toISOString().split("T")[0],
          visit_type: "baseline",
        };
        await apiClient.post("/visits", visitData);
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
        <form onSubmit={handleSubmit(onSubmit, () => setError("กรุณากรอกข้อมูลทั่วไปที่มีเครื่องหมาย * ให้ครบ"))} className="bg-white rounded-2xl shadow-xl p-8">
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
              <label className="block text-gray-800 font-bold text-lg mb-3">4. ระดับการศึกษา <span className="text-red-500">*</span></label>
              <select
                {...register("education_level")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                {Object.entries(demographicOptions.education_level).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>

            {/* 5. Marital Status - สถานภาพการสมรส */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                5. สถานภาพการสมรส <span className="text-red-500">*</span>
              </label>
              <select
                {...register("marital_status")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                {Object.entries(demographicOptions.marital_status).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>

            {/* 6. Monthly Income - รายได้ต่อเดือน */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                6. รายได้ต่อเดือน (บาท) <span className="text-red-500">*</span>
              </label>
              <select
                {...register("monthly_income")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                {Object.entries(demographicOptions.monthly_income).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>

            {/* 7. Income Sources - แหล่งรายได้ (Multiple) */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                7. แหล่งรายได้ (เลือกได้มากกว่า 1 ข้อ) <span className="text-red-500">*</span>
              </label>
              <div className="space-y-2">
                {Object.entries(incomeSourceOptions).map(
                  ([source, label]) => (
                    <label
                      key={source}
                      className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={incomeSourcesChecked.includes(source as IncomeSource)}
                        onChange={(e) => handleIncomeSourceChange(source as IncomeSource, e.target.checked)}
                        className="w-5 h-5 text-blue-600 rounded"
                      />
                      <span className="ml-3 text-gray-700 font-medium">{label}</span>
                    </label>
                  ),
                )}
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer">
                  <input type="checkbox" checked={incomeAnswered && incomeSourcesChecked.length === 0} onChange={() => { setIncomeAnswered(true); setIncomeSourcesChecked([]); setValue("income_sources", []); }} className="w-5 h-5 text-blue-600 rounded" />
                  <span className="ml-3 text-gray-700 font-medium">ไม่มีแหล่งรายได้ตามรายการ</span>
                </label>
              </div>
            </div>

            {/* 8. Chronic Diseases - โรคประจำตัว (Multiple + Other) */}
            <div>
              <label className="block text-gray-800 font-bold text-lg mb-3">
                8. โรคประจำตัว (เลือกได้มากกว่า 1 ข้อ) <span className="text-red-500">*</span>
              </label>
              <div className="space-y-2">
                {Object.entries(chronicDiseaseOptions).map(
                  ([disease, label]) => (
                    <label
                      key={disease}
                      className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={chronicDiseasesChecked.includes(disease as ChronicDisease)}
                        onChange={(e) => handleChronicDiseaseChange(disease as ChronicDisease, e.target.checked)}
                        className="w-5 h-5 text-blue-600 rounded"
                      />
                      <span className="ml-3 text-gray-700 font-medium">{label}</span>
                    </label>
                  ),
                )}
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl hover:border-blue-400 cursor-pointer">
                  <input type="checkbox" checked={diseaseAnswered && chronicDiseasesChecked.length === 0 && !chronicDiseasesOther.trim()} onChange={() => { setDiseaseAnswered(true); setChronicDiseasesChecked([]); setChronicDiseasesOther(""); setValue("chronic_diseases", { diseases: [], other: "" }); }} className="w-5 h-5 text-blue-600 rounded" />
                  <span className="ml-3 text-gray-700 font-medium">ไม่มีโรคประจำตัวตามรายการ</span>
                </label>
                <div className="mt-3">
                  <label className="block text-gray-700 mb-2">อื่นๆ (ระบุ)</label>
                  <input
                    type="text"
                    value={chronicDiseasesOther}
                    onChange={(e) => {
                      setDiseaseAnswered(true);
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
                9. ท่านอาศัยอยู่กับ <span className="text-red-500">*</span>
              </label>
              <select
                {...register("living_arrangement")}
                className="w-full px-5 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              >
                <option value="">เลือก...</option>
                {Object.entries(demographicOptions.living_arrangement).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
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
