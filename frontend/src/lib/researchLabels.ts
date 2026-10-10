// Display vocabulary only. Stored answers and score rules are not changed here.
export const demographicOptions: Record<string, Record<string, string>> = {
  status: { elderly: 'ผู้สูงอายุ', caregiver: 'ผู้ดูแล' },
  sex: { female: 'หญิง', male: 'ชาย' },
  education_level: { no_education: 'ไม่ได้เรียนหนังสือ', primary: 'ประถมศึกษา', secondary: 'มัธยมศึกษา', vocational: 'ปวช./ปวส.', bachelor: 'ปริญญาตรี', graduate: 'สูงกว่าปริญญาตรี' },
  marital_status: { single: 'โสด', married: 'สมรส', divorced: 'หย่าร้าง', widowed: 'หม้าย' },
  monthly_income: { under_10k: 'น้อยกว่า 10,000 บาท', '10k_20k': '10,000–20,000 บาท', '20k_30k': '20,001–30,000 บาท', over_30k: 'มากกว่า 30,000 บาท' },
  living_arrangement: { alone: 'อยู่คนเดียว', with_spouse: 'อยู่กับคู่สมรส', with_friends: 'อยู่กับเพื่อน', with_family: 'อยู่กับครอบครัว (คู่สมรส ญาติพี่น้อง บุตร)' },
};

export const incomeSourceOptions: Record<string, string> = {
  old_age: 'เบี้ยยังชีพผู้สูงอายุ', pension: 'บำเหน็จบำนาญ', spouse: 'คู่สมรส',
  children: 'บุตร', work: 'การทำงาน',
};

export const chronicDiseaseOptions: Record<string, string> = {
  dm: 'เบาหวาน', ht: 'ความดันโลหิตสูง', dlp: 'ไขมันในเลือดสูง',
  ckd: 'ไตเรื้อรัง', ca: 'มะเร็ง',
};

const historicalLabels: Record<string, Record<string, string>> = {
  bmi_category: { underweight: 'ผอม', normal: 'ปกติ', overweight: 'น้ำหนักเกิน', obese_1: 'อ้วนระดับ 1', obese_2: 'อ้วนระดับ 2' },
  monthly_income: { under_10k: 'น้อยกว่า 10,000 บาท', '20k_30k': '20,001–30,000 บาท', over_30k: 'มากกว่า 30,000 บาท' },
  living_arrangement: { with_family: 'อยู่กับครอบครัว', with_friends: 'อยู่กับเพื่อน' },
  income_sources: { oldage: 'เบี้ยยังชีพผู้สูงอายุ', old_age: 'เบี้ยยังชีพผู้สูงอายุ', pension: 'เงินบำนาญ', spouse: 'คู่สมรส', children: 'ลูกหลานให้', work: 'รายได้จากการทำงาน' },
  chronic_diseases: { dm: 'เบาหวาน', diabetes: 'เบาหวาน', ht: 'ความดันโลหิตสูง', hypertension: 'ความดันโลหิตสูง', dlp: 'ไขมันในเลือดสูง', ckd: 'โรคไตเรื้อรัง', ca: 'มะเร็ง', cancer: 'มะเร็ง' },
};

export const sansaQuestions = [
  ['q1_weight_change', 'น้ำหนักเปลี่ยนแปลง 3 เดือน'], ['q2_food_intake', 'การกินเปลี่ยนแปลง 3 เดือน'],
  ['q3_daily_activities', 'ทำกิจวัตรเกี่ยวกับอาหาร'], ['q4_chronic_disease', 'โรคประจำตัว'],
  ['q5_meals_per_day', 'จำนวนมื้ออาหาร'], ['q6_portion_size', 'ปริมาณอาหารต่อมื้อ'],
  ['q7_food_texture', 'ลักษณะอาหาร'], ['q8_rice_starch', 'ข้าวและแป้ง'],
  ['q9_protein', 'เนื้อสัตว์'], ['q10_milk', 'นม'], ['q11_fruits', 'ผลไม้'],
  ['q12_vegetables', 'ผัก'], ['q13_water', 'น้ำดื่ม'], ['q14_sweet_drinks', 'เครื่องดื่ม 3in1'],
  ['q15_cooking_method', 'วิธีปรุงอาหาร'], ['q16_oil_coconut', 'น้ำมันและกะทิ'],
] as const;

