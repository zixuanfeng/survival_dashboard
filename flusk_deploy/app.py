import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import plotly.graph_objs as go
import plotly.io as pio
from flask import Flask, render_template
import statsmodels.api as sm
import numpy as np
from dash.dependencies import Input, Output
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
from datetime import datetime, timedelta
from dash import Dash
from dash import Dash, dcc, html
from lifelines import CoxPHFitter
from flask import Flask, render_template, request, jsonify  # Import jsonify

app = Flask(__name__)

surv_data_flutter = pd.read_csv("~/Desktop/combined.csv")
surv_data_flutter['recent_day'] = pd.to_datetime(surv_data_flutter['recent_day'])
months_years = surv_data_flutter['recent_day'].dt.to_period('M').unique().tolist()


def df_to_html_list(df):
    # Generate a list in HTML format without the title
    html_list = '<ul class="Box" style="max-width: 100%; margin-bottom: 10px; margin-top: 30px">'
    
    for index, row in df.iterrows():
        # Convert login_name to a clickable link with a custom data-login attribute.
        login_link = f'<a href="#" class="login-link" data-login="{row["login_name"]}">{row["login_name"]}</a>'
        
        html_list += f'''
        <li class="Box-row d-flex flex-items-center" style="height: 15px; font-size: 1em; padding: 5px 10px;">  <!-- Reduced height, padding, and font size -->
            <div class="d-flex flex-auto flex-justify-between flex-column flex-sm-row flex-items-baseline" style="display: flex; justify-content: center; align-items: center;">
                <span style="display: flex; align-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="20px" height="40px">
                    </svg>
                    <span class="contributor-name" data-contributor-index="{index}">&nbsp; {login_link} (Risk %: {row['hazard_percentage']:.2f}%)</span>
                </span>
            </div>
        </li>
        <br>
        '''
    
    html_list += '</ul>'
    return html_list



# def df_to_html_list_inactive(df):
#     # Generate a list in HTML format
#     html_list = '<ul class="CustomBox">'
#     for index, row in df.iterrows():
#         login_link = f'<a href="#" class="login-link" data-login="{row["Login"]}">{row["Login"]}</a>'

#         html_list += f'''
#         <li class="CustomBoxRow d-flex flex-items-center" style="height: 80px; border-bottom: 1px solid #e1e4e8;">
#             <div class="d-flex flex-auto flex-justify-between flex-column flex-sm-row flex-items-baseline">
#                 <span style="display: flex; align-items: center;">
#                     <span class="contributor-name" data-contributor-index="{index}">&nbsp; {login_link} (Gender: {row['Gender']}) (Region: {row['western']}) (Newcomer: {row['newcomer']}) (Affiliated: {row['paid']}) (Recent active day: {row['recent_day']}) (Number commits: {row['commits']}) (Number PR: {row['PRs']}) (Number PR comments: {row['PR_commenter']})</span>
#                 </span>
#             </div>
#         </li>
#         '''
#     html_list += '</ul>'
#     return html_list


def df_to_html_list_inactive(df):
    # Start the table with a header row
    headers = [
        "Name", "Gender", "Region", "Newcomer", "Affiliated", "Recent Active Day"
    ]

    html_table = '<table class="CustomBox">'
    
    # Header row
    html_table += '<thead><tr class="CustomBoxHeader">'
    for header in headers:
        html_table += f'<th class="header-item">{header}</th>'
    html_table += '</tr></thead>'

    # Data rows
    html_table += '<tbody>'
    for index, row in df.iterrows():
        login_link = f'<a href="#" class="login-link" data-login="{row["Login"]}">{row["Login"]}</a>'
        data_items = [
            login_link, row['Gender'], row['western'], row['newcomer'],
            row['paid'], row['recent_day']
        ]
        html_table += '<tr class="CustomBoxRow">'
        for item in data_items:
            html_table += f'<td class="data-item">{item}</td>'
        html_table += '</tr>'
    html_table += '</tbody>'

    html_table += '</table>'
    return html_table


# ##############################################------Inactive table-----#########################################################


