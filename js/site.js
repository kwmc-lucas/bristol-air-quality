"use strict";

// Single Page App inspired by:
// https://tutorialzine.com/2015/02/single-page-app-without-a-framework

$(function () {

    // checkboxes.click(function () {
    //     // The checkboxes in our app serve the purpose of filters.
    //     // Here on every click we add or remove filtering criteria from a filters object.
    //
    //     // Then we call this function which writes the filtering criteria in the url hash.
    //     createQueryHash(filters);
    // });

    function getSensorsHashLocation () {
        // Get url type hash string to represent current
        // sensor selection state
        let hashFragment = "sensor1=" + $('#sensor-id').val();
        return hashFragment;
    }

    function setPageTitle (title) {
        $('#page-title').text(title);
    }

    function hideSensorChoices () {
        $('#sensor-choices').addClass('hidden');
    }

    function showSensorChoices () {
        $('#sensor-choices').removeClass('hidden');
    }

    $.getJSON( "/data/luftdaten/aggregated/sensor-summary.json", function( data ) {
        // Get data about our products from products.json.

        // Call a function that will turn that data into HTML.
        // generateAllProductsHTML(data);
        populateSensors("#sensor-id", data);

        $('#nav-home').click(function () {
            window.location.hash = '';
        });

        $('#nav-day-of-week').click(function () {
            // var sensor1Code = $('#sensor-id').val();
            var sensorHashFragment = getSensorsHashLocation();
            window.location.hash = 'dayofweek/' + sensorHashFragment;
        });

        $('#nav-over-time').click(function () {
            // var sensor1Code = $('#sensor-id').val();
            var sensorHashFragment = getSensorsHashLocation();
            window.location.hash = 'overtime/' + '5';
        });


        // Manually trigger a hashchange to start the app.
        $(window).trigger('hashchange');
    });

    $(window).on('hashchange', function(){
        // On every hash change the render function is called with the new hash.
        // This is how the navigation of our app happens.
        render(decodeURI(window.location.hash));
    });

    function render(url) {
        // This function decides what type of page to show
        // depending on the current url hash value.


        // Get the keyword from the url.
        var temp = url.split('/')[0];

        // Hide whatever page is currently shown.
        // $('.main-content .page').removeClass('visible');
        setPageTitle("");
        hideSensorChoices();
        $('.main-content .page').addClass('hidden');

        console.log("Rendering", temp)

        var map = {

            // The Homepage.
            '': function() {

                // Clear the filters object, uncheck all checkboxes, show all the products
                // filters = {};
                // checkboxes.prop('checked',false);

                renderHomePage();
            },

            // Single Products page.
            '#dayofweek': function() {
                // Get the index of which product we want to show and call the appropriate function.
                var sensorCode1 = url.split('#dayofweek/')[1].trim();

                renderDayOfWeekPage(sensorCode1);
            },

            '#overtime': function() {
                // Get the index of which product we want to show and call the appropriate function.
                var sensorCode1 = url.split('#overtime/')[1].trim();

                renderOverTimePage(sensorCode1);
            },

            // Single Products page.
            '#product': function() {

                // Get the index of which product we want to show and call the appropriate function.
                var index = url.split('#product/')[1].trim();

                renderSingleProductPage(index, products);
            },

            // Page with filtered products
            '#filter': function() {

                // Grab the string after the '#filter/' keyword. Call the filtering function.
                url = url.split('#filter/')[1].trim();

                // Try and parse the filters object from the query string.
                try {
                    filters = JSON.parse(url);
                }
                // If it isn't a valid json, go back to homepage ( the rest of the code won't be executed ).
                catch(err) {
                    window.location.hash = '#';
                }

                renderFilterResults(filters, products);
            }

        };

        // Execute the needed function depending on the url keyword (stored in temp).
        if(map[temp]){
            map[temp]();
        }
        // If the keyword isn't listed in the above - render the error page.
        else {
            renderErrorPage();
        }
    }

    function populateSensors(el, config) {
        // Create drop down list of sensors
        $(el).append($('<option>', {value: '', text: 'Select sensor...'}));

        $.each(config.luftdaten_sensors, function (i, sensor) {
            var name = sensor.name + ' (' + sensor.code + ')',
                code = sensor.code;
            $(el).append($('<option>', {value: code, text: name}));
        })
    };

    function generateAllProductsHTML(data){
        // Uses Handlebars to create a list of products using the provided data.
        // This function is called only once on page load.
    }

    function renderHomePage(){
        // Hides and shows products in the All Products Page depending on the data it recieves.
        setPageTitle("Home");
        var page = $('.home-page');

        // Show the page itself.
        // (the render function hides all pages so we need to show the one we want).
        // page.addClass('visible');
        page.removeClass('hidden');
    }

    function renderDayOfWeekPage(sensorCode1) {
        setPageTitle("Best/worst times of the week");
        showSensorChoices();
        var page = $('.day-of-week');

        console.log(sensorCode1)


        // Show the page itself.
        // (the render function hides all pages so we need to show the one we want).
        page.removeClass('hidden');
    }

    function renderOverTimePage(sensorCode1) {
        setPageTitle("Air quality over time");
        showSensorChoices();
        var page = $('.day-of-week');

        console.log(sensorCode1)


        // Show the page itself.
        // (the render function hides all pages so we need to show the one we want).
        page.removeClass('hidden');
    }

    function renderSingleProductPage(index, data){
        // Shows the Single Product Page with appropriate data.
    }

    function renderFilterResults(filters, products){
        // Crates an object with filtered products and passes it to renderProductsPage.
        // renderProductsPage(results);
    }

    function renderErrorPage(){
        // Shows the error page.
    }

    function createQueryHash(filters){
        // Get the filters object, turn it into a string and write it into the hash.
    }

});

