// Enums
export enum Sex {
  MALE = 'male',
  FEMALE = 'female',
  OTHER = 'other',
  PREFER_NOT_TO_SAY = 'prefer_not_to_say',
}

export enum UserRole {
  ADMIN = 'admin',
  STAFF = 'staff',
}

export enum MealType {
  BREAKFAST = 'breakfast',
  MORNING_SNACK = 'morning_snack',
  LUNCH = 'lunch',
  AFTERNOON_SNACK = 'afternoon_snack',
  DINNER = 'dinner',
  BEFORE_BED = 'before_bed',
  OTHER = 'other',
}

// Auth Types
export interface LoginRequest {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: UserRole
  is_active: boolean
  created_at: string
}

// Respondent Types
export interface RespondentCreate {
  respondent_code?: string
  age?: number
  sex?: Sex
  education_level?: string
  income_range?: string
  occupation?: string
  marital_status?: string
  living_arrangement?: string
  phone?: string
  email?: string
}

export interface Respondent extends RespondentCreate {
  id: number
  respondent_code: string
  created_at: string
  updated_at: string
}

// Visit Types
export interface VisitCreate {
  respondent_id: number
  visit_number?: number
  visit_date: string
  visit_time?: string
  facility_id?: number
  visit_type?: 'baseline' | 'follow_up' | 'final'
  notes?: string
}

export interface Visit extends VisitCreate {
  id: number
  created_at: string
}

// SANSA Types
export interface SANSAItemInput {
  item_type: 'screening' | 'dietary'
  item_number: number
  item_code: string
  answer_value: string
  item_score: number
}

export interface SANSAResponseCreate {
  visit_id: number
  items: SANSAItemInput[]
}

export interface SANSAItem {
  item_type: string
  item_number: number
  item_code: string
  answer_value: string
  item_score: number
}

export interface SANSAResponse {
  id: number
  visit_id: number
  scoring_version_id: number
  screening_total?: number
  diet_total?: number
  total_score?: number
  result_level?: string
  completed_at?: string
  items: SANSAItem[]
}

export interface SANSAAdviceResponse {
  result_level: string
  total_score?: number
  advice_text?: string
}

// Satisfaction Types
export interface SatisfactionItemInput {
  item_number: number
  item_code: string
  question_text?: string
  answer_value: number
}

export interface SatisfactionResponseCreate {
  visit_id: number
  overall_satisfaction?: number
  comments?: string
  items: SatisfactionItemInput[]
}

export interface SatisfactionResponse {
  id: number
  visit_id: number
  overall_satisfaction?: number
  comments?: string
  completed_at?: string
  items: SatisfactionItemInput[]
}

// Food Diary Types
export interface FoodDiaryEntryCreate {
  visit_id: number
  entry_date: string
  entry_time?: string
  meal_type: MealType
  menu_name: string
  description?: string
  portion_description?: string
}

export interface FoodDiaryPhoto {
  id: number
  original_filename?: string
  stored_filename: string
  file_path: string
  file_size_bytes?: number
  mime_type?: string
  uploaded_at: string
}

export interface FoodDiaryEntry extends FoodDiaryEntryCreate {
  id: number
  photos: FoodDiaryPhoto[]
  created_at: string
}

// Knowledge Types
export interface KnowledgePost {
  id: number
  title: string
  slug: string
  content?: string
  summary?: string
  featured_image_path?: string
  category?: string
  tags?: string
  is_published: boolean
  published_at?: string
  display_order: number
  created_at: string
}

// Facility Types
export interface Facility {
  id: number
  name: string
  code?: string
  type?: string
  description?: string
  address?: string
  phone?: string
  email?: string
  website?: string
  latitude?: number
  longitude?: number
  map_link?: string
  is_active: boolean
  display_order: number
  created_at: string
}

// API Response Types
export interface ApiError {
  detail: string
}

export interface MessageResponse {
  message: string
  detail?: string
}
