import sys

import sqlalchemy.orm
from datetime import date
from datetime import datetime
from IWMDatabaseService import IWMDatabaseService
from IWMErrorService import IWMErrorService
from sqlalchemy import create_engine, func, MetaData
from sqlalchemy import exc
from sqlalchemy.ext.automap import automap_base
from typing import Any


# Service to handle all interactions with the Weather Manager database
class WMDatabaseService(IWMDatabaseService):
    engine = None
    _error_service: IWMErrorService
    base = automap_base()
    observations: Any = None

    def __init__(self, url, port, username, password, dbname, error_service: IWMErrorService):

        self._error_service = error_service

        try:

            self.engine = create_engine(f"mariadb+mariadbconnector://{username}:{password}@{url}:{port}/{dbname}")

            # First, check what tables exist using raw metadata
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            raw_table_names = list(metadata.tables.keys())

            self.base.prepare(self.engine, reflect=True)

            # Check if an "observations" table exists in reflected tables
            available_tables = list(self.base.classes.keys())

            if not available_tables:
                # Tables exist, but automap couldn't map them
                if raw_table_names:
                    raw_tables_str = ", ".join(raw_table_names)
                    self._error_service.handle_error(
                        f"Database {dbname} contains tables ({raw_tables_str}) but SQLAlchemy automap could not reflect them. "
                        f"This typically means the 'Observations' table is missing a PRIMARY KEY constraint. "
                        f"Please add a PRIMARY KEY to the Observations table (e.g., ALTER TABLE Observations ADD PRIMARY KEY (ObservationTime);)",
                        "Error", send_email=True, terminate=True)
                else:
                    self._error_service.handle_error(
                        f"No tables found in database {dbname}. Please ensure the database is initialized with the required schema.",
                        "Error", send_email=True, terminate=True)

            # Try to find the "observations" table (case-insensitive)
            observations_table = None
            for table_name in available_tables:
                if table_name.lower() == 'observations':
                    observations_table = table_name
                    break

            if observations_table is None:
                available_tables_str = ", ".join(available_tables)
                self._error_service.handle_error(
                    f"Table 'observations' not found in database {dbname}. "
                    f"Available tables: {available_tables_str}. "
                    f"Please run DatabaseInitialBuild.sql to create the required schema.",
                    "Error", send_email=True, terminate=True)

            # At this point, observations_table is guaranteed to be a string (not None)
            assert observations_table is not None, "observations_table should not be None at this point"

            # Use the actual table name from the database
            self.observations = getattr(self.base.classes, observations_table)

        except sqlalchemy.exc.TimeoutError:

            self._error_service.handle_error(f"Timeout connecting to database {url}:{port}/{dbname}",
                                             "Error", send_email=True, terminate=True)

        except sqlalchemy.exc.DBAPIError as ex:

            self._error_service.handle_error(f"Database access error: {ex}",
                                             "Error", send_email=True, terminate=True)

        except AttributeError as ex:

            self._error_service.handle_error(
                f"Failed to map database table: {ex}. "
                f"Please verify the database schema is correctly initialized.",
                "Error", send_email=True, terminate=True)

    def dispose(self):
        self.engine.dispose()

    # Gets the date of the most recent observation from the "observations" table.
    # If there are no observations, then the default observation date is returned.
    def get_most_recent_observation_date(self, default_observation_date: date) -> date:

        try:

            session_factory = sqlalchemy.orm.sessionmaker()
            session_factory.configure(bind=self.engine)
            session = session_factory()
            result: datetime = session.query(func.max(self.observations.ObservationTime)).scalar()
            session.close()

            if result is None:
                return default_observation_date
            else:
                return result.date()

        except sqlalchemy.exc.DBAPIError as ex:

            self._error_service.handle_error(f"Database access error while getting most recent observation date: {ex}",
                                             "Error", send_email=True, terminate=True)
            sys.exit(1)

    # Saves observations to the database. Observations are provided as a list of hourly
    # observations for a multiple of days. These need to be reformatted before writing.
    def save_list_of_observations(self, observations):

        try:

            session = sqlalchemy.orm.sessionmaker()
            session.configure(bind=self.engine)
            session = session()

            for daily_observation in observations:

                _hourly_observation_counter = 0

                if daily_observation["observations"]:

                    _date_of_observations = daily_observation["observations"][0]["obsTimeLocal"][0:10]

                    for hourly_observation in daily_observation["observations"]:
                        session.add(self._create_formatted_observation(hourly_observation))
                        _hourly_observation_counter += 1

                    if _hourly_observation_counter == 24:
                        self._error_service.handle_error(f"Observations recorded for {_date_of_observations}",
                                                         "Info")
                    else:
                        self._error_service.handle_error(f"Only {_hourly_observation_counter} "
                                                         f"observations were recorded for {_date_of_observations}",
                                                         "Warning", send_email=True, batch_message=True)

            session.commit()
            session.close()

        except sqlalchemy.exc.DBAPIError as ex:

            self._error_service.handle_error(f"Database access error while saving list of observations: {ex}",
                                             "Error", send_email=True, terminate=True, exc_info=ex)

    # Creates and returns a single SQLAlchemy observation object from an hourly observation
    # that was returned from Weather Underground.
    def _create_formatted_observation(self, hourly_observation):

        return self.observations(ObservationTime=hourly_observation["obsTimeLocal"],
                                 SolarRadiationHigh=hourly_observation["solarRadiationHigh"],
                                 UvHigh=hourly_observation["uvHigh"],
                                 WindDirectionMean=hourly_observation["winddirAvg"],
                                 HumidityHigh=hourly_observation["humidityHigh"],
                                 HumidityLow=hourly_observation["humidityLow"],
                                 HumidityMean=hourly_observation["humidityAvg"],
                                 TemperatureHigh=hourly_observation["metric"]["tempHigh"],
                                 TemperatureLow=hourly_observation["metric"]["tempLow"],
                                 TemperatureMean=hourly_observation["metric"]["tempAvg"],
                                 WindSpeedHigh=hourly_observation["metric"]["windspeedHigh"],
                                 WindSpeedLow=hourly_observation["metric"]["windspeedLow"],
                                 WindSpeedMean=hourly_observation["metric"]["windspeedAvg"],
                                 WindGustHigh=hourly_observation["metric"]["windgustHigh"],
                                 WindGustLow=hourly_observation["metric"]["windgustLow"],
                                 WindGustMean=hourly_observation["metric"]["windgustAvg"],
                                 DewPointHigh=hourly_observation["metric"]["dewptHigh"],
                                 DewPointLow=hourly_observation["metric"]["dewptLow"],
                                 DewPointMean=hourly_observation["metric"]["dewptAvg"],
                                 WindChillHigh=hourly_observation["metric"]["windchillHigh"],
                                 WindChillLow=hourly_observation["metric"]["windchillLow"],
                                 WindChillMean=hourly_observation["metric"]["windchillAvg"],
                                 HeatIndexHigh=hourly_observation["metric"]["heatindexHigh"],
                                 HeatIndexLow=hourly_observation["metric"]["heatindexLow"],
                                 HeatIndexMean=hourly_observation["metric"]["heatindexAvg"],
                                 PressureHigh=hourly_observation["metric"]["pressureMax"],
                                 PressureLow=hourly_observation["metric"]["pressureMin"],
                                 PressureTrend=hourly_observation["metric"]["pressureTrend"],
                                 PrecipitationRate=hourly_observation["metric"]["precipRate"],
                                 PrecipitationTotal=hourly_observation["metric"]["precipTotal"]
                                 )
