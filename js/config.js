"use strict";

var config = config || (function ($) {
    // Private properties
    var valField = "P1",
        dateField = "timestamp",

        // Private methods
        loadSpec = function (url) {
            // Return promise
            return $.getJSON(url);
        },

        getSensorConfig = function (config, sensorCode) {
            let i;

            for (i = 0; i < config.luftdaten_sensors.length; i++) {
                if (config.luftdaten_sensors[i].code.toString() === sensorCode) {
                    return config.luftdaten_sensors[i];
                }
            }

            return null;
        },

        dayOfWeekDataUrl = function (config, sensorCode, year, month) {
            let sensorConfig = getSensorConfig(config, sensorCode),
                datesInfo = sensorConfig.day_of_week.available_dates[year.toString()],
                url = null, i;
            for (i = 0; i < datesInfo.length; i++) {
                if (datesInfo[i].month.toString() === month.toString()) {
                    url = datesInfo[i].path;
                    break;
                }
            }
            return url;
        };

    // Public interface
    return {
        loadSpec: loadSpec,
        getSensorConfig: getSensorConfig,
        dayOfWeekDataUrl: dayOfWeekDataUrl
    }
} (jQuery));
