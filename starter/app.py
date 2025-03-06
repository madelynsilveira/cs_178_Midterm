from flask import Flask, render_template, request
import duckdb

app = Flask(__name__)
continuous_columns = ['humidity', 'temp', 'wind']
discrete_columns = ['day']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
sorted_months = sorted(months)

@app.route('/')
def index():
    scatter_ranges_query = f'SELECT MIN(X), MAX(X), MIN(Y), MAX(Y) FROM forestfires.csv' # Retrieves the minimum and maximum X and Y coordinates
    scatter_ranges_results = duckdb.sql(scatter_ranges_query).df()

    # retrieve the scatter ranges from the series columns
    min_x = float(scatter_ranges_results['min(X)'].iloc[0])
    max_x = float(scatter_ranges_results['max(X)'].iloc[0])
    min_y = float(scatter_ranges_results['min(Y)'].iloc[0])
    max_y = float(scatter_ranges_results['max(Y)'].iloc[0])
    scatter_ranges = [min_x, max_x, min_y, max_y]

    # Write a query that retrieves the maximum number of forest fires that occurred in a single month
    max_count_query = '''
    SELECT MAX(month_count) AS max_count
    FROM (
        SELECT month, COUNT(*) AS month_count
        FROM forestfires.csv
        GROUP BY month
    )'''
    max_count_results = duckdb.sql(max_count_query).df()
    
    # Extract the maximum count from the query results
    max_count = float(max_count_results.iloc[0])

    # Write a query that retrieves the the minimum and maximum value for each slider
    filter_ranges_query = '''SELECT 
    MIN(humidity), MAX(humidity), MIN(temp), MAX(temp), MIN(wind), MAX(wind) 
    FROM forestfires.csv'''
    filter_ranges_results = duckdb.sql(filter_ranges_query).df()
    # print(str(filter_ranges_results))
    min_h = float(filter_ranges_results['min(humidity)'].iloc[0])
    max_h = float(filter_ranges_results['max(humidity)'].iloc[0])
    min_t = float(filter_ranges_results['min("temp")'].iloc[0])
    max_t = float(filter_ranges_results['max("temp")'].iloc[0])
    min_w = float(filter_ranges_results['min(wind)'].iloc[0])
    max_w = float(filter_ranges_results['max(wind)'].iloc[0])

    # Create a dictionary where each key is a filter and values are the minimum and maximum values
    filter_ranges = {'humidity': [min_h, max_h],
                     'temp': [min_t, max_t],
                     'wind': [min_w, max_w]}
    return render_template(
        'index.html', months=months, days=days,
        filter_ranges=filter_ranges, scatter_ranges=scatter_ranges, max_count=max_count
    )

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()
    # TODO: update where clause from sliders
    # continuous_predicate = ' AND '.join([f'({column} >= 0 AND {column} <= 0)' for column in continuous_columns]) 
    continuous_predicate = ' AND '.join([
        f'({column} BETWEEN {request_data[column][0]} AND {request_data[column][1]})' 
        for column in continuous_columns]) 

    # TODO: update where clause from checkboxes
    # discrete_predicate = ' AND '.join([f'{column} IN ()' for column in discrete_columns]) 
    selected_days = request_data.get('day', [])
    if selected_days:
        days_str = ", ".join([f"'{day}'" for day in selected_days])
        discrete_predicate = ' AND '.join([f'{column} IN ({days_str})' for column in discrete_columns])
    else:
        # If no days are selected, graph should be empty
        discrete_predicate = ' AND '.join([f'1=0' for column in       
                                           discrete_columns])

    # Combine where clause from sliders and checkboxes
    predicate = ' AND '.join([continuous_predicate, discrete_predicate]) 
    scatter_query = f'SELECT X, Y FROM forestfires.csv WHERE {predicate}'
    scatter_results = duckdb.sql(scatter_query).df()
    # print(str(scatter_results.head()))
    
    # TODO: Extract data to populate scatter
    # scatter_data = [] 
    scatter_data = scatter_results.to_dict(orient="records")

    # TODO: Write a query that retrieves the number of forest fires per month after filtering
    # bar_query = f'SELECT * FROM forestfires.csv' 
    bar_query = f'''
        SELECT month, COUNT(*) as count
        FROM forestfires.csv
        WHERE {predicate}
        GROUP BY month
        ORDER BY month
    '''
    bar_results = duckdb.sql(bar_query).df()
    bar_results['month'] = bar_results.index.map({i: sorted_months[i] for i in range(len(sorted_months))})

    # TODO: Extract the data that will populate the bar chart from the results
    # bar_data = [] 
    bar_data = bar_results.to_dict(orient="records")

    # TODO: Extract the maximum number of forest fires in a single month from the results
    # max_count = 0 
    max_count = float(bar_results['count'].max()) if not bar_results.empty else 0


    return {'scatter_data': scatter_data, 'bar_data': bar_data, 'max_count': max_count}

if __name__ == "__main__":
    app.run(debug=True)
    