var luftviz = luftviz || {};

luftviz.page = (function ($) {
    // Private
    var populateSensors = function (el, config) {
        // Create drop down list of sensors
        // console.log(config);
        // $(el).append($('<option>', {value: null, text: 'Please select...'}));
        //
        // $.each(config.luftdaten_sensors, function (i, sensor) {
        //     console.log(sensor)
        //     var name = sensor.name + ' (' + sensor.code + ')',
        //         code = sensor.code;
        //     $(el).append($('<option>', {value: code, text: name}));
        // })
    };

    // Public
    return {
        populateSensors: populateSensors
    };
} (jQuery));

luftviz.chart24hourmean = (function (d3, vega) {
    // Private properties
    var valField = "P1",
        dateField = "timestamp",
        dateFormat = "%-d %b %y",
        euLimitPM10 = 50,
        euLimitPM2point5 = 50,
        vegaTooltipOptions = {
            showAllFields: false,
            fields: [
                {
                    field: dateField,
                    title: "Date",
                    formatType: "time",
                    format: dateFormat + " %H:%M"
                },
                {
                    field: valField,
                    title: "Val"
                }

            ]
        },

        // Private methods
        createSpec = function (sensorId, data, valField, dateField) {
            // Creates a vega spec
            var minMaxDates, minDate, maxDate, limitValues;

            // Find the min and max dates
            minMaxDates = d3.extent(data.map(d => d[dateField]));
            minDate = minMaxDates[0];
            maxDate = minMaxDates[1];

            // Create data for EU remmended limits line
            limitValues = [
                {
                    "date": minDate,
                    "value": euLimitPM10
                },
                {
                    "date": maxDate,
                    "value": euLimitPM10
                }
            ];

            var spec = {
                "$schema": "https://vega.github.io/schema/vega/v3.json",
                "width": 500,
                "height": 200,
                "padding": 5,

                "data": [
                    {
                        "name": "table",
                        "values": data
                        // "url": "/data/luftdaten_sds011_sensor_" + sensorId + "_24_hour_means.csv",
                        // "format": {
                        //     "type": "csv",
                        //     "parse": "auto"
                        // }
                    },
                    {
                        "name": "limitEU",
                        "values": limitValues
                    }
                ],

                "scales": [
                    {
                        "name": "x",
                        "type": "time",
                        "range": "width",
                        "domain": {"data": "table", "field": dateField}
                        // "nice": true
                        // "interval": "week", "step": 1
                    },
                    {
                        "name": "y",
                        "type": "linear",
                        "range": "height",
                        "nice": true,
                        "zero": true,
                        "domain": {"data": "table", "field": valField}
                    },
                    {
                        "name": "color",
                        "type": "ordinal",
                        "range": "category",
                        "domain": {"data": "table", "field": valField}
                    },
                    {
                        "name": "colorPM",
                        "type": "ordinal",
                        "range": "category",
                        "domain": {"data": "table", "field": valField}
                    }
                ],

                "axes": [
                    {
                        "orient": "bottom",
                        "scale": "x",
                        "format": dateFormat,
                        // "format": "%-m %b %y",
                        "labelOverlap": "true"
                    },
                    {
                        "orient": "left",
                        "scale": "y"
                    }
                ],

                "marks": [
                    // {
                    //     "type": "line",
                    //     "from": {"data": "table"},
                    //     "encode": {
                    //         "enter": {
                    //             "x": {"scale": "x", "field": dateField},
                    //             "y": {"scale": "y", "field": valField},
                    //             // "stroke": {"scale": "color", "field": "c"},
                    //             "strokeWidth": {"value": 2}
                    //         },
                    //         "update": {
                    //             "fillOpacity": {"value": 1}
                    //         },
                    //         "hover": {
                    //             "fillOpacity": {"value": 0.5}
                    //         }
                    //     }
                    // },
                    // Sensor data
                    {
                        "type": "symbol",
                        "from": {"data": "table"},
                        "encode": {
                            "enter": {
                                "x": {"scale": "x", "field": dateField},
                                "y": {"scale": "y", "field": valField},
                                "fill": {"value": "#ff0000"},
                                // "stroke": {"value": "#000"},
                                // "strokeWidth": {"value": 1},
                                "size": {"value": 5}
                            }
                        }
                    },
                    // Limits
                    {
                        "type": "line",
                        "from": {"data": "limitEU"},
                        "encode": {
                            "enter": {
                                "x": {"scale": "x", "field": "date"},
                                "y": {"scale": "y", "field": "value"},
                                // "stroke": {"scale": "color", "field": "c"},
                                "strokeWidth": {"value": 2}
                            },
                            "update": {
                                "fillOpacity": {"value": 1}
                            },
                            "hover": {
                                "fillOpacity": {"value": 0.5}
                            }
                        }
                    }
                ]
            };
            return spec;
        },
        render = function (el, sensorId) {
            var dataUrl = "/website/data/luftdaten_sds011_sensor_" + sensorId + "_24_hour_means.csv";
            d3.csv(dataUrl, function(data) {
                // Set data types
                var parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S");
                data.forEach(function(d) {
                    d[dateField] = parseDate(d[dateField]);
                    d.P1 = +d.P1;
                });

                var specCopy = createSpec(sensorId, data, valField, dateField),
                    view = new vega.View(vega.parse(specCopy))
                        .renderer('canvas')  // set renderer (canvas or svg)
                        .initialize(el) // initialize view within parent DOM container
                        .hover()             // enable hover encode set processing
                        .run();
                vegaTooltip.vega(view, vegaTooltipOptions);
            });
        };

    // Public interface
    return {
        render: render
    }
} (d3, vega));




// var opt = {};
// var view = null;


// vegaEmbed("#view2", spec).then(function (result) {
//         vegaTooltip.vega(result.view, tooltipOption);
//         // view = result.view;
//         // vegaTooltip.vega(result.view);
//     }).catch(console.error);


// var view;
//
// function render(spec) {
//     view = new vega.View(vega.parse(spec))
//         .renderer('canvas')  // set renderer (canvas or svg)
//         .initialize('#view') // initialize view within parent DOM container
//         .hover()             // enable hover encode set processing
//         .run();
//     vegaTooltip.vega(view, vegaTooltipOptions);
// }
// render(spec);

var scale = d3.scaleBand()
    .domain([1, 2, 3])
    .range([0, 100]);
// console.log(scale(1))
// console.log(scale(2))
// console.log(scale(3))

var scaleOrd = d3.scaleOrdinal()
    .domain([1, 2, 3])
    .range([d3.rgb("red"), d3.rgb("green"), d3.rgb("blue")]);
// console.log(scaleOrd(1))
// console.log(scaleOrd(1.5))
// console.log(scaleOrd(2))
// console.log(scaleOrd(3))
