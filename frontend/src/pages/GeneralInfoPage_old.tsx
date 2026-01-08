import apiClient from "@/lib/api";
import { Respondent, Sex, VisitCreate } from "@/types";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { z } from "zod";

const generalInfoSchema = z.object({
  age: z.number().min(0).max(150).optional(),
  sex: z.nativeEnum(Sex).optional(),
  education_level: z.string().optional(),
  income_range: z.string().optional(),
  occupation: z.string().optional(),
  marital_status: z.string().optional(),
  living_arrangement: z.string().optional(),
});

type GeneralInfoForm = z.infer<typeof generalInfoSchema>;

export default function GeneralInfoPage() {
  const { respondentCode } = useParams<{ respondentCode: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [respondent, setRespondent] = useState<Respondent | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<GeneralInfoForm>({
    resolver: zodResolver(generalInfoSchema),
  });

  useEffect(() => {
    // Fetch existing respondent data
    const fetchRespondent = async () => {
      try {
        const response = await apiClient.get<Respondent>(`/respondents/${respondentCode}`);
        setRespondent(response.data);

        // Pre-fill form if data exists
        if (response.data.age) setValue("age", response.data.age);
        if (response.data.sex) setValue("sex", response.data.sex as Sex);
        if (response.data.education_level)
          setValue("education_level", response.data.education_level);
        if (response.data.income_range) setValue("income_range", response.data.income_range);
        if (response.data.occupation) setValue("occupation", response.data.occupation);
        if (response.data.marital_status) setValue("marital_status", response.data.marital_status);
        if (response.data.living_arrangement)
          setValue("living_arrangement", response.data.living_arrangement);
      } catch (err) {
        setError("Failed to load respondent data");
      }
    };

    if (respondentCode) {
      fetchRespondent();
    }
  }, [respondentCode, setValue]);

  const onSubmit = async (data: GeneralInfoForm) => {
    setLoading(true);
    setError(null);

    try {
      // Update respondent info
      if (respondent) {
        await apiClient.put(`/respondents/${respondent.id}`, data);
      }

      // Create visit
      const visitData: VisitCreate = {
        respondent_id: respondent!.id,
        visit_number: 1,
        visit_date: new Date().toISOString().split("T")[0],
        visit_type: "baseline",
      };

      await apiClient.post("/visits", visitData);

      // Navigate to SANSA form
      navigate(`/sansa/${respondentCode}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "Failed to save information");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">General Information</h1>
          <p className="text-gray-600">
            Participant Code: <span className="font-mono font-semibold">{respondentCode}</span>
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-xl shadow-lg p-8">
          <div className="space-y-6">
            {/* Age */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Age (years)</label>
              <input
                type="number"
                {...register("age", { valueAsNumber: true })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="Enter your age"
              />
              {errors.age && <p className="mt-1 text-sm text-red-600">{errors.age.message}</p>}
            </div>

            {/* Sex */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Sex</label>
              <select
                {...register("sex")}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select...</option>
                <option value={Sex.MALE}>Male</option>
                <option value={Sex.FEMALE}>Female</option>
                <option value={Sex.OTHER}>Other</option>
                <option value={Sex.PREFER_NOT_TO_SAY}>Prefer not to say</option>
              </select>
            </div>

            {/* Education Level */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Education Level</label>
              <select
                {...register("education_level")}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select...</option>
                <option value="primary">Primary School</option>
                <option value="secondary">Secondary School</option>
                <option value="high_school">High School</option>
                <option value="vocational">Vocational/Technical</option>
                <option value="bachelor">Bachelor's Degree</option>
                <option value="master">Master's Degree</option>
                <option value="doctorate">Doctorate</option>
              </select>
            </div>

            {/* Income Range */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Monthly Income Range</label>
              <select
                {...register("income_range")}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select...</option>
                <option value="under_10k">Under 10,000</option>
                <option value="10k_20k">10,000 - 20,000</option>
                <option value="20k_30k">20,000 - 30,000</option>
                <option value="30k_50k">30,000 - 50,000</option>
                <option value="50k_100k">50,000 - 100,000</option>
                <option value="over_100k">Over 100,000</option>
              </select>
            </div>

            {/* Occupation */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Occupation</label>
              <input
                type="text"
                {...register("occupation")}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="e.g., Teacher, Engineer, Retired"
              />
            </div>

            {/* Marital Status */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Marital Status</label>
              <select
                {...register("marital_status")}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select...</option>
                <option value="single">Single</option>
                <option value="married">Married</option>
                <option value="divorced">Divorced</option>
                <option value="widowed">Widowed</option>
              </select>
            </div>

            {/* Living Arrangement */}
            <div>
              <label className="block text-gray-700 font-medium mb-2">Living Arrangement</label>
              <select
                {...register("living_arrangement")}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select...</option>
                <option value="alone">Living alone</option>
                <option value="with_spouse">With spouse</option>
                <option value="with_family">With family</option>
                <option value="with_children">With children</option>
                <option value="nursing_home">Nursing home/care facility</option>
              </select>
            </div>
          </div>

          {/* Buttons */}
          <div className="mt-8 flex gap-4">
            <button
              type="button"
              onClick={() => navigate("/")}
              className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 font-semibold"
            >
              {loading ? "Saving..." : "Continue to Assessment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