@app.route('/', methods=['GET', 'POST'])
def index():
    def compute_date_thresholds():
        today = datetime.today()
        return today - timedelta(days=365), today - timedelta(days=180)

    def get_filters_from_request():
        return {
            "gender": request.form.get('gender', "all"),
            "newcomer": request.form.get('newcomer', "all"),
            "region": request.form.get('region', "all"),
            "paid": request.form.get('paid', "all")
        }

    def build_mask(df, filters, one_year_ago, one_eighty_days_ago):
        base_mask = (df['recent_day'] > one_year_ago) & (df['recent_day'] < one_eighty_days_ago)
        field_to_column_map = {
            "gender": "Gender",
            "newcomer": "newcomer",
            "region": "western",
            "paid": "paid"
        }
        for field, column in field_to_column_map.items():
            value = filters[field]
            if value != "all":
                base_mask &= (df[column] == value)
        return base_mask

    def sort_and_trim_dataframe(df):
        sort_by_default = "recent_day"
        sort_by = request.form.get('sort_by', sort_by_default)
        order = False if sort_by == "recent_day" else True
        return df.sort_values(by=sort_by, ascending=False).head(20)

    # Main logic
    surv_data_flutter['recent_day'] = pd.to_datetime(surv_data_flutter['recent_day'])
    one_year_ago, one_eighty_days_ago = compute_date_thresholds()

    filters = get_filters_from_request()
    mask = build_mask(surv_data_flutter, filters, one_year_ago, one_eighty_days_ago)

    sorted_df = sort_and_trim_dataframe(surv_data_flutter[mask])
    inactive_html_table = df_to_html_list_inactive(sorted_df)

    return render_template(
        'plot.html',
        months_years=months_years,
        inactive_html_table_html=inactive_html_table,
        gender_selected=filters['gender'],
        sort_by=request.form.get('sort_by', "recent_day"),
        newcomer_selected=filters['newcomer'],
        region_selected=filters['region'],
        paid_selected=filters['paid'],
        columns=surv_data_flutter.columns
    )




##############################################------Survival analysis------#########################################################

@app.route('/update_data', methods=['POST'])

##############################################------Time selector------#########################################################

def update_data():
    selected_time_range = request.form.get('time_range')
    print("Selected Time Range:", selected_time_range)
    # Defaults
    xaxis_range = [0, None]
    end_date = pd.Timestamp.now()  # Use current date as the end date


    if selected_time_range == 'recent-year':
        start_date = pd.Timestamp.now() - pd.DateOffset(days=365)
        xaxis_range = [0, 365+365]
    elif selected_time_range == 'recent-three-years':
        start_date = pd.Timestamp.now() - pd.DateOffset(days=1095)
        xaxis_range = [0, 1095+365]
    elif selected_time_range == 'recent-five-years':
        start_date = pd.Timestamp.now() - pd.DateOffset(days=1825)
        xaxis_range = [0, 1825+365]
    else:
        start_date = surv_data_flutter['recent_day'].min()

    filtered_data = surv_data_flutter[
        (surv_data_flutter['recent_day'] >= start_date) & (surv_data_flutter['recent_day'] <= end_date)
    ]
    



##############################################------Overall data------#########################################################

    cutoff_date = datetime.now() - timedelta(days=365)
    active_contributors_index = filtered_data[filtered_data['recent_day'] > cutoff_date]['Login'].nunique()

    #################metric calculation
    total_contributor = filtered_data['Login'].nunique()
    left_contributors = total_contributor - active_contributors_index
    average_tenure = int(filtered_data['survival_days'].mean())
    turnover_rate = round((left_contributors / total_contributor) * 100, 2) if total_contributor != 0 else 0
    # one_year_ago_contributors = filtered_data[filtered_data['recent_day'] < cutoff_date]['Login'].nunique()
    # one_year_ago_left_contributors = filtered_data[(filtered_data['recent_day'] < cutoff_date) & (filtered_data['recent_day'] >= cutoff_date - timedelta(days=365))]['Login'].nunique()
    # yearly_turnover_rate = round((one_year_ago_left_contributors / one_year_ago_contributors) * 100, 2) if one_year_ago_contributors != 0 else 0

    # Newcomers
    newcomer_cutoff_date = datetime.now() - timedelta(days=60)
    filtered_data['is_newcomer'] = filtered_data['recent_day'] > newcomer_cutoff_date
    newcomers = filtered_data['is_newcomer'].sum()

    # Gender ratio
    male_contributors = filtered_data[filtered_data['Gender'] == 'male'].shape[0]
    female_contributors = filtered_data[filtered_data['Gender'] == 'female'].shape[0]
    gender_ratio = f"{male_contributors}:{female_contributors}"

    # Region ratio
    western_contributors = filtered_data[filtered_data['western'] == 'Western'].shape[0]
    non_western_contributors = filtered_data[filtered_data['western'] != 'Western'].shape[0]
    region_ratio = f"{western_contributors}:{non_western_contributors}"

    # Paid ratio
    paid_contributors = filtered_data[filtered_data['paid'] == 'yes'].shape[0]
    non_paid_contributors = filtered_data[filtered_data['paid'] == 'no'].shape[0]
    paid_ratio = f"{paid_contributors}:{non_paid_contributors}"

    # Overview plot ratios
    total_gender = male_contributors + female_contributors
    gender_ratio_percentage = round(male_contributors / total_gender * 100) if total_gender != 0 else 0

    total_region = western_contributors + non_western_contributors
    region_ratio_percentage = round(western_contributors / total_region * 100) if total_region != 0 else 0

    total_paid = paid_contributors + non_paid_contributors
    paid_ratio_percentage = round(paid_contributors / total_paid * 100) if total_paid != 0 else 0   


