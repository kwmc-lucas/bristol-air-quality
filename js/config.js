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
        };

    // Public interface
    return {
        loadSpec: loadSpec,
        getSensorConfig: getSensorConfig
    }
} (jQuery));
