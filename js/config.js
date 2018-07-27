"use strict";

var config = config || (function ($) {
    // Private properties
    var valField = "P1",
        dateField = "timestamp",

        // Private methods
        loadSpec = function (url) {
            // Return promise
            return $.getJSON(url);
        };

    // Public interface
    return {
        loadSpec: loadSpec
    }
} (jQuery));
