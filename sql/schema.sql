-- India Groundwater Crisis Analysis
-- Schema: 3 source tables + composite key for joining
-- All BCM (Billion Cubic Metres) unless noted

CREATE TABLE groundwater (
    state                        VARCHAR(100),
    year                         INTEGER,
    recharge_rainfall_monsoon    NUMERIC(8,2),
    recharge_other_monsoon       NUMERIC(8,2),
    recharge_rainfall_nonmonsoon NUMERIC(8,2),
    recharge_other_nonmonsoon    NUMERIC(8,2),
    total_recharge               NUMERIC(8,2),
    natural_discharges           NUMERIC(8,2),
    extractable_resource         NUMERIC(8,2),
    irrigation                   NUMERIC(8,2),
    industrial                   NUMERIC(8,2),
    domestic                     NUMERIC(8,2),
    total_extraction             NUMERIC(8,2),
    domestic_allocation          NUMERIC(8,2),
    net_availability             NUMERIC(8,2),
    stage_extraction             NUMERIC(8,2),
    industrial_was_missing       BOOLEAN,
    stateyearkey                 VARCHAR(120)
);

-- stage_extraction > 100 means the state extracts more
-- than it naturally recharges (Over-Exploited classification)

CREATE TABLE population (
    state                 VARCHAR(100),
    year                  INTEGER,
    population            BIGINT,
    cagr_2011_2021_pct    NUMERIC(6,4),
    source_note           TEXT,
    stateyearkey          VARCHAR(120)
);

-- Note: population values are ORGI projections based on
-- 2011 Census CAGR, not actual measured counts.
-- India has not conducted a census since 2011.

CREATE TABLE rainfall (
    state                  VARCHAR(100),
    year                   INTEGER,
    rainfall_mm            NUMERIC(6,1),
    rainfall_mapping_note  TEXT,
    stateyearkey           VARCHAR(120)
);

-- rainfall_mapping_note values:
--   direct                          = subdivision name matched state directly
--   averaged_from_2_subdivisions    = two IMD subdivisions averaged into one state
--   shared_combined_subdivision_value_not_state_specific = J&K + Ladakh share one figure
--   UNAVAILABLE_*                   = no subdivision exists for this small UT
