import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("OMSCS Course Ratings")
st.sidebar.markdown("# About this app")
st.sidebar.markdown("This is an open source project and you are very welcome to **contribute** with [pull requests](https://gitHub.com/rohitgeo/omscs/pulls). This app is maintained by [Rohit Singh](https://www.linkedin.com/in/rohitgeo/). Follow me on Twitter to be notified of updates.")

st.sidebar.markdown("[![Star](<https://img.shields.io/github/stars/rohitgeo/omscs.svg?logo=github&style=social>)](<https://gitHub.com/rohitgeo/omscs>) [![Follow](<https://img.shields.io/twitter/follow/geonumist?style=social>)](<https://www.twitter.com/geonumist>)")


course_list = []
w, h = 1000, 800

@st.cache()
def get_course_list():
    omscs_courses = []
    with open('courses/current_omscs_courses.csv') as f:
        omscs_courses = f.readlines()
    course_list = [c.replace('*', '').replace('"', '').split(':')[0].replace(' ', '-') for c in omscs_courses]
    return course_list
    
@st.cache()
def load_data():
    course_list = get_course_list()
    rdf = pd.read_json('courses/omscentral_reviews.json')
    cdf = pd.read_json('courses/omscentral_courses.json')

    rdf.created = pd.to_datetime(rdf.created, unit='ms')
    cdf = cdf[cdf.id.isin(course_list)].drop(columns=['deprecated', 'number'])
    df = pd.merge(rdf, cdf, left_on='course_id', right_on='id')
    gb = df.groupby(['course_id'])
    rsumdf = gb.size().to_frame(name='num_reviews')
    rsumdf = (rsumdf
        .join(gb.agg({'rating': 'mean'}))
        .join(gb.agg({'difficulty': 'mean'}))
        .join(gb.agg({'workload': 'mean'}))
        .reset_index()
    )
    rsumdf = rsumdf.merge(cdf, left_on='course_id', right_on='id')
    return rsumdf

@st.cache
def load_specdf():
    specdf = pd.read_json('courses/omscentral_specializations.json')
    specdf = specdf[specdf['program_id'] == 'compsci']
    return specdf

data_load_state = st.text('Loading data...')

course_list = get_course_list()
sumdf = load_data()
specdf = load_specdf()
data_load_state.text('')
specs = list(specdf.name)
specs.reverse()
specialization = st.selectbox(
            "Choose Specialization", ["Pick a specialization..."] + specs,
                                      help="""Students in the OMS CS program further customize their education by selecting one of our four specializations.
                                      The OMS CS degree requires 10 courses.  Students must declare one specialization, which, depending on the specialization, is 5-6 courses.
                                      The remaining 4-5 courses are “free” electives and can be any courses offered through the OMS CS program."""
        )
# List Gotchas
if specialization == 'Computational Perception & Robotics':
    st.info("Note: CS 7638 Artificial Intelligence Techniques for Robotics is required for this specialization.")
elif specialization == 'Computing Systems':
    st.info("Note: Any Core Courses in excess of the 3 course requirement may be used as Computing Systems electives")
elif specialization == 'Pick a specialization...':
    st.info("Note: Two foundational courses should be completed with a grade of B or better in the first year. A maximum of two courses may be taken with a subject code other than CS or CSE.")

if specialization == "Pick a specialization...":
    ssdf = sumdf.copy()
    fig = px.scatter(ssdf, width=w, height=h, size=ssdf['workload'],
            x='rating', y='difficulty', hover_name='name', 
               color='foundational', 
            # opacity=0.25+ssdf['num_reviews']*0.75/ssdf['num_reviews'].max(),
            hover_data=['course_id', 'workload', 'num_reviews'])
    fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="left",
            x=0.01
            ))            
    st.plotly_chart(fig, use_container_width=True)
else:
    corei = 0
    electivei = 0
    course_groups = {}
    spec_courses = eval(list(specdf[specdf.name==specialization]['requirements'])[0])
    for coursegroup in spec_courses:
        available_courses = []
        if coursegroup['type'] == 'core':
            corei = corei + 1
            key = f"Core Group {corei} (pick {coursegroup['count']})"
        elif coursegroup['type'] == 'elective':
            electivei = electivei + 1
            key = f"Elective Group {electivei} (pick {coursegroup['count']})"
        
        course_groups[key] = [c for c in coursegroup['courses'] if c in course_list]
    
    ssdf = sumdf.copy()
    ssdf['type'] = "Free Elective"
    keys = sorted(course_groups.keys())
    for k in reversed(keys): # Handle Electives before Core Courses
        ssdf.loc[ssdf['course_id'].isin(course_groups[k]), 'type'] = k

    ssdf = ssdf.sort_values('type', ascending=True)
    fig = px.scatter(ssdf, width=w, height=h, size=ssdf['workload'],
        x='rating', y='difficulty', hover_name='name', 
        color='type', 
        hover_data=['course_id', 'workload', 'num_reviews'])
    fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="left",
            x=0.01
            ))            
    st.plotly_chart(fig, use_container_width=True)
    
