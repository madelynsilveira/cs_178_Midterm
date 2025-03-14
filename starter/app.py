from flask import Flask, render_template, request
import duckdb
import re
import pandas as pd
import numpy as np

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
  "ExtracurricularActivities": ['Yes', 'No'],
  "PlacementTraining": ['Yes', 'No']
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
    filter_ranges = {'internships': [min_internships, max_internships],
                     'projects': [min_projects, max_projects],
                     'aptitudetestscore': [min_aptitude, max_aptitude],
                     'softskillsrating': [min_softskillsrating, max_softskillsrating],
                     'ssc_marks': [min_ssc, max_ssc],
                     'hsc_marks': [min_hsc, max_hsc]}

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

    # keep this in for now to avoid potential error 
    if x == 'Workshops':
        x = 'Workshops/Certifications'
    if y == 'Workshops':
        y = 'Workshops/Certifications'
        
    # Update where clause from sliders
    # continuous_predicate = ' AND '.join([f'({column} >= 0 AND {column} <= 0)' for column in continuous_columns]) 
    continuous_predicate = ' AND '.join([
        f'({column} BETWEEN {request_data[column][0]} AND {request_data[column][1]})' 
        for column in continuous_columns]) 

    # Update where clause from radio buttons
    activities_list = request_data.get('ExtracurricularActivities')
    training_list = request_data.get('PlacementTraining')
    activities_sql_list = ", ".join([f"{item}" for item in activities_list])
    training_sql_list = ", ".join([f"{item}" for item in training_list])
    
    discrete_predicate = f'ExtracurricularActivities IN ({activities_sql_list}) AND PlacementTraining IN ({training_sql_list})'

    # Combine where clause from sliders and checkboxes
    facetTrue = facet_options[facet][0]
    facetFalse = facet_options[facet][1]
    
    predicate = ' AND '.join([continuous_predicate, discrete_predicate]) 
    
    scatter1_query = f'SELECT "{x}" AS "x", "{y}" AS "y" FROM placementdata.csv WHERE {facet} = \'{facetTrue}\' AND {predicate} '
    scatter2_query = f'SELECT "{x}" AS "x", "{y}" AS "y" FROM placementdata.csv WHERE {facet} = \'{facetFalse}\' AND {predicate}'
    
    scatter1_results = duckdb.sql(scatter1_query).df()
    scatter2_results = duckdb.sql(scatter2_query).df()
    
    # Extract data to populate scatter
    scatter1_data = scatter1_results.to_dict(orient="records")
    scatter2_data = scatter2_results.to_dict(orient="records")

    # Format labels
    facet = re.sub(r'([a-z])([A-Z])', r'\1 \2', facet)
    facetTrue = re.sub(r'([a-z])([A-Z])', r'\1 \2', facetTrue)
    facetFalse = re.sub(r'([a-z])([A-Z])', r'\1 \2', facetFalse)
    x = re.sub(r'([a-z])([A-Z])', r'\1 \2', x).replace('_', ' ')
    y = re.sub(r'([a-z])([A-Z])', r'\1 \2', y).replace('_', ' ')

    # Compute stats for each graph
    slope1, intercept1 = get_line_metrics(scatter1_results)
    slope2, intercept2 = get_line_metrics(scatter2_results)
    stats1 = {
      'total': len(scatter1_results),
      'x_avg': scatter1_results['x'].mean(),
      'y_avg': scatter1_results['y'].mean(),
      'slope': slope1,
      'intercept': intercept1
    }
    stats2 = {
      'total': len(scatter2_results),
      'x_avg': scatter2_results['x'].mean(),
      'y_avg': scatter2_results['y'].mean(),
      'slope': slope2,
      'intercept': intercept2
    }

    return {'scatter1_data': scatter1_data, 'scatter2_data': scatter2_data,
      'scatter1_label': facet + ": " + facetTrue, 'scatter2_label': facet + ": " + facetFalse,
       'x_label': x, 'y_label': y, 'scatter1_stats': stats1, 'scatter2_stats': stats2}


# functions to get regression line metrics
def get_line_metrics(scatter_data):
  coefficients = np.polyfit(scatter_data['x'], scatter_data['y'], 1)
  return coefficients[0], coefficients[1]


if __name__ == "__main__":
    app.run(debug=True, port=3000)
    