#################plot
    survival_days = filtered_data['survival_days']
    survival = filtered_data['survival']

    # Create Kaplan-Meier estimator for overall survival
    kmf = KaplanMeierFitter()
    kmf.fit(survival_days, survival)

    # Create Plotly trace for survival curve
    trace = go.Scatter(
        x=kmf.timeline, 
        y=kmf.survival_function_.iloc[:, 0],
        mode='lines', 
        name='Overall',
        line=dict(width=3)  # Setting the line width to 3; adjust as needed
    )

    # Create the layout for the survival plot
    layout = go.Layout(
        xaxis=dict(title='Days', range=xaxis_range),
        yaxis=dict(title='Survival probability'),
        legend=dict(x=0, y=1, yanchor='bottom'),
        autosize=True, 
        width=None,  # Allow the plot to fill its container width-wise
        height=240,
        margin=dict(l=50, r=50, b=50, t=50),  # Adjust these values as needed
        plot_bgcolor='rgba(225, 228, 232, 0.5)'   # Setting the plot background color

    )

    # Create the survival plot
    fig_total = go.Figure(data=[trace], layout=layout)
    
    
    plotly_fig_total = fig_total.to_json()



##############################################------DEI lens------#########################################################


################# plots

    def create_km_plot(filtered_data, column_name, title, x_title, y_title):
        # Separate survival days and survival status by a specific column
        unique_values = filtered_data[column_name].unique()

        # Initialize empty lists for survival data of each category
        survival_days = []
        survival = []

        for value in unique_values:
            survival_days.append(filtered_data[filtered_data[column_name] == value]['survival_days'])
            survival.append(filtered_data[filtered_data[column_name] == value]['survival'])

        # Create Kaplan-Meier estimator for each category
        kmfs = []
        for i in range(len(unique_values)):
            kmf = KaplanMeierFitter()
            kmf.fit(survival_days[i], survival[i])
            kmfs.append(kmf)

        # Create Plotly traces for each category's survival curve
        traces = []
        for i, value in enumerate(unique_values):
            trace = go.Scatter(
                x=kmfs[i].timeline,
                y=kmfs[i].survival_function_.iloc[:, 0],
                mode='lines',
                name=str(value)
            )
            traces.append(trace)

        min_timeline = min([min(kmf.timeline) for kmf in kmfs])
        max_timeline = max([max(kmf.timeline) for kmf in kmfs])

        # Create the layout for the plot
        layout = go.Layout(
            xaxis=dict(title='Days', range=xaxis_range),
            yaxis=dict(title=y_title, range=[0, None], fixedrange=True),  # Set fixedrange=True to lock the y-axis range
            legend=dict(x=0, y=1, yanchor='bottom'),
            autosize=True,
            width=None,
            height=240,
            margin=dict(l=50, r=50, b=50, t=50),
            plot_bgcolor='rgba(225, 228, 232, 0.5)'
        )

        # Create the plot
        fig = go.Figure(data=traces, layout=layout)

        # Perform log-rank tests and display p-values
        p_values = []
        for i in range(len(unique_values)):
            for j in range(i + 1, len(unique_values)):
                result = logrank_test(survival_days[i], survival_days[j], survival[i], survival[j])
                p_values.append(result.p_value)


        # Calculate a single p-value for the comparison
        p_value = np.min(p_values)  # Use the minimum p-value among all comparisons

        fig.add_annotation(
            x=0,  # Adjust the x-coordinate for left bottom corner
            y=0,  # Adjust the y-coordinate for left bottom corner
            xref="paper",  # Specify the x-coordinate reference as "paper" for relative positioning
            yref="paper",  # Specify the y-coordinate reference as "paper" for relative positioning
            text=f"p-value: {p_value:.2f}",
            showarrow=False,
            font=dict(size=12)
        )

        return fig.to_json()

    plotly_fig_gender = create_km_plot(filtered_data, 'Gender', 'Gender Survival Plot', 'Days', 'Survival probability (Gender)')
    plotly_fig_paid = create_km_plot(filtered_data, 'paid', 'Compensation Survival Plot', 'Days', 'Survival probability (Paid)')
    plotly_fig_western = create_km_plot(filtered_data, 'western', 'Region Survival Plot', 'Days', 'Survival probability (Region)')

