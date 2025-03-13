function draw_svg(container_id, margin, width, height){
    svg = d3.select("#"+container_id)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .style("background-color", "#f5f5f5")
    .append("g")
    .attr("transform", "translate(" + 1.5*margin.left + "," + margin.bottom + ")");
    return svg
}

function draw_xaxis(plot_name, svg, height, scale){
    svg.append("g")
        .attr('class', plot_name + "-xaxis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(scale).tickSize(0))

    // Add the x-axis label (initially)
    svg.append("text")
        .attr("class", "x-label")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + 36)
        .text("CGPA");
}

function draw_yaxis(plot_name, svg, scale){
    svg.append("g")
        .attr('class', plot_name + "-yaxis")
        .call(d3.axisLeft(scale));

    // Add the y-axis label (initially)
    svg.append("text")
    .attr("class", "y-label") // add class name "y-label" so we can update it
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("y", -margin.left) // add some padding between y-axis label and y-axis
    .attr("x", -height / 2 + 10) // Adjust the x position to center the label vertically
    .text("CGPA");
}

function draw_axis(plot_name, axis, svg, height, domain, range, discrete){
    if (discrete){
        var scale = d3.scaleBand()
            .domain(domain)
            .range(range)
            .padding([0.2])
    } else {
        var scale = d3.scaleLinear()
            .domain(domain)
            .range(range);
    }
    if (axis=='x'){
        draw_xaxis(plot_name, svg, height, scale)
    } else if (axis=='y'){
        draw_yaxis(plot_name, svg, scale)
    }
    return scale
}

function draw_axes(plot_name, svg, width, height, domainx, domainy, x_discrete){
    var x_scale = draw_axis(plot_name, 'x', svg, height, domainx, [0, width], x_discrete)
    var y_scale = draw_axis(plot_name, 'y', svg, height, domainy, [height, 0], false)
    return {'x': x_scale, 'y': y_scale}
}

function draw_slider(column, min, max, scatter1_svg, scatter2_svg, scatter1_scale, scatter2_scale){
    slider = document.getElementById(column+'-slider')
    noUiSlider.create(slider, {
      start: [min, max],
      connect: false,
          tooltips: true,
      step: 1,
      range: {'min': min, 'max': max}
    });
    slider.noUiSlider.on('change', function(){
        update(scatter1_svg, scatter2_svg, scatter1_scale, scatter2_scale)
    });
}

function draw_reg_line(svg, slope, intercept, data, scale){
    // Remove previous regression line 
    svg.selectAll(".line").remove();

    // Generate the points for the regression line using the custom equation y = mx + b
    const lineData = [
    { x: d3.min(data, d=> d.x), y: slope * d3.min(data, d => d.x) + intercept }, 
    { x: d3.max(data, d => d.x), y: slope * d3.max(data, d => d.x) + intercept } // Point at max x
    ];

    // Create the regression line
    svg.append("path")
        .data([lineData])
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", "deeppink")
        .attr("opacity", .60)
        .attr("stroke-width", 2)
        .attr("d", d3.line()
            .x(d => scale.x(d.x))
            .y(d => scale.y(d.y))
        );
    console.log("in svg")
}

