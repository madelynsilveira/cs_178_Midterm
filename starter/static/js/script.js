function draw_svg(container_id, margin, width, height){
    svg = d3.select("#"+container_id)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .style("background-color", "#F5F5F5")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    return svg
}

function draw_xaxis(plot_name, svg, height, scale){
    svg.append("g")
        .attr('class', plot_name + "-xaxis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(scale).tickSize(0))
}

function draw_yaxis(plot_name, svg, scale){
    svg.append("g")
        .attr('class', plot_name + "-yaxis")
        .call(d3.axisLeft(scale));
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

// TODO: Write a function that draws the scatterplot
function draw_scatter(data, svg, scale, name){
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

    // TODO: update x and y labels
    // TODO: update title (based on facet)
    
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
function update_scatter(data1, data2, svg1, svg2, scatter1_scale, scatter2_scale){
    // Remove existing points before drawing new ones
    svg1.selectAll(".scatter-point").remove();
    svg2.selectAll(".scatter-point").remove();

    draw_scatter(data1, svg1, scatter1_scale, 'scatter1');
    draw_scatter(data2, svg2, scatter2_scale, 'scatter2');
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
        update_scatter(results['scatter1_data'], results['scatter2_data'], scatter1_svg, scatter2_svg, scatter1_scale, scatter2_scale)
    })
}

function update_aggregate(value, key){  
    params = get_params()  
//   fetch('/update_aggregate', {
//       method: 'POST',
//       credentials: 'include',
//       body: JSON.stringify({value: value, key: key}),
//       cache: 'no-cache',
//       headers: new Headers({
//           'content-type': 'application/json'
//       })
//   }).then(async function(response){
//       var results = JSON.parse(JSON.stringify((await response.json())))
    
//       // Extract data
//       data = JSON.parse(results.data)
//       let x = results.x_column
//       let y = results.y_column

//       // Redraw bar graph 
//       draw_bar(data, x, y)
//   })
}