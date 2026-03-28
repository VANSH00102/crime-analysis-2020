"""
app.py – Indian Crime Data Analysis 2020
Flask backend server with REST API endpoints.
Run with: python app.py
"""

from flask import Flask, jsonify, send_file, request, make_response
import pandas as pd
import os
import json

from analysis import (
    load_and_preprocess,
    get_stats,
    run_all,
    OUTPUT_DIR,
    DATA_PATH,
)

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)

# ─── Manual CORS (no flask-cors needed) ──────────────────────────────────────
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin']  = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp, 200

# ─── Helper ───────────────────────────────────────────────────────────────────
def error_response(msg, code=500):
    return jsonify({'error': msg, 'status': 'failed'}), code


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint."""
    return jsonify({
        'message': 'Indian Crime Data Analysis API 2020',
        'status':  'running',
        'version': '1.0',
        'endpoints': ['/data', '/stats', '/visualizations', '/run-analysis', '/image/<filename>']
    })


# ── 1. /data ──────────────────────────────────────────────────────────────────
@app.route('/data', methods=['GET'])
def get_data():
    """
    Returns the cleaned crime CSV as JSON.
    Optional query params:
      ?state=Maharashtra  → filter by state
      ?crime=Theft        → filter by crime type
      ?limit=100          → limit rows (default 500)
    """
    try:
        df    = load_and_preprocess()
        state = request.args.get('state')
        crime = request.args.get('crime')
        limit = int(request.args.get('limit', 500))

        if state:
            df = df[df['State_UT'].str.lower() == state.lower()]
        if crime:
            df = df[df['Crime_Type'].str.lower() == crime.lower()]

        df = df.head(limit)

        return jsonify({
            'status':      'success',
            'total_rows':  len(df),
            'columns':     df.columns.tolist(),
            'data':        df.to_dict(orient='records'),
            'states':      sorted(load_and_preprocess()['State_UT'].unique().tolist()),
            'crime_types': sorted(load_and_preprocess()['Crime_Type'].unique().tolist()),
        })
    except Exception as e:
        return error_response(str(e))


# ── 2. /stats ─────────────────────────────────────────────────────────────────
@app.route('/stats', methods=['GET'])
def get_statistics():
    """
    Returns key crime statistics and insights.
    """
    try:
        df    = load_and_preprocess()
        stats = get_stats(df)
        return jsonify({'status': 'success', **stats})
    except Exception as e:
        return error_response(str(e))


# ── 3. /visualizations ────────────────────────────────────────────────────────
@app.route('/visualizations', methods=['GET'])
def get_visualizations():
    """
    Returns list of available visualization images with metadata.
    """
    try:
        images = []
        meta = {
            'top_states_bar.png':       {'title': 'Top 10 States by Crime Count',
                                          'description': 'Horizontal bar chart showing the 10 states with the highest number of registered cases in 2020.'},
            'crime_type_pie.png':        {'title': 'Crime Type Distribution',
                                          'description': 'Pie chart illustrating the proportion of each crime type across India.'},
            'top5_grouped_bar.png':      {'title': 'Major Crimes – Top 5 States',
                                          'description': 'Grouped bar chart comparing five major crime types across the top 5 states.'},
            'crime_rate_heatmap.png':    {'title': 'Crime Rate Heatmap',
                                          'description': 'Heatmap showing crime rate (per lakh population) across all states and crime types.'},
            'conviction_rate_bar.png':   {'title': 'Conviction Rate by Crime Type',
                                          'description': 'Bar chart displaying the percentage of registered cases that resulted in conviction, per crime category.'},
            'state_crime_rate.png':      {'title': 'State-wise Crime Rate',
                                          'description': 'Average crime rate per lakh population for the top 15 states.'},
            'arrests_vs_cases.png':      {'title': 'Arrests vs Cases Scatter',
                                          'description': 'Scatter plot correlating persons arrested with cases registered for each state, with a trend line.'},
            'crime_composition.png':     {'title': 'Crime Composition by State',
                                          'description': 'Stacked bar chart showing the percentage breakdown of crime types for the top 8 states.'},
        }

        for fname in os.listdir(OUTPUT_DIR):
            if fname.endswith('.png'):
                info = meta.get(fname, {'title': fname, 'description': ''})
                images.append({
                    'filename':    fname,
                    'url':         f'/image/{fname}',
                    'title':       info['title'],
                    'description': info['description'],
                })

        images.sort(key=lambda x: list(meta.keys()).index(x['filename'])
                    if x['filename'] in meta else 99)

        return jsonify({'status': 'success', 'count': len(images), 'images': images})
    except Exception as e:
        return error_response(str(e))


# ── 4. /run-analysis ──────────────────────────────────────────────────────────
@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    """
    Triggers the full analysis pipeline.
    Regenerates all visualizations and returns stats.
    """
    try:
        result = run_all()
        return jsonify({
            'status':  'success',
            'message': 'Analysis completed successfully.',
            'stats':   result['stats'],
            'images_generated': result['images'],
        })
    except Exception as e:
        return error_response(str(e))


# ── 5. /image/<filename> ──────────────────────────────────────────────────────
@app.route('/image/<filename>', methods=['GET'])
def serve_image(filename):
    """
    Serves a visualization image from the outputs folder.
    """
    try:
        # Security: only allow .png files, no path traversal
        if not filename.endswith('.png') or '/' in filename or '..' in filename:
            return error_response('Invalid filename.', 400)

        path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(path):
            return error_response(f'Image "{filename}" not found. Run /run-analysis first.', 404)

        return send_file(path, mimetype='image/png')
    except Exception as e:
        return error_response(str(e))


# ── Extra: /states ─────────────────────────────────────────────────────────────
@app.route('/states', methods=['GET'])
def get_states():
    """Returns list of all states in the dataset."""
    try:
        df     = load_and_preprocess()
        states = sorted(df['State_UT'].unique().tolist())
        return jsonify({'status': 'success', 'states': states, 'count': len(states)})
    except Exception as e:
        return error_response(str(e))


# ── Extra: /state/<name> ───────────────────────────────────────────────────────
@app.route('/state/<name>', methods=['GET'])
def get_state_data(name):
    """Returns analysis data for a specific state."""
    try:
        df       = load_and_preprocess()
        state_df = df[df['State_UT'].str.lower() == name.lower()]

        if state_df.empty:
            return error_response(f'State "{name}" not found.', 404)

        stats = {
            'state':               state_df['State_UT'].iloc[0],
            'total_crimes':        int(state_df['Cases_Registered'].sum()),
            'most_common_crime':   state_df.loc[state_df['Cases_Registered'].idxmax(), 'Crime_Type'],
            'avg_conviction_rate': round(state_df['Conviction_Rate'].mean(), 2),
            'crime_breakdown':     state_df[['Crime_Type', 'Cases_Registered', 'Crime_Rate']]
                                           .sort_values('Cases_Registered', ascending=False)
                                           .to_dict(orient='records'),
        }
        return jsonify({'status': 'success', **stats})
    except Exception as e:
        return error_response(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  Indian Crime Data Analysis API – 2020")
    print("  Backend server starting on http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, host='0.0.0.0', port=5001)