// TODO: Write a function that draws the scatterplot
function draw_scatter(data, svg, scale, name, x_label, y_label, title, stats){
    // Update scale for x and y axis
    scale.x.domain(d3.extent(data, d => d.x));
    scale.y.domain(d3.extent(data, d => d.y));

    // Update axes and labels
    svg.select("." + name + "-yaxis")
      .transition().duration(500)
      .call(d3.axisLeft(scale.y));
    svg.select("." + name + "-xaxis")
        .transition().duration(500)
        .call(d3.axisBottom(scale.x));

    // Update x and y labels
    svg.select(".y-label")
      .transition().duration(500)
      .text(y_label)
    svg.select(".x-label")
      .transition().duration(500)
      .text(x_label)

    // Update title (based on facet)
    document.getElementById(name + "-header").innerText = title;
    
    // Draw regression line for each graph
    draw_reg_line(svg, stats['slope'], stats['intercept'], data, scale);
   
    // Add data points
    console.log(data[0].x)
    console.log(scale)
    svg.selectAll(".scatter-point")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "scatter-point")
        .attr("cx", d => scale.x(d.x)) 
        .attr("cy", d => scale.y(d.y)) 
        .attr("r", 3) 
        .attr("fill", "#87CEEB") 
        .attr("stroke", "black") 
        .attr("stroke-width", 0.5); 
         
    // Update student totals
    document.getElementById(name + "-total").innerText = `Total Students: ${stats['total']}`;

    // Update student averages
    x_avg = stats['x_avg'].toFixed(2); 
    y_avg = stats['y_avg'].toFixed(2);
    document.getElementById(name + "-x-avg").innerText = `Average ${x_label}: ${x_avg}`;

    // Only add y average if it is different from the x average 
    document.getElementById(name + "-y-avg").innerText = `Average ${y_label}: ${y_avg}`;
    if (x_label == y_label) {
      document.getElementById(name + "-y-avg").innerText = ``;
    };
}

// TODO: Write a function that extracts the selected days and minimum/maximum values for each slider
function get_params(){
    var checkboxes = document.querySelectorAll('input[class="extracurricular activities-selected"]:checked')
    var activities = Array.from(checkboxes).map(checkbox => checkbox.value);
    var checkboxes = document.querySelectorAll('input[class="placementtraining-selected"]:checked')
    var training =  Array.from(checkboxes).map(checkbox => checkbox.value);

    var x = document.getElementById('X').value;
    var y = document.getElementById('Y').value;
    var facet = document.getElementById('Facet').value;
    
    var internships = document.getElementById("internships-slider").noUiSlider.get()
    var projects = document.getElementById("projects-slider").noUiSlider.get()
    var aptitude = document.getElementById("aptitudetestscore-slider").noUiSlider.get()
    var softskills = document.getElementById("softskillsrating-slider").noUiSlider.get()
    var ssc_marks = document.getElementById("ssc_marks-slider").noUiSlider.get()
    var hsc_marks= document.getElementById("hsc_marks-slider").noUiSlider.get()

    return {'Internships': internships, 'Projects': projects, 'AptitudeTestScore': aptitude,
      'SoftSkillsRating': softskills, 'SSC_Marks': ssc_marks, 'HSC_Marks': hsc_marks, 
      'ExtracurricularActivities': activities, 'PlacementTraining': training,
      'X': x, 'Y': y, 'Facet': facet}
}

// TODO: Write a function that removes the old data points and redraws the scatterplot
function update_scatter(data1, data2, svg1, svg2, scatter1_scale, scatter2_scale, 
  x, y, label1, label2, stats1, stats2){
    // Remove existing points before drawing new ones
    svg1.selectAll(".scatter-point").remove();
    svg2.selectAll(".scatter-point").remove();

    draw_scatter(data1, svg1, scatter1_scale, 'scatter1', x, y, label1, stats1);
    draw_scatter(data2, svg2, scatter2_scale, 'scatter2', x, y, label2, stats2);
}

function update(scatter1_svg, scatter2_svg, scatter1_scale, scatter2_scale){
    params = get_params()
    fetch('/update', {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(params),
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        })
    }).then(async function(response){
        var results = JSON.parse(JSON.stringify((await response.json())))
        // Grab labels from the results 
        x = results['x_label']
        y = results['y_label']
        label1 = results['scatter1_label']
        label2 = results['scatter2_label']
        stats1 = results['scatter1_stats']
        stats2 = results['scatter2_stats']

        update_scatter(results['scatter1_data'], results['scatter2_data'], 
          scatter1_svg, scatter2_svg, scatter1_scale, scatter2_scale, 
          x, y, label1, label2, stats1, stats2)
    })
}