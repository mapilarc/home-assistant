"""
homeassistant.components.sensor.time_date
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Date and Time service.

Configuration:

To use the Date and Time sensor you will need to add something like the
following to your configuration.yaml file.

sensor:
  platform: time_date
  display_options:
    - 'time'
    - 'date'
    - 'date_time'
    - 'time_date'
    - 'time_utc'
    - 'beat'

Variables:

display_options
*Required
The variable you wish to display. See the configuration example above for a
list of all available variables.
"""
import logging

import homeassistant.util.dt as dt_util
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
OPTION_TYPES = {
    'time': 'Time',
    'date': 'Date',
    'date_time': 'Date & Time',
    'time_date': 'Time & Date',
    'beat': 'Time (beat)',
    'time_utc': 'Time (UTC)',
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Get the Time and Date sensor. """

    if hass.config.time_zone is None:
        _LOGGER.error("Timezone is not set in Home Assistant config")
        return False

    dev = []
    for variable in config['display_options']:
        if variable not in OPTION_TYPES:
            _LOGGER.error('Option type: "%s" does not exist', variable)
        else:
            dev.append(TimeDateSensor(variable))

    add_devices(dev)


# pylint: disable=too-few-public-methods
class TimeDateSensor(Entity):
    """ Implements a Time and Date sensor. """

    def __init__(self, option_type):
        self._name = OPTION_TYPES[option_type]
        self.type = option_type
        self._state = None
        self.update()

    @property
    def name(self):
        """ Returns the name of the device. """
        return self._name

    @property
    def state(self):
        """ Returns the state of the device. """
        return self._state

    def update(self):
        """ Gets the latest data and updates the states. """

        time_date = dt_util.utcnow()
        time = dt_util.datetime_to_time_str(dt_util.as_local(time_date))
        time_utc = dt_util.datetime_to_time_str(time_date)
        date = dt_util.datetime_to_date_str(dt_util.as_local(time_date))

        # Calculate the beat (Swatch Internet Time) time without date.
        hours, minutes, seconds = time_date.strftime('%H:%M:%S').split(':')
        beat = ((int(seconds) + (int(minutes) * 60) + ((int(hours) + 1) *
                                                       3600)) / 86.4)

        if self.type == 'time':
            self._state = time
        elif self.type == 'date':
            self._state = date
        elif self.type == 'date_time':
            self._state = date + ', ' + time
        elif self.type == 'time_date':
            self._state = time + ', ' + date
        elif self.type == 'time_utc':
            self._state = time_utc
        elif self.type == 'beat':
            self._state = '{0:.2f}'.format(beat)
