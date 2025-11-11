import argparse
import configparser
import os
import sys
import traceback
from DateTimeProvider import DateTimeProvider
from MainRoutine import MainRoutine
from WeatherUndergroundApiService import WeatherUndergroundApiService
from WMDatabaseService import WMDatabaseService
from WMErrorService import WMErrorService


# Launches the Weather Manager Downloader

# Define unhandled exception handler
def _catch_unhandled_exceptions(exception_type, value, trace_back):
    trace_back_strings = traceback.format_exception(exception_type, value, trace_back)
    error_message = "Unhandled exception:" + "\r\n".join(trace_back_strings)

    error_service.handle_error(error_message, "Critical", send_email=True,
                               terminate=True)


# Get command line argument
command_line_parser = argparse.ArgumentParser(description="Download observations from Weather Underground")
command_line_parser.add_argument("ConfigFile", metavar="configfile", type=str,
                                 help="Fully qualified name of config file")
command_line_arguments = command_line_parser.parse_args()
if not os.path.isfile(command_line_arguments.ConfigFile):
    print("The supplied configuration file name does not exist")
    sys.exit()


# Get configuration
_config = configparser.ConfigParser(interpolation=None)
_config.read(command_line_arguments.ConfigFile)
if _config is None:
    print(f"Could not read the configuration file config.ini in {os.getcwd()}")
    input("Press return to continue")
    sys.exit()

# Instance the services for WU Api, database, date and errors

error_service = WMErrorService(_config.get("EMail", "Host"),
                               _config.get("EMail", "Port"),
                               _config.get("EMail", "Username"),
                               _config.get("EMail", "Password"),
                               _config.get("EMail", "FromAddress"),
                               _config.get("EMail", "FromName"),
                               _config.get("EMail", "ToAddress"),
                               _config.get("EMail", "ToName"))

database_service = WMDatabaseService(_config.get("Database", "IPAddress"),
                                     _config.get("Database", "Port"),
                                     _config.get("Database", "UserId"),
                                     _config.get("Database", "Password"),
                                     _config.get("Database", "DatabaseName"),
                                     error_service)

date_time_provider = DateTimeProvider()

wu_underground_api_service = WeatherUndergroundApiService(_config.get("WeatherUnderground", "StationId"),
                                                          _config.get("WeatherUnderground", "ApiKey"))

# Assign function to log unhandled exceptions
sys.excepthook = _catch_unhandled_exceptions

# Instance the MainRoutine injecting these services.

main_routine = MainRoutine(database_service,
                           date_time_provider,
                           wu_underground_api_service,
                           error_service,
                           _config.get("Downloader", "ApiThrottlingLimit"),
                           _config.get("WeatherUnderground", "InitialObservationDate"),
                           _config.get("Downloader", "LogFile"))

# Run the MainRoutine
main_routine.download_recent_observations()
