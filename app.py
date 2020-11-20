# Import modules
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Read in the data
gss = pd.read_csv('https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv',
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"],
                 low_memory=False)

# Clean the data
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

# Text describing the dashboard
markdown_text = '''There is a well-documented gender wage gap in American society, such that men tend to make more money than
women ([source here](https://en.wikipedia.org/wiki/Gender_pay_gap)). On average, women make approximately 79% the amount that 
men do. After adjusting for work time, type of occupation, education, and experience, the wage gap is less stark at 95%. 
On average, the gender wage gap decreased steadily across the 20th century. However, research suggests that the gender wage 
gap may not fully close until 2109! This report will explore the gender wage gap from various angles by visualizing several 
factors that are important for differences in pay across individuals in general.

The General Social Survey (GSS; [source here](http://www.gss.norc.org/About-The-GSS)) includes responses 
on a variety of items, such as demographics, attitudes, and job outcomes to name a few. The survey has been conducted since 
1972 and has two primary goals:

- Conduct basic research on the development of American society
- Distribute high-quality data to social scientists and various stakeholders

The GSS has a methodological report which contains over 124 papers, in order to advance survey research methodology. For these 
reasons, the GSS is considered to be one of the best resources for scientifically examining the sociological dynamics of the 
United States of America. Here we will be using this rich dataset to explore the gender wage gap in American society.''' 

# ----------

# Group by sex and compute means on select columns
gss_tab = gss_clean.groupby('sex')[
    ['income', 'job_prestige', 'socioeconomic_index', 'education']
].mean().reset_index().round(2).rename({'education': 'years of education'}, axis=1)

# Clean up column names for display
gss_tab.columns = map(lambda x: str(x).replace('_', ' ').title(), gss_tab.columns)

# Show the table
table = ff.create_table(gss_tab)
table.show()

# ----------

# Build the scatter plot
fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', color='sex', 
                         trendline='ols', hover_data=['education', 'socioeconomic_index'],
                         labels={'job_prestige': 'Occupational Prestige', 
                                 'income': 'Annual Income',
                                 'sex': 'Sex'})

# ----------

# Build the prestige box-plot
fig_box1 = px.box(gss_clean, x='job_prestige',  color='sex', 
       labels={'job_prestige': 'Occupational Prestige'})
fig_box1.update_layout(showlegend=False)

# Build the income box-plot
fig_box2 = px.box(gss_clean, x='income',  color='sex', 
       labels={'income': 'Annual Income'})
fig_box2.update_layout(showlegend=False)

# ----------

# Select columns
gss_sub = gss_clean[['income', 'sex', 'job_prestige']]

# Specify category labels
labs = ['lowest', 'low', 'mid-low', 'mid-high', 'high', 'highest']

# Discretize job prestige
gss_sub.loc[:, 'job_grp'] = pd.cut(gss_sub.job_prestige, bins=6, labels=labs)

# Drop missing values
gss_sub.dropna(inplace=True)

# Build the facet-grid box plot
fig_facet = px.box(gss_sub, x='income',  color='sex', facet_col='job_grp', facet_col_wrap=2,
       labels={'income': 'Annual Income'}, 
       color_discrete_map = {'male':'green', 'female':'purple'},
       category_orders={'job_grp': labs})
fig_facet.for_each_annotation(lambda a: a.update(text=a.text.replace('job_grp=', '')))

# ----------

# Specify extra credit columns
x_cols = ['satjob', 'relationship', 'male_breadwinner', 
          'men_bettersuited', 'child_suffer', 'men_overwork']
grp_cols = ['sex', 'region', 'education']

# Specify background and text colors
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Update the layout
def update_layout(fig):
    return fig.update_layout(plot_bgcolor=colors['background'],
                             paper_bgcolor=colors['background'],
                             font_color=colors['text'])
[update_layout(i) for i in [fig_scatter, fig_box1, fig_box2, fig_facet]]

# Initialize the dashboard
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Build the dashboard
app.layout = html.Div(
    style={'backgroundColor': colors['background'], 
           'textAlign': 'center',
           'color': colors['text']},
    children=[
        
        html.Div([
            
            html.H1('Exploration of the Gender Wage Gap Using the General Social Survey (GSS)'),
            dcc.Markdown(children = markdown_text),
         ], style={'textAlign': 'left'}),
        
        html.H2('Summary statistics across the sexes'),
        dcc.Graph(figure=table),
        
        html.H2('Income and prestige are positively correlated'),
        dcc.Graph(figure=fig_scatter),
        
        html.Div([
            
            html.H2('Job outcome distributions'),
            dcc.Graph(figure=fig_box1)
         ], style = {'width':'50%', 'float':'left'}),
        
        html.Div([
            
            html.H2('red: female; blue: male'),
            dcc.Graph(figure=fig_box2)
         ], style = {'width':'50%', 'float':'right'}),
        
        html.H2('Income stratified by grouped levels of job prestige'),
        dcc.Graph(figure=fig_facet),
        
        html.H3('Pick the variables you would like to view!'), 
        dcc.Graph(id='graph'),
            
        html.H3('Select the x-axis'),   
        dcc.Dropdown(id='x-axis',
        options=[{'label': i, 'value': i} for i in x_cols],
        value='male_breadwinner'),
            
        html.H3('Select the grouping variable'),       
        dcc.Dropdown(id='group',
        options=[{'label': i, 'value': i} for i in grp_cols],
        value='sex')
        
    ]
)

@app.callback(Output(component_id='graph',component_property='figure'), 
             [Input(component_id='x-axis',component_property='value'),
              Input(component_id='group',component_property='value')])

def make_figure(x, grp):
    # Get counts for variable by grouping
    gss_bar = gss_clean[[grp, x]].value_counts().reset_index().rename(
        {0: 'Count'}, axis=1)
        
    return update_layout(px.bar(gss_bar, x=x, y='Count', color=grp, barmode='group'))

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True)
