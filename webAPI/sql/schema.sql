PRAGMA foreign_keys = ON;

-- null or not null
CREATE TABLE data(
    totalCarbonEmission VARCHAR(256) NOT NULL, 
    solarCarbonEmission VARCHAR(256) NOT NULL,
    evCarbonEmission VARCHAR(256) NOT NULL,
    emsCarbonEmission VARCHAR(256) NOT NULL,
    netInvertertoGrid VARCHAR(256) NOT NULL,
    netSolartoInverter VARCHAR(256) NOT NULL,
    netInvertertoComps VARCHAR(256) NOT NULL,
    -- totalPowerConsumed VARCHAR(256) NOT NULL,
    -- totalCleanConsumed VARCHAR(256) NOT NULL,
    -- totalGridConsumed VARCHAR(256) NOT NULL,
    -- totalSolarConsumed VARCHAR(256) NOT NULL,
    postid INTEGER PRIMARY KEY AUTOINCREMENT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chart(
    baselineEmission VARCHAR(256) NOT NULL,
    noEMSEmission VARCHAR(256) NOT NULL,
    withEMSEmission VARCHAR(256) NOT NULL,
    postid INTEGER PRIMARY KEY AUTOINCREMENT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);