/* Initial creation of Weather Manager database */
/* Creates the database and table structure */
/* Requires root access to the database */

USE weathermanagertest;

/* Add tables */
CREATE TABLE Observations(
	ObservationId INT PRIMARY KEY IDENTITY(1,1),
	ObservationTime DATETIME NOT NULL,
	SolarRadiationHigh DECIMAL(5,1) NOT NULL CHECK(SolarRadiationHigh >= 0),
	UvHigh DECIMAL(4,1) NOT NULL CHECK(UvHigh >= 0),
	WindDirectionMean DECIMAL(3) NOT NULL CHECK(WindDirectionMean >= 0),
	HumidityHigh TINYINT NOT NULL CHECK(HumidityHigh >= 0),
	HumidityLow TINYINT NOT NULL CHECK(HumidityLow>=0),
	HumidityMean DECIMAL(4,1) NOT NULL CHECK(HumidityMean>= 0),
	TemperatureHigh DECIMAL(3,1) NOT NULL,
	TemperatureLow DECIMAL(3,1) NOT NULL,
	TemperatureMean DECIMAL(3,1) NOT NULL,
	WindSpeedHigh DECIMAL(4,1) NOT NULL,
	WindSpeedLow DECIMAL(4,1) NOT NULL,
	WindSpeedMean DECIMAL(4,1) NOT NULL,
	WindGustHigh DECIMAL(4,1) NOT NULL,
	WindGustLow DECIMAL(4,1) NOT NULL,
	WindGustMean DECIMAL(4,1) NOT NULL,
	DewPointHigh DECIMAL(3,1) NOT NULL,
	DewPointLow DECIMAL(3,1) NOT NULL,
	DewPointMean DECIMAL(3,1) NOT NULL,
	WindChillHigh DECIMAL(3,1) NOT NULL,
	WindChillLow DECIMAL(3,1) NOT NULL,
	WindChillMean DECIMAL(3,1) NOT NULL,
	HeatIndexHigh DECIMAL(3,1) NOT NULL,
	HeatIndexLow DECIMAL(3,1) NOT NULL,
	HeatIndexMean DECIMAL(3,1) NOT NULL,
	PressureHigh DECIMAL(6,2) NOT NULL CHECK(PressureHigh >= 0),
	PressureLow DECIMAL(6,2) NOT NULL CHECK(PressureLow >= 0),
	PressureTrend DECIMAL(4,2),
	PrecipitationRate DECIMAL(5,2) NOT NULL CHECK(PrecipitationRate >= 0),
	PrecipitationTotal DECIMAL(5,2) NOT NULL CHECK(PrecipitationTotal >= 0)
)

CREATE TABLE Extremes (
	extremeId INT PRIMARY KEY IDENTITY(1,1),
	Name VARCHAR(50) NOT NULL, -- Description of extreme
	Date DATETIME NOT NULL, -- Date on which the extreme occurred
	Rank TINYINT NOT NULL DEFAULT 0 CHECK(Rank >= 0), -- 1 = 1st etc
	HighInt INT NOT NULL DEFAULT 0 CHECK(HighInt >= 0), -- Highest integer of the extreme
	LowInt INT NOT NULL DEFAULT 0 CHECK(LowInt >= 0), -- Lowest integer of the extreme
	HighFloat FLOAT NOT NULL DEFAULT 0 CHECK(HighFloat >= 0), -- Highest float of the extreme
	LowFloat FLOAT NOT NULL DEFAULT 0 CHECK(LowFloat >= 0) -- Lowest float of the extreme
)