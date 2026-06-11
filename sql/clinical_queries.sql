/* ============================================================
   St. Martin's Hospital — Clinical & Financial SQL Analysis
   Dialect: T-SQL (Microsoft SQL Server)
   Author:  Jennifer Iwunze
   ------------------------------------------------------------
   Database: StMartinsHospital
   Table:    dbo.patients (10,000 cleaned patient records)
   ============================================================ */


/* ------------------------------------------------------------
   SUMMARY STATISTICS — headline numbers
   ------------------------------------------------------------ */
SELECT COUNT(*) AS total_patients FROM dbo.patients;

SELECT
    CAST(AVG(Treatment_Cost) AS DECIMAL(10,2))  AS overall_avg_cost,
    CAST(SUM(Treatment_Cost) AS DECIMAL(12,2))  AS total_hospital_spend
FROM dbo.patients
WHERE Treatment_Cost IS NOT NULL;


/* ------------------------------------------------------------
   QUERY 1 — Simple filter
   Clinical question: "Show me all high-risk patients over 60,
   sorted by treatment cost — our review priorities."
   ------------------------------------------------------------ */
SELECT
    Patient_ID,
    Age,
    Gender,
    Smoking_Status,
    Diabetes_Diagnosis,
    Treatment_Cost
FROM dbo.patients
WHERE Heart_Disease_Risk = 'High'
    AND Age > 60
    AND Treatment_Cost IS NOT NULL
ORDER BY Treatment_Cost DESC;


/* ------------------------------------------------------------
   QUERY 2 — Aggregation by risk tier
   Clinical question: "Break down our population and spend by
   risk level. Which tier drains the most money?"
   ------------------------------------------------------------ */
SELECT
    Heart_Disease_Risk,
    COUNT(*)                                    AS patient_count,
    CAST(AVG(Treatment_Cost) AS DECIMAL(10,2))  AS avg_cost,
    CAST(SUM(Treatment_Cost) AS DECIMAL(12,2))  AS total_cost,
    CAST(AVG(Hospital_Visits) AS DECIMAL(10,2)) AS avg_visits
FROM dbo.patients
WHERE Heart_Disease_Risk IS NOT NULL
GROUP BY Heart_Disease_Risk
ORDER BY total_cost DESC;


/* ------------------------------------------------------------
   QUERY 3 — Cohort segmentation with CASE
   Clinical question: "If we intervene on diabetic smokers over
   60, how large and expensive is that group vs everyone else?"
   ------------------------------------------------------------ */
SELECT
    CASE
        WHEN Diabetes_Diagnosis = 'Yes'
             AND Smoking_Status = 'Current'
             AND Age > 60
        THEN 'Target Cohort'
        ELSE 'Everyone Else'
    END                                         AS patient_segment,
    COUNT(*)                                    AS patient_count,
    CAST(AVG(Treatment_Cost) AS DECIMAL(10,2))  AS avg_cost,
    CAST(SUM(Treatment_Cost) AS DECIMAL(12,2))  AS total_cost
FROM dbo.patients
WHERE Treatment_Cost IS NOT NULL
GROUP BY
    CASE
        WHEN Diabetes_Diagnosis = 'Yes'
             AND Smoking_Status = 'Current'
             AND Age > 60
        THEN 'Target Cohort'
        ELSE 'Everyone Else'
    END;


/* ------------------------------------------------------------
   QUERY 4 — CTE + window function
   Clinical question: "Within each risk tier, who are the top 5
   most expensive patients? Our case-review shortlist."
   ------------------------------------------------------------ */
WITH RankedPatients AS (
    SELECT
        Patient_ID,
        Age,
        Gender,
        Heart_Disease_Risk,
        Treatment_Cost,
        ROW_NUMBER() OVER (
            PARTITION BY Heart_Disease_Risk
            ORDER BY Treatment_Cost DESC
        ) AS cost_rank
    FROM dbo.patients
    WHERE Treatment_Cost IS NOT NULL
        AND Heart_Disease_Risk IS NOT NULL
)
SELECT
    Heart_Disease_Risk,
    cost_rank,
    Patient_ID,
    Age,
    Gender,
    Treatment_Cost
FROM RankedPatients
WHERE cost_rank <= 5
ORDER BY Heart_Disease_Risk, cost_rank;

/* ============================================================
   Note: ROW_NUMBER / PARTITION BY syntax is identical in
   Google BigQuery, so these queries port directly to a
   cloud warehouse environment.
   ============================================================ */
