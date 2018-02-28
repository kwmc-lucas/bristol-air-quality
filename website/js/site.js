"use strict";

var luftviz = luftviz || {};

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
            var dataUrl = "/data/luftdaten_sds011_sensor_" + sensorId + "_24_hour_means.csv";
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
console.log(scale(1))
console.log(scale(2))
console.log(scale(3))

var scaleOrd = d3.scaleOrdinal()
    .domain([1, 2, 3])
    .range([d3.rgb("red"), d3.rgb("green"), d3.rgb("blue")]);
console.log(scaleOrd(1))
console.log(scaleOrd(1.5))
console.log(scaleOrd(2))
console.log(scaleOrd(3))
