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

    // DEPRECATED
    function getSensorsHashLocation () {
        // Get url type hash string to represent current
        // sensor selection state
        let hashFragment = "sensor1=" + $('#sensor-id').val();
        return hashFragment;
    }

    function getSensorsHashFragment (elSensor1, elDate1, elSensor2, elDate2) {
        // Get url type hash fragment to represent current
        // sensor selection state
        return "sensor1=" + $(elSensor1).val() +
            "&date1=" + $(elDate1).val();
    }

    function getDayOfWeekSensorsHashFragment () {
        // Get url type hash fragment to represent current
        // sensor selection state
        return getSensorsHashFragment(
            '#sensor-code-day-of-week-1',
            '#sensor-date-day-of-week-1',
            '#sensor-code-day-of-week-2',
            '#sensor-date-day-of-week-2',
        );
    }

    function getOverTimeSensorsHashFragment () {
        // Get url type hash fragment to represent current
        // sensor selection state
        return getSensorsHashFragment(
            '#sensor-code-over-time-1',
            '#sensor-date-over-time-1',
            '#sensor-code-over-time-2',
            '#sensor-date-over-time-2',
        );
    }

    function parseSensorsHashFragment (fragment) {
        let keyValuePairs = fragment.split('&'),
            store = {
                sensor1: null,
                date1: null,
                sensor2: null,
                date2: null
            };
        $.each(keyValuePairs, function (i, keyValuePair) {
            let keyValue = keyValuePair.split('=');
            if (keyValue.length !== 2) {
                throw new Error("Query string key value pair not formatted correctly");
            }
            store[keyValue[0]] = keyValue[1] === 'null' ? null : keyValue[1];
        });
        console.log(store);
        return store;
    }

    function setPageTitle (title) {
        $('#page-title').text(title);
    }

    function parseHyphenatedDate (dateStr) {
        let parts = dateStr.split('-');
        return {year: parts[0], month: parts[1]};
    }

    // DEPRECATED
    // function hideSensorChoices () {
    //     $('#sensor-choices').addClass('hidden');
    // }

    // DEPRECATED
    // function showSensorChoices () {
    //     $('#sensor-choices').removeClass('hidden');
    // }

    $.getJSON( "/data/luftdaten/aggregated/sensor-summary.json", function( configData ) {
        // Get data about our products from products.json.

        // Call a function that will turn that data into HTML.
        // generateAllProductsHTML(data);
        // populateSensors('#sensor-id', configData);

        $('#sensor-code-day-of-week-1, #sensor-date-day-of-week-1').change(function () {
            // Fill in the date drop down for new sensor
            // let sensorCode = this.value,
            //     sensorConfig = config.getSensorConfig(configData, sensorCode);
            // console.log(sensorConfig)
            // let selectedVal = '2018-6';
            // populate24HourMeansDates('#sensor-dates-1', sensorConfig, selectedVal);
            let hashFragment = getDayOfWeekSensorsHashFragment();
            window.location.hash = 'dayofweek/' + hashFragment;
        });

        $('#sensor-code-over-time-1, #sensor-date-over-time-1').change(function () {
            let hashFragment = getOverTimeSensorsHashFragment();
            window.location.hash = 'overtime/' + hashFragment;
        });

        // $('#sensor-id').change(function () {
        //     // Fill in the date drop down for new sensor
        //     let sensorCode = this.value,
        //         sensorConfig = config.getSensorConfig(configData, sensorCode);
        //     console.log(sensorConfig)
        //     let selectedVal = '2018-6';
        //     populate24HourMeansDates('#sensor-dates-1', sensorConfig, selectedVal);
        // });

        $('#nav-home').click(function () {
            window.location.hash = '';
        });

        $('#nav-day-of-week').click(function () {
            let hashFragment = getDayOfWeekSensorsHashFragment();
            window.location.hash = 'dayofweek/' + hashFragment;
        });

        $('#nav-over-time').click(function () {
            let hashFragment = getOverTimeSensorsHashFragment();
            window.location.hash = 'overtime/' + hashFragment;
            // var sensor1Code = $('#sensor-id').val();
            // var sensorHashFragment = getSensorsHashLocation();
            // window.location.hash = 'overtime/' + '5';
        });

        $(window).on('hashchange', function(){
            // On every hash change the render function is called with the new hash.
            // This is how the navigation of our app happens.
            render(decodeURI(window.location.hash), configData);
        });

        // Manually trigger a hashchange to start the app.
        $(window).trigger('hashchange');
    });

    function render(url, config) {
        // This function decides what type of page to show
        // depending on the current url hash value.


        // Get the keyword from the url.
        var temp = url.split('/')[0];

        // Hide whatever page is currently shown.
        // $('.main-content .page').removeClass('visible');
        setPageTitle("");
        // hideSensorChoices();
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

            // Day of week page
            '#dayofweek': function() {
                // Get the info from url hash string and render page
                var selectedHashFragment = url.split('#dayofweek/')[1].trim(),
                    selectedInfo = parseSensorsHashFragment(selectedHashFragment);
                renderDayOfWeekPage(
                    config,
                    selectedInfo.sensor1,
                    selectedInfo.date1,
                    selectedInfo.sensor2,
                    selectedInfo.date2
                );
            },

            // Time series page
            '#overtime': function() {
                // Get the info from url hash string and render page
                var selectedHashFragment = url.split('#overtime/')[1].trim(),
                    selectedInfo = parseSensorsHashFragment(selectedHashFragment);
                renderOverTimePage(
                    config,
                    selectedInfo.sensor1,
                    selectedInfo.date1,
                    selectedInfo.sensor2,
                    selectedInfo.date2
                );
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

    function populateSensors (el, config, selectedVal) {
        // Create drop down list of sensors
        $(el).append($('<option>', {value: '', text: 'Select sensor...'}));

        $.each(config.luftdaten_sensors, function (i, sensor) {
            var name = sensor.name + ' (' + sensor.code + ')',
                code = sensor.code;
            $(el).append($('<option>', {
                value: code,
                text: name,
                selected: code.toString() === selectedVal
            }));
        });
    };

    function getMonthName(monthNumber) {
        // Use non zero based month number, e.g. May = 5
        const monthNames = [
            "January", "February", "March",
            "April", "May", "June",
            "July", "August", "September",
            "October", "November", "December"
        ];
        return monthNames[monthNumber-1];
    }

    function sortDates (listOfDates) {
        listOfDates.sort(function (a, b) {
            if (a.year === b.year) {
                if (a.month < b.month)
                    return -1;
                if (a.month > b.month)
                    return 1;
                return 0;
            } else {
                if (a.year < b.year)
                    return -1;
                if (a.year > b.year)
                    return 1;
                return 0;
            }
        })
        return listOfDates;
    }

    function populateDates (el, sensorConfig, selectedVal, dataType) {
        // Create drop down list of dates
        $(el).append($('<option>', {value: '', text: 'Select date...'}));

        let listOfDates = [];
        $.each(sensorConfig[dataType].available_dates, function (year, yearData) {
            $.each(yearData, function (i, monthData) {
                // console.log(year_i, year, i, month)
                listOfDates.push({
                    'year': year,
                    'month': monthData.month
                });
            });
        });
        listOfDates = sortDates(listOfDates);

        $.each(listOfDates, function (i, dateInfo) {
            let optionVal = dateInfo.year + '-' + dateInfo.month;
            $(el).append(
                $(
                    '<option>',
                    {
                        value: optionVal,
                        text: getMonthName(dateInfo.month) + ' ' + dateInfo.year,
                        selected: optionVal === selectedVal
                    }
                )
            );
        });
    };

    function populate24HourMeansDates (el, sensorConfig, selectedVal) {
        populateDates(el, sensorConfig, selectedVal, '24_hour_means')
    }

    function populateDayOfWeekDates (el, sensorConfig, selectedVal) {
        populateDates(el, sensorConfig, selectedVal, 'day_of_week')
    }

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

    function renderDayOfWeekPage(configData, sensorCode1, date1, sensorCode2, date2) {
        setPageTitle("Best/worst times of the week");
        // showSensorChoices();
        var page = $('.day-of-week'),
            sensors = [
                {id: 1, code: sensorCode1, date: date1},
                {id: 2, code: sensorCode2, date: date2}
            ],
            date1Info,
            dataUrlChart1;

        // Populate drop downs
        $.each(sensors, function (i, sensor) {
            populateSensors('#sensor-code-day-of-week-' + sensor.id, configData, sensor.code);
            if (sensor.code) {
                let sensorConfig = config.getSensorConfig(configData, sensor.code);
                populateDayOfWeekDates('#sensor-date-day-of-week-' + sensor.id, sensorConfig, sensor.date);
            }
        });

        // Show chart 1
        if (sensorCode1 && date1) {
            date1Info = parseHyphenatedDate(date1)
            dataUrlChart1 = config.dayOfWeekDataUrl(configData, sensorCode1, date1Info.year, date1Info.month);
            console.log(dataUrlChart1);
            luftviz.dayOfWeekCircular.render("#day-of-week-chart1", dataUrlChart1);
        }

        // Show the page itself.
        // (the render function hides all pages so we need to show the one we want).
        page.removeClass('hidden');
    }

    function renderOverTimePage(configData, sensorCode1, date1, sensorCode2, date2) {
        setPageTitle("Air quality over time");
        // showSensorChoices();
        var page = $('.over-time'),
            sensors = [
                {id: 1, code: sensorCode1, date: date1},
                {id: 2, code: sensorCode2, date: date2}
            ];

        // Populate drop downs
        $.each(sensors, function (i, sensor) {
            populateSensors('#sensor-code-over-time-' + sensor.id, configData, sensor.code);
            if (sensor.code) {
                let sensorConfig = config.getSensorConfig(configData, sensor.code);
                populate24HourMeansDates('#sensor-date-over-time-' + sensor.id, sensorConfig, sensor.date);
            }
        });

        // Show chart 1
        // if (sensorCode1 && date1) {
        //     date1Info = parseHyphenatedDate(date1)
        //     dataUrlChart1 = config.TODOdayOfWeekDataUrl(configData, sensorCode1, date1Info.year, date1Info.month);
        //     console.log(dataUrlChart1);
        //     luftviz.chart24hourmean.render("#day-of-week-chart1", sensorCode1);
        // }

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
