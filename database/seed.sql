-- Baseline Seed Data for Smart Crop Advisory

-- 1. Crops Catalog
INSERT OR IGNORE INTO crops (id, crop_name, hindi_name, scientific_name, season, base_temp_c, msp_inr_quintal, avg_yield_q_ha) VALUES
(1, 'Wheat', 'गेहूं', 'Triticum aestivum', 'Rabi', 5.0, 2275.0, 48.5),
(2, 'Paddy (Rice)', 'धान', 'Oryza sativa', 'Kharif', 10.0, 2300.0, 55.0),
(3, 'Mustard', 'सरसों', 'Brassica juncea', 'Rabi', 5.0, 5650.0, 21.0),
(4, 'Cotton', 'कपास', 'Gossypium hirsutum', 'Kharif', 12.0, 7121.0, 22.5),
(5, 'Sugarcane', 'गन्ना', 'Saccharum officinarum', 'Annual', 12.0, 340.0, 780.0);

-- 2. Government Schemes (PM-KISAN, PMFBY, Soil Health Card, Kisan Credit Card)
INSERT OR IGNORE INTO government_schemes (id, code, scheme_name, hindi_name, ministry, purpose, eligibility_info, benefits_summary, official_portal_url, helpline_number) VALUES
(1, 'PMFBY', 'Pradhan Mantri Fasal Bima Yojana (PMFBY)', 'प्रधानमंत्री फसल बीमा योजना', 'Ministry of Agriculture & Farmers Welfare',
 'Financial support and risk mitigation to farmers suffering crop loss or damage arising out of natural calamities, pests and diseases.',
 'All farmers growing notified crops in notified areas including sharecroppers and tenant farmers.',
 'Comprehensive risk insurance from pre-sowing to post-harvest. Farmer premium capped at 1.5% for Rabi, 2% for Kharif, 5% for commercial/horticultural crops.',
 'https://pmfby.gov.in', '1800-180-1551'),

(2, 'PMKISAN', 'PM-KISAN Samman Nidhi', 'प्रधानमंत्री किसान सम्मान निधि', 'Ministry of Agriculture & Farmers Welfare',
 'Direct income support of Rs 6,000 per year to small and marginal farmer families to augment agricultural and domestic needs.',
 'All landholder farmer families having cultivable landholding in their names across India.',
 'Direct benefit transfer of Rs 6,000 annually in three equal 4-monthly installments of Rs 2,000 directly into Aadhaar-seeded bank accounts.',
 'https://pmkisan.gov.in', '155261'),

(3, 'SHC', 'Soil Health Card Scheme', 'मृदा स्वास्थ्य कार्ड योजना', 'Department of Agriculture & Cooperation',
 'Promoting soil test-based balanced nutrient management and improving soil organic carbon.',
 'Available to all registered farmers across every rural gram panchayat in India.',
 'Free diagnostic assessment of 12 soil parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) with tailored crop-wise fertilizer dosage recommendations.',
 'https://soilhealth.dac.gov.in', '011-23382012'),

(4, 'KCC', 'Kisan Credit Card (KCC) Scheme', 'किसान क्रेडिट कार्ड योजना', 'Ministry of Finance & NABARD',
 'Adequate and timely credit support from the banking system under single window for agricultural cultivation and allied activities.',
 'Individual/joint farmers, owner cultivators, tenant farmers, oral lessees, self-help groups (SHGs).',
 'Revolving cash credit limit up to Rs 3 Lakh at an effective interest rate of 4% per annum (after 3% prompt repayment incentive). Simple documentation.',
 'https://www.myscheme.gov.in/schemes/kcc', '1800-115-565');

-- 3. Baseline Machinery at Karnal Custom Hiring Center
INSERT OR IGNORE INTO machinery (id, equipment_name, equipment_type, ownership, registration_number, operating_cost_per_hour, status, last_service_date, next_service_due, contact_phone) VALUES
(1, 'Mahindra 575 DI 45HP Tractor', 'Tractor', 'Owned', 'HR-05-AB-4120', 450.0, 'Available', '2026-08-15', '2026-11-15', '+91 98120 44551'),
(2, 'Happy Seeder / Zero-Till Seed Drill', 'Seed Drill', 'Custom Hiring Center (CHC)', 'HR-05-CH-1092', 350.0, 'Available', '2026-09-01', '2026-12-01', '+91 94160 88210'),
(3, 'Agri-Flyer Pro 16L Drone Sprayer', 'Drone Sprayer', 'Custom Hiring Center (CHC)', 'DRONE-HR-204', 600.0, 'Available', '2026-09-20', '2026-10-20', '+91 98960 77332'),
(4, 'Laser Land Leveler with Transmitter', 'Laser Land Leveler', 'Rented', 'HR-05-LL-3011', 500.0, 'Available', '2026-07-10', '2026-10-10', '+91 94162 11994');
