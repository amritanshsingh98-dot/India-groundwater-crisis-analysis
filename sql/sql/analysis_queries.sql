-- India Groundwater Crisis — Analysis Queries
-- Run these in DBeaver after importing cleaned CSVs
-- All queries use real column names from cleaned data

-- ================================================
-- QUERY 1: Depletion trend using window functions
-- Shows year-over-year change per state and rank
-- ================================================

SELECT
    state,
    year,
    stage_extraction,
    LAG(stage_extraction)
        OVER (PARTITION BY state ORDER BY year)
        AS prev_stage_extraction,
    ROUND(
        stage_extraction -
        LAG(stage_extraction)
            OVER (PARTITION BY state ORDER BY year)
    , 2) AS yoy_change,
    RANK()
        OVER (PARTITION BY year ORDER BY stage_extraction DESC)
        AS stress_rank
FROM groundwater
ORDER BY state, year;

-- ================================================
-- QUERY 2: Current status vs historical average
-- Shows where each state stands today vs its own past
-- ================================================

SELECT
    state,
    MAX(CASE
        WHEN year = (SELECT MAX(year) FROM groundwater)
        THEN stage_extraction
    END) AS current_status,
    ROUND(AVG(stage_extraction), 2) AS historical_avg,
    ROUND(
        MAX(CASE
            WHEN year = (SELECT MAX(year) FROM groundwater)
            THEN stage_extraction
        END) - AVG(stage_extraction)
    , 2) AS how_far_above_own_average
FROM groundwater
GROUP BY state
ORDER BY current_status DESC;

-- ================================================
-- QUERY 3: CGWB classification categories
-- Mirrors the official Safe/Semi-Critical/Critical/
-- Over-Exploited classification system
-- ================================================

SELECT
    state,
    year,
    stage_extraction,
    CASE
        WHEN stage_extraction > 100 THEN 'Over-Exploited'
        WHEN stage_extraction BETWEEN 90 AND 100 THEN 'Critical'
        WHEN stage_extraction BETWEEN 70 AND 90  THEN 'Semi-Critical'
        ELSE 'Safe'
    END AS cgwb_category,
    ROUND(PERCENT_RANK()
        OVER (PARTITION BY year ORDER BY stage_extraction)
        * 100, 1) AS national_percentile
FROM groundwater
WHERE year = (SELECT MAX(year) FROM groundwater)
ORDER BY stage_extraction DESC;

-- ================================================
-- QUERY 4: Sector driver analysis
-- Shows what % of each state's extraction
-- comes from irrigation vs industrial vs domestic
-- ================================================

SELECT
    state,
    year,
    irrigation,
    industrial,
    domestic,
    total_extraction,
    ROUND(irrigation  / NULLIF(total_extraction,0) * 100, 1)
        AS pct_irrigation,
    ROUND(industrial  / NULLIF(total_extraction,0) * 100, 1)
        AS pct_industrial,
    ROUND(domestic    / NULLIF(total_extraction,0) * 100, 1)
        AS pct_domestic,
    -- share of national irrigation extraction
    ROUND(
        irrigation /
        SUM(irrigation) OVER (PARTITION BY year)
        * 100, 2) AS pct_of_national_irrigation
FROM groundwater
WHERE year = (SELECT MAX(year) FROM groundwater)
ORDER BY pct_irrigation DESC;

-- ================================================
-- QUERY 5: Rainfall vs stress causation check
-- Key query: high stress + normal rainfall = extraction-driven
-- Low dryness_rank + high stress_rank = the smoking gun
-- ================================================

SELECT
    g.state,
    g.year,
    g.stage_extraction,
    r.rainfall_mm,
    r.rainfall_mapping_note,
    RANK()
        OVER (PARTITION BY g.year ORDER BY g.stage_extraction DESC)
        AS stress_rank,
    RANK()
        OVER (PARTITION BY g.year ORDER BY r.rainfall_mm ASC)
        AS dryness_rank
FROM groundwater g
JOIN rainfall r
    ON g.state = r.state
    AND g.year  = r.year
WHERE r.rainfall_mm IS NOT NULL
  AND g.year = (SELECT MAX(year) FROM groundwater)
ORDER BY stress_rank;

-- A state with high stress_rank but LOW dryness_rank
-- (normal or above-average rainfall) is extracting
-- unsustainably regardless of weather — this is the
-- central finding of the project.
-- Punjab stress_rank = 1, dryness_rank = mid-table.