################# metric calculation


    def calculate_metrics(group):
        active_contributors = group[group['recent_day'] > cutoff_date]['Login'].nunique()
        newcomers = group[group['recent_day'] > newcomer_cutoff_date]['is_newcomer'].sum()
        total_contributors = group['Login'].nunique()
        contributors_left = total_contributors - active_contributors
        average_tenure = group['survival_days'].mean()

        turnover_rate = contributors_left / total_contributors * 100 if total_contributors != 0 else 0
        yearly_turnover_rate = turnover_rate / average_tenure * 365 * 100 if average_tenure > 0 else 0

        metrics = {
            'active_contributors': int(active_contributors),
            'newcomers': int(newcomers),
            'contributors_left': int(contributors_left),
            'average_tenure': float(average_tenure),
            'turnover_rate': float(turnover_rate),
            'total_contributor': float(total_contributors)
        }

        return metrics
    

    newcomer_cutoff_date = datetime.now() - timedelta(days=60)
    filtered_data['is_newcomer'] = filtered_data['recent_day'] > newcomer_cutoff_date
    newcomers = filtered_data['is_newcomer'].sum()

    grouped_gender = filtered_data.groupby('Gender')
    grouped_paid = filtered_data.groupby('paid')
    grouped_western = filtered_data.groupby('western')
    
    metrics_men = calculate_metrics(grouped_gender.get_group('male'))
    metrics_women = calculate_metrics(grouped_gender.get_group('female'))
    metrics_yes = calculate_metrics(grouped_paid.get_group('yes'))
    metrics_no = calculate_metrics(grouped_paid.get_group('no'))
    metrics_western = calculate_metrics(grouped_western.get_group('Western'))
    metrics_non_western = calculate_metrics(grouped_western.get_group('Asia&Africa&Latin Am'))


