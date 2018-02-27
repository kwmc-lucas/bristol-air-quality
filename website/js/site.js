var valField = "P1",
    dateField = "timestamp";

var spec = {
    "$schema": "https://vega.github.io/schema/vega/v3.json",
    "width": 500,
    "height": 200,
    "padding": 5,

    "data": [
        {
            "name": "table",
            "url": "/data/luftdaten_sds011_sensor_7675_24_hour_means.csv",
            "format": {
                "type": "csv",
                "parse": "auto"
            }
        }
    ],

    "scales": [
        {
            "name": "x",
            "type": "time",
            "range": "width",
            "domain": {"data": "table", "field": dateField}
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
        }
    ],

    "axes": [
        {
            "orient": "bottom",
            "scale": "x",
            "format": "%-m %b %y",
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
        }
    ]
};

var opt = {};

vegaEmbed("#view2", spec, opt).then(function (result) {
    var tooltipOption = {
            showAllFields: false,
            fields: [
                {
                    field: dateField,
                    title: "Date",
                    formatType: "time",
                    format: "%B %e",
                    valueAccessor: function (d) {
                        console.log(d);
                        return 1;
                    }
                },
                {
                    field: valField,
                    title: "Val"
                }

            ]
        };
        vegaTooltip.vega(result.view, tooltipOption);
        // vegaTooltip.vega(result.view);
    }).catch(console.error);

// var view;
//
// function render(spec) {
//     view = new vega.View(vega.parse(spec))
//         .renderer('canvas')  // set renderer (canvas or svg)
//         .initialize('#view') // initialize view within parent DOM container
//         .hover()             // enable hover encode set processing
//         .run();
// }
// render(spec);
