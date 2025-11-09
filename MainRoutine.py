# Main logic for importing Weather Underground PWS data and adding it to the Weather Manager database.
# Will import all observations not yet downloaded up until yesterday's date.

from IDateTimeProvider import IDateTimeProvider
from IWMDatabaseService import IWMDatabaseService
from IWMErrorService import IWMErrorService
from IWeatherUndergroundApiService import IWeatherUndergroundApiService
import logging
from WuApiException import WuApiException
from datetime import date
from datetime import datetime
from datetime import timedelta
from os.path import exists


def _configure_logging(log_file_full_name: str):
    _log_format = "%(asctime)s - %(levelname)s - %(message)s"

    if exists(log_file_full_name):
        logging.basicConfig(filename=log_file_full_name, format=_log_format, level=logging.INFO)
    else:
        logging.basicConfig(filename="WMDownloader.log", format=_log_format)
        logging.warning(f"Couldn't find the supplied log file {log_file_full_name}")


class MainRoutine:
    _api_throttling_limit: str
    _database_service: IWMDatabaseService
    _date_time_provider: IDateTimeProvider
    _initial_observation_date = None
    _wm_error_service: IWMErrorService
    _wu_api_service: IWeatherUndergroundApiService

    def __init__(self,
                 wm_database_service: IWMDatabaseService,
                 date_time_provider: IDateTimeProvider,
                 wu_api_service: IWeatherUndergroundApiService,
                 wm_error_service: IWMErrorService,
                 api_throttling_limit: str,
                 initial_observation_date: str,
                 log_file_full_name: str):

        # Setup logging
        _configure_logging(log_file_full_name)

        # Store the injected services and parameters
        self._database_service = wm_database_service
        self._date_time_provider = date_time_provider
        self._wu_service = wu_api_service
        self._wm_error_service = wm_error_service
        self._api_throttling_limit = api_throttling_limit
        self._initial_observation_date = initial_observation_date

    # The controlling method that is called to drive the download of recent observations
    def download_recent_observations(self) -> None:

        self._not_currently_gathering_data_warner()

        if self._initial_observation_date is None:
            raise ValueError("Initial observation date is not configured")

        _initial_observation_date = datetime.strptime(self._initial_observation_date, '%Y-%m-%d').date()
        _most_recent_observation_date: date = \
            self._database_service.get_most_recent_observation_date(_initial_observation_date)

        # We only get observations from up to TWO days ago, not up to yesterday. This is because the Weather
        # Underground API is sometimes slow in providing the full set of observations for yesterday.
        _fetch_up_to_date = self._apply_api_throttling_limit(self._date_time_provider.now() -
                                                             timedelta(days=2),
                                                             _most_recent_observation_date)

        _retrieved_observations = self._retrieve_recent_observations(_most_recent_observation_date,
                                                                     _fetch_up_to_date)

        self._database_service.save_list_of_observations(_retrieved_observations)

        self._wm_error_service.finalise_error_handling()

    # To avoid tripping the Weather Underground API throttling limit, this will restrict the number of
    # recent observations downloaded to the value set in the config file. Outstanding observations will
    # get downloaded on subsequent days.
    def _apply_api_throttling_limit(self, yesterdays_date: date, most_recent_observation_date: date):

        _api_throttle_limit: timedelta = timedelta(days=float(self._api_throttling_limit))

        if yesterdays_date - most_recent_observation_date > _api_throttle_limit:
            _throttled_date = most_recent_observation_date + _api_throttle_limit
            self._wm_error_service.handle_error(f"Downloading throttled to avoid Weather Underground API throttling. "
                                                f"Only observations up until {_throttled_date} will be downloaded. "
                                                f"Later observations will be downloaded on later runs",
                                                "Info")
            return _throttled_date

        else:
            return yesterdays_date

    # Alerts user to the fact that no data has been logged to Weather Underground today.
    # Weather station may be offline for some reason.
    def _not_currently_gathering_data_warner(self):

        try:

            self._wu_service.start_wu_api_session()

            _retrieved_observations = self._wu_service.get_hourly_observations_for_date(datetime.now().date())

            if _retrieved_observations is None:
                self._wm_error_service.handle_error("Weather Underground is not logging observations today",
                                                    "Warning", send_email=True)

            self._wu_service.stop_wu_api_session()

        except WuApiException as ex:

            self._wm_error_service.handle_error(str(ex), "Critical", send_email=True, terminate=True, exc_info=ex)

    # Repeatedly call the Weather Underground API to fetch recent observations
    def _retrieve_recent_observations(self, most_recent_observation_date: date, fetch_up_to_date: date):

        _observation_list = []

        _date_counter: date = most_recent_observation_date + timedelta(days=1)

        try:

            self._wu_service.start_wu_api_session()

            while _date_counter <= fetch_up_to_date:

                _retrieved_observations = self._wu_service.get_hourly_observations_for_date(_date_counter)

                if not _retrieved_observations["observations"]:
                    self._wm_error_service.handle_error(f"No data for {_date_counter} retrieved "
                                                        f"from Weather Underground",
                                                        "Warning", send_email=True, batch_message=True)
                else:
                    _observation_list.append(_retrieved_observations)

                _date_counter = _date_counter + timedelta(days=1)

            self._wu_service.stop_wu_api_session()

        except WuApiException as ex:

            self._wm_error_service.handle_error(str(ex), "Critical", send_email=True, terminate=True)

        return _observation_list