const answerLabels: Record<string, Record<string, string>> = {
  q1_weight_change: { decrease: 'ลดลง', stable: 'คงเดิม', increase: 'เพิ่มขึ้น' },
  q2_food_intake: { decrease: 'น้อยลง', normal: 'ปกติ', increase: 'มากขึ้น' },
  q3_daily_activities: { cannot: 'ไม่ได้', slower: 'ช้ากว่าปกติ', normal: 'ปกติ' },
  q4_chronic_disease: { no: 'ไม่มี', yes: 'มี' },
  q7_food_texture: { liquid: 'เหลว (น้ำ นม)', soft: 'อ่อน (โจ๊ก)', normal: 'ปกติ (ข้าวสวย)' },
  q15_cooking_method: { steam_boil: 'ข้อมูลเดิม: ต้ม/นึ่ง', stir_fry: 'ผัด', coconut_curry: 'แกงกะทิ', fried: 'ทอด', no_coconut: 'แกงไม่มีกะทิ' },
};

const units: Record<string, string> = {
  q5_meals_per_day: 'มื้อ', q8_rice_starch: 'กำปั้น/วัน', q9_protein: 'ฝ่ามือ/วัน',
  q10_milk: 'แก้ว/วัน', q11_fruits: 'กำปั้น/วัน', q12_vegetables: 'อุ้งมือ/วัน',
  q13_water: 'แก้ว/วัน', q14_sweet_drinks: 'แก้ว/วัน', q16_oil_coconut: 'นิ้วหัวแม่มือ/วัน',
};

export function displayResearchValue(field: string, value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (Array.isArray(value)) return value.map(item => displayResearchValue(field, item)).join(', ') || '—';
  if (field === 'chronic_diseases') {
    if (typeof value === 'string' && value.trim().startsWith('{')) {
      try { return displayResearchValue(field, JSON.parse(value)); } catch { return 'ข้อมูลเดิมต้องตรวจสอบ'; }
    }
    if (typeof value === 'object') {
      const data = value as Record<string, unknown>;
      const list = Array.isArray(data.diseases) ? data.diseases : Object.entries(data)
        .filter(([key, item]) => key in historicalLabels.chronic_diseases && (item === true || item === 1)).map(([key]) => key);
      const other = data.other || data.other_text;
      const otherText = typeof other === 'string' ? other.trim() : '';
      const meaningfulOther = /[A-Za-z0-9\u0E00-\u0E7F]/.test(otherText) ? [otherText] : [];
      return [...list.map(item => displayResearchValue(field, item)), ...meaningfulOther].join(', ') || '—';
    }
  }
  const text = String(value);
  const label = demographicOptions[field]?.[text] ?? historicalLabels[field]?.[text.toLowerCase()] ?? answerLabels[field]?.[text];
  if (label) return label;
  if (/[\u0E00-\u0E7F]/.test(text)) return text;
  if (field.startsWith('q')) {
    if (text === 'rarely') return 'แทบไม่ได้';
    const normalized = text.replace(/^more_than_/, '>').replace(/^less_than_/, '<').replace(/_to_/g, '–').replace(/_meals?$/, '');
    if (/^[<>]?\d+(?:[-–]\d+)?%?$/.test(normalized)) {
      const quantity = normalized.replace(/^>/, 'มากกว่า ').replace(/^</, 'น้อยกว่า ');
      if (field === 'q6_portion_size') return quantity.replace(/%$/, '') + '%';
      return units[field] ? `${quantity} ${units[field]}` : quantity;
    }
  }
  return 'ข้อมูลเดิมต้องตรวจสอบ';
}
