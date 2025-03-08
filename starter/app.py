from flask import Flask, render_template, request
import duckdb

app = Flask(__name__)
continuous_columns = ['Internships', 'Projects', 'AptitudeTestScore', 'SoftSkillsRating', 'SSC_Marks', 'HSC_Marks']
discrete_columns = ['ExtracurricularActivities', 'PlacementTraining']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
sorted_months = sorted(months)

# Dictionary to hold selected values
selected = {
  "X" : 'AptitudeTestScore',
  "Y" : 'CGPA',
  "Facet" : 'PlacementStatus'
}
# Dictionary to hold facet options
facet_options = {
  "PlacementStatus": ['Placed', 'NotPlaced'],
  "ExtracurricularActivities": ["Yes", "No"],
  "PlacementTraining": ["Yes", "No"]
}

@app.route('/')
def index():
    x = selected['X']
    y = selected['Y']
    scatter_ranges_query = f'SELECT MIN({x}), MAX({x}), MIN({y}), MAX({y}), FROM placementdata.csv'
    scatter_ranges_results = duckdb.sql(scatter_ranges_query).df()
    
    scatter_ranges = scatter_ranges_results.iloc[0].tolist()

    # Write a query that retrieves the the minimum and maximum value for each slider
    filter_ranges_query = f'SELECT MIN(Internships), MAX(Internships), MIN(Projects), MAX(Projects), MIN(AptitudeTestScore), MAX(AptitudeTestScore), MIN(SoftSkillsRating), MAX(SoftSkillsRating), MIN(SSC_Marks), MAX(SSC_Marks), MIN(HSC_Marks), MAX(HSC_Marks), FROM placementdata.csv'
    filter_ranges_results = duckdb.sql(filter_ranges_query).df()
    min_internships = float(filter_ranges_results['min(Internships)'].iloc[0])
    max_internships = float(filter_ranges_results['max(Internships)'].iloc[0])
    min_projects = float(filter_ranges_results['min(Projects)'].iloc[0])
    max_projects = float(filter_ranges_results['max(Projects)'].iloc[0])
    min_aptitude = float(filter_ranges_results['min(AptitudeTestScore)'].iloc[0])
    max_aptitude = float(filter_ranges_results['max(AptitudeTestScore)'].iloc[0])
    min_softskillsrating = float(filter_ranges_results['min(SoftSkillsRating)'].iloc[0])
    max_softskillsrating = float(filter_ranges_results['max(SoftSkillsRating)'].iloc[0])
    min_ssc = float(filter_ranges_results['min(SSC_Marks)'].iloc[0])
    max_ssc = float(filter_ranges_results['max(SSC_Marks)'].iloc[0])
    min_hsc = float(filter_ranges_results['min(HSC_Marks)'].iloc[0])
    max_hsc = float(filter_ranges_results['max(HSC_Marks)'].iloc[0])

    # Create a dictionary where each key is a filter and values are the minimum and maximum values
    filter_ranges = {'Internships': [min_internships, max_internships],
                     'Projects': [min_projects, max_projects],
                     'AptitudeTestScore': [min_aptitude, max_aptitude],
                     'SoftSkillsRating': [min_softskillsrating, max_softskillsrating],
                     'SSC_Marks': [min_ssc, max_ssc],
                     'HSC_Marks': [min_hsc, max_hsc]}

    options = ['CGPA', 'Internships', 'Projects', 'Workshops/Certifications',
      'AptitudeTestScore', 'SoftSkillsRating', 'SSC_Marks', 'HSC_Marks']
    facets = ['ExtracurricularActivities', 'PlacementTraining', 'PlacementStatus']

    return render_template(
        'index.html', x_options=options, y_options=options, facet_options=facets,
        filter_ranges=filter_ranges, scatter_ranges=scatter_ranges
    )

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()

    x = request_data.get('X')
    y = request_data.get('Y')
    facet = request_data.get('Facet')
    
    # Update where clause from sliders
    # continuous_predicate = ' AND '.join([f'({column} >= 0 AND {column} <= 0)' for column in continuous_columns]) 
    continuous_predicate = ' AND '.join([
        f'({column} BETWEEN {request_data[column][0]} AND {request_data[column][1]})' 
        for column in continuous_columns]) 

    # Update where clause from radio buttons
    activities = request_data.get('ExtracurricularActivities')
    training = request_data.get('PlacementTraining')
    discrete_predicate = f'ExtracurricularActivities = {activities} AND PlacementTraining = {training}'


    # Combine where clause from sliders and checkboxes
    facet = selected['Facet']
    facetTrue = facet_options[facet][0]
    facetFalse = facet_options[facet][1]
    
    predicate = ' AND '.join([continuous_predicate, discrete_predicate]) 
    scatter1_query = f'SELECT {x}, {y}, FROM placementdata.csv WHERE {facet} = {facetTrue} AND {predicate} '
    scatter2_query = f'SELECT {x}, {y}, FROM placementdata.csv WHERE NOT {facet} = {facetFalse} AND {predicate}'

    scatter1_results = duckdb.sql(scatter1_query).df()
    scatter2_results = duckdb.sql(scatter2_query).df()
    # print(str(scatter_results.head()))
    
    # TODO: Extract data to populate scatter
    scatter1_data = scatter1_results.to_dict(orient="records")
    scatter2_data = scatter2_results.to_dict(orient="records")

    return {'scatter1_data': scatter1_data, 'scatter2_data': scatter2_data}

# # Update aggregated data
# @app.route("/update_aggregate", methods=['POST'])
# def update_aggregate():
#     data = request.get_json()
#     val = data.get('value')
#     key = data.get('key')

#     # Update value
#     selected[key] = val
#     x = selected['X']
#     y = selected['Y']
#     facet = selected['Facet']

#     # Update data
#     new_data = update() #get_aggregated_data(group, value, agg)

#     return jsonify({'data': new_data.to_json(), 'x_column': group, 'y_column': value})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
    