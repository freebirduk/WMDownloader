import sqlalchemy

Base = declarative_base()


class Observation(Base):
    __tablename__ = "observations"
    ObservationId = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    ObservationTime = sqlalchemy.Column(sqlalchemy.DATETIME)
    SolarRadiationHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(5, 1))
    UvHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    WindDirectionMean = sqlalchemy.Column(sqlalchemy.DECIMAL(3))
    HumidityHigh = sqlalchemy.Column(sqlalchemy.SmallInteger)
    HumidityLow = sqlalchemy.Column(sqlalchemy.SmallInteger)
    HumidityMean = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    TemperatureHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    TemperatureLow = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    TemperatureMean = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    WindSpeedHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    WindSpeedLow = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    WindSpeedMean = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    WindGustHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    WindGustLow = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    WindGustMean = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 1))
    DewPointHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    DewPointLow = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    DewPointMean = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    WindChillHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    WindChillLow = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    WindChillMean = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    HeatIndexHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    HeatIndexLow = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    HeatIndexMean = sqlalchemy.Column(sqlalchemy.DECIMAL(3, 1))
    PressureHigh = sqlalchemy.Column(sqlalchemy.DECIMAL(6, 2))
    PressureLow = sqlalchemy.Column(sqlalchemy.DECIMAL(6, 2))
    PressureTrend = sqlalchemy.Column(sqlalchemy.DECIMAL(4, 2))
    PrecipitationRate = sqlalchemy.Column(sqlalchemy.DECIMAL(5, 2))
    PrecipitationTotal = sqlalchemy.Column(sqlalchemy.DECIMAL(5, 2))
