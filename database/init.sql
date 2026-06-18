-- DDL Relational Schema Initialization
DROP TABLE IF EXISTS golden_corridors CASCADE;
DROP TABLE IF EXISTS batch_telemetry CASCADE;
DROP TABLE IF EXISTS batch_metadata CASCADE;

CREATE TABLE batch_metadata (
    batch_id VARCHAR(50) PRIMARY KEY,
    product_code VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    execution_type VARCHAR(20) DEFAULT 'Production',
    reagent_purity NUMERIC(5,2),
    moisture_content NUMERIC(5,2),
    particle_size_d50 NUMERIC(5,2),
    final_impurity NUMERIC(5,3),
    final_yield NUMERIC(5,2),
    final_cycle_time NUMERIC(5,2)
);

CREATE TABLE batch_telemetry (
    batch_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    phase VARCHAR(20) NOT NULL,
    internal_temp NUMERIC(5,2),
    pressure NUMERIC(5,2),
    dosing_rate NUMERIC(5,2),
    cooling_rate NUMERIC(5,2),
    seed_temp NUMERIC(5,2),
    cake_pressure NUMERIC(5,2),
    wash_volume NUMERIC(5,2),
    vacuum_level NUMERIC(5,2),
    agitation_rpm NUMERIC(5,2),
    PRIMARY KEY (batch_id, timestamp)
) PARTITION BY HASH (batch_id);

CREATE TABLE batch_telemetry_p1 PARTITION OF batch_telemetry FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE batch_telemetry_p2 PARTITION OF batch_telemetry FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE batch_telemetry_p3 PARTITION OF batch_telemetry FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE batch_telemetry_p4 PARTITION OF batch_telemetry FOR VALUES WITH (MODULUS 4, REMAINDER 3);

CREATE TABLE golden_corridors (
    parameter_name VARCHAR(50) PRIMARY KEY,
    ai_min NUMERIC(5,2) NOT NULL,
    ai_max NUMERIC(5,2) NOT NULL,
    sme_manual_min NUMERIC(5,2) NOT NULL,
    sme_manual_max NUMERIC(5,2) NOT NULL
);

INSERT INTO golden_corridors VALUES ('internal_temp', 180.00, 185.00, 170.00, 195.00);
INSERT INTO golden_corridors VALUES ('cooling_rate', 15.00, 18.00, 10.00, 25.00);
INSERT INTO golden_corridors VALUES ('wash_volume', 850.00, 900.00, 500.00, 1000.00);
INSERT INTO golden_corridors VALUES ('vacuum_level', 15.00, 20.00, 10.00, 50.00);
