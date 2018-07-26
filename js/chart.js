d3.csv("/website/data/luftdaten_sds011_sensor_7675_by_weekday_and_hour.csv", function(data) {
    var valueField = "P1";

    // Set data types
    data.forEach(function(d) {
        d.hourOfDay = +d.hourOfDay;
        d.P1 = +d.P1;
    });
    // console.log(data[0]);

    // The data for circular heat map list of values, one for each segment,
    // spiraling out from the centre outwards. This means we need to order
    // the rows by day of week and hour of day.

    var days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

    // Make an lookup with order of days, e.g. {"Monday": 0, "Tuesday": 1, ...}
    var daysOrder = {};
    days.forEach( function (day, i) {
        daysOrder[day] = i;
    });
    console.log(daysOrder)

    // Set segment number for each day/hour (starting from Monday 00:00)
    data.forEach(function(d) {
        d.segmentId = (daysOrder[d.dayOfWeek] * 24) + d.hourOfDay
    });

    if (data.length !== 24 * 7) {
        throw new Error("Expected one weeks worth of data values, one for each hour of the day")
    }

    // Sort the data
    data.sort( function(a, b) {return a.segmentId - b.segmentId} );

    var chart = circularHeatChart()
        .accessor(function(d) {return d[valueField];})
        .segmentHeight(20)
        .innerRadius(20)
        .numSegments(24)
        .radialLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        .segmentLabels(["Midnight", "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", "10am", "11am", "Midday", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm"])
        .margin({top: 20, right: 0, bottom: 20, left: 280});

    d3.select('#circleChart')
        .selectAll('svg')
        .data([data])
        .enter()
        .append('svg')
        .call(chart);

        /* Add a mouseover event */
        d3.selectAll("#circleChart path").on('mouseover', function() {
        	var d = d3.select(this).data()[0],
                txt = d.dayOfWeek + ' ' + ("0" + d.hourOfDay).slice(-2) + ':00 has value ' + d[valueField];
            d3.select("#info").text(txt);
        });
        d3.selectAll("#circleChart svg").on('mouseout', function() {
            d3.select("#info").text('');
        });
});