##############################################------Survival prediction------#########################################################


    selected_vars = request.form.getlist('variables')
    formula = ' + '.join(selected_vars) if selected_vars else "commits + PRs + PR_comment_received  + first_response + in_degree_centrality "

    # Initialize and fit CoxPH model
    cph = CoxPHFitter()
    cph.fit(filtered_data, duration_col='survival_days', event_col='survival', formula=formula)

    # Calculate survival function, partial hazards, hazard ratios, and c-index
    survival_function = cph.predict_survival_function(filtered_data)
    partial_hazards = cph.predict_partial_hazard(filtered_data)
    hazard_ratios = np.exp(partial_hazards)
    hazard_percentages = (hazard_ratios - 1) * 100  # Convert to percentages

    c_index = cph.score(filtered_data, scoring_method='concordance_index')

    # Create a data frame with contributor information
    contributor_table = pd.DataFrame({
        'login_name': filtered_data['Login'],
        'western': filtered_data['western'],
        'paid': filtered_data['paid'],
        'Gender': filtered_data['Gender'],
        'newcomer': filtered_data['newcomer'],
        'hazard_percentage': hazard_percentages.round(2)  # Add the hazard percentage column
    })

    # Create details column
    contributor_table['details'] = (
        'Commits: ' + filtered_data['commits'].astype(str) +
        ', PRs: ' + filtered_data['PRs'].astype(str) +
        ', PR Comments: ' + filtered_data['PR_comment_received'].astype(str)
    )

    # Sort the contributor_table by hazard ratios in descending order
    contributor_table = contributor_table.sort_values(by='hazard_percentage', ascending=False)

    # Extract top contributors by gender, western, and paid categories
    top_5_male_contributors = contributor_table[contributor_table['Gender'] == 'male'].head(5)
    top_5_female_contributors = contributor_table[contributor_table['Gender'] == 'female'].head(5)

    top_5_no_western_contributors = contributor_table[contributor_table['western'] == 'Asia&Africa&Latin Am'].head(5)
    top_5_western_contributors = contributor_table[contributor_table['western'] == 'Western'].head(5)

    top_5_unpaid_contributors = contributor_table[contributor_table['paid'] == 'no'].head(5)
    top_5_paid_contributors = contributor_table[contributor_table['paid'] == 'yes'].head(5)

    # Create HTML representations of top contributors
    top_5_male_contributors_html = df_to_html_list(top_5_male_contributors)
    top_5_female_contributors_html = df_to_html_list(top_5_female_contributors)
    top_5_no_western_contributors_html = df_to_html_list(top_5_no_western_contributors)
    top_5_western_contributors_html = df_to_html_list(top_5_western_contributors)
    top_5_unpaid_contributors_html = df_to_html_list(top_5_unpaid_contributors)
    top_5_paid_contributors_html = df_to_html_list(top_5_paid_contributors)

    # Create login tables for each unique login
    login_tables = {}
    for login in filtered_data['Login'].unique():
        sub_df = filtered_data[filtered_data['Login'] == login]
        table_html = sub_df.to_html(classes='login-table', border=0, index=False)
        styled_table = f'<table class="login-table">{table_html}</table>'
        login_tables[login] = styled_table


    metrics = {
        # Overall
        'active_contributors_index': int(active_contributors_index),
        'total_contributor': int(total_contributor),
        'left_contributors': int(left_contributors), 
        'average_tenure': int(average_tenure), 
        'turnover_rate': int(turnover_rate), 
        # 'yearly_turnover_rate': int(yearly_turnover_rate), 
        'newcomers': int(newcomers), 
        'gender_ratio': gender_ratio,
        'region_ratio': region_ratio, 
        'paid_ratio': paid_ratio, 
        'gender_ratio_percentage': gender_ratio_percentage, 
        'region_ratio_percentage': region_ratio_percentage, 
        'paid_ratio_percentage': paid_ratio_percentage,
        'plot_total':plotly_fig_total,

        # DEI attribute metrics

        'plot_gender':plotly_fig_gender,
        'plot_paid':plotly_fig_paid,
        'plot_western':plotly_fig_western,

        # gender
        'active_contributors_indx_men': int(metrics_men['active_contributors']),
        'left_contributors_men': int(metrics_men['contributors_left']),
        'average_tenure_men':int(metrics_men['average_tenure']),
        'turnover_rate_men': int(metrics_men['turnover_rate']),
        'total_contributor_men': int(metrics_men['total_contributor']),
        'newcomers_men': int(metrics_men['newcomers']),

        'active_contributors_index_women': int(metrics_women['active_contributors']),
        'left_contributors_women': int(metrics_women['contributors_left']),
        'average_tenure_women': int(metrics_women['average_tenure']),
        'turnover_rate_women': int(metrics_women['turnover_rate']),
        'total_contributor_women': int(metrics_women['total_contributor']),
        'newcomers_women': int(metrics_women['newcomers']),

        # paid
        'active_contributors_paid_yes': int(metrics_yes['active_contributors']),
        'left_contributors_paid_yes': int(metrics_yes['contributors_left']),
        'average_tenure_paid_yes': int(metrics_yes['average_tenure']),
        'turnover_rate_paid_yes': int(metrics_yes['turnover_rate']),
        'total_contributor_paid_yes': int(metrics_yes['total_contributor']),
        'newcomers_paid_yes': int(metrics_yes['newcomers']),

        'active_contributors_paid_no': int(metrics_no['active_contributors']),
        'left_contributors_paid_no': int(metrics_no['contributors_left']),
        'average_tenure_paid_no': int(metrics_no['average_tenure']),
        'turnover_rate_paid_no': int(metrics_no['turnover_rate']),
        'total_contributor_paid_no': int(metrics_no['total_contributor']),
        'newcomers_paid_no': int(metrics_no['newcomers']),

        #region
        'active_contributors_western': int(metrics_western['active_contributors']),
        'left_contributors_western': int(metrics_western['contributors_left']),
        'average_tenure_western': int(metrics_western['average_tenure']),
        'turnover_rate_western': int(metrics_western['turnover_rate']),
        'total_contributor_western': int(metrics_western['total_contributor']),
        'newcomers_western': int(metrics_western['newcomers']),

        'active_contributors_non_western': int(metrics_non_western['active_contributors']),
        'left_contributors_non_western': int(metrics_non_western['contributors_left']),
        'average_tenure_non_western': int(metrics_non_western['average_tenure']),
        'turnover_rate_non_western': int(metrics_non_western['turnover_rate']),
        'total_contributor_non_western': int(metrics_non_western['total_contributor']),
        'newcomers_non_western': int(metrics_non_western['newcomers']),

        # prediction

        'top_5_female_contributors_html':top_5_female_contributors_html,
        'top_5_male_contributors_html':top_5_male_contributors_html,
        'top_5_western_contributors_html':top_5_western_contributors_html,
        'top_5_no_western_contributors_html':top_5_no_western_contributors_html,
        'top_5_paid_contributors_html':top_5_paid_contributors_html,
        'top_5_unpaid_contributors_html':top_5_unpaid_contributors_html, 
        'login_tables': login_tables,
        'c_index': c_index

    }

    return jsonify(metrics)



if __name__ == '__main__':
    app.run()