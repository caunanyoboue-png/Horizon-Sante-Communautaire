/**
 * API Types for ONG ADJAHI Platform
 */

export interface User {
  id: number
  email: string
  phone: string
  first_name: string
  last_name: string
  full_name: string
  role: 'ADMIN' | 'DOCTOR' | 'MIDWIFE' | 'COMMUNITY_AGENT' | 'PSYCHOLOGIST' | 'NURSE' | 'PATIENT'
  location: 'GRAND_BASSAM' | 'BONOUA' | 'BOTH'
  specialization?: string
  license_number?: string
  is_2fa_enabled: boolean
  is_active: boolean
  avatar?: string
  bio?: string
  last_login?: string
  created_at: string
}

export interface Patient {
  id: number
  patient_id: string
  first_name: string
  last_name: string
  full_name: string
  date_of_birth: string
  age: number
  gender: 'M' | 'F'
  phone: string
  email?: string
  address: string
  city: string
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relation: string
  blood_group: string
  height?: number
  weight?: number
  bmi?: number
  marital_status: string
  occupation?: string
  registration_location: string
  is_active: boolean
  notes?: string
  created_at: string
  updated_at: string
}

export interface Pregnancy {
  id: number
  patient: number
  patient_name: string
  pregnancy_number: number
  parity: number
  last_menstrual_period: string
  expected_delivery_date: string
  actual_delivery_date?: string
  status: 'ONGOING' | 'COMPLETED' | 'MISCARRIAGE' | 'ABORTION'
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  blood_group_verified: boolean
  rh_factor?: string
  has_diabetes: boolean
  has_hypertension: boolean
  has_anemia: boolean
  other_risks?: string
  assigned_midwife?: number
  assigned_midwife_name?: string
  notes?: string
  gestational_age_weeks?: number
  gestational_age_display?: string
  trimester?: number
  created_at: string
  updated_at: string
}

export interface CPNConsultation {
  id: number
  pregnancy: number
  patient_name: string
  cpn_type: 'CPN1' | 'CPN2' | 'CPN3' | 'CPN4' | 'CPN_EXTRA'
  consultation_date: string
  gestational_age_weeks: number
  weight: number
  blood_pressure_systolic: number
  blood_pressure_diastolic: number
  temperature?: number
  fundal_height?: number
  fetal_heart_rate?: number
  hemoglobin?: number
  glucose?: number
  protein_in_urine: boolean
  hiv_test_done: boolean
  hiv_test_result?: string
  syphilis_test_done: boolean
  syphilis_test_result?: string
  iron_supplement_given: boolean
  folic_acid_given: boolean
  antimalarial_given: boolean
  tetanus_vaccine_given: boolean
  next_appointment_date?: string
  next_cpn_type?: string
  conducted_by?: number
  conducted_by_name?: string
  complaints?: string
  examination_findings?: string
  diagnosis?: string
  treatment_plan?: string
  referral_needed: boolean
  referral_reason?: string
  notes?: string
  is_high_blood_pressure: boolean
  is_anemic: boolean
  bmi?: number
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface ApiError {
  success: false
  error: {
    message: string
    code: number
    details?: any
  }
}
