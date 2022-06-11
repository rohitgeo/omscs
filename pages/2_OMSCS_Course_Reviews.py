import streamlit as st
import pandas as pd
import plotly.express as px

w, h = 1000, 800

st.set_page_config(layout="wide")

st.markdown("# OMSCS Course Reviews")
# st.sidebar.markdown("# Course Reviews")
# st.sidebar.markdown("[![Star](<https://img.shields.io/github/stars/rohitgeo/geonotebooks.svg?logo=github&style=social>)](<https://gitHub.com/rohitgeo/geonotebooks>) [![Follow](<https://img.shields.io/twitter/follow/geonumist?style=social>)](<https://www.twitter.com/geonumist>)")



@st.cache()
def get_course_list():
    omscs_courses = []
    with open('courses/current_omscs_courses.csv') as f:
        omscs_courses = f.readlines()
    course_list = [c.replace('*', '').replace('"', '').split(':')[0].replace(' ', '-') for c in omscs_courses]
    return course_list

@st.cache()
def get_course_df():
    course_list = get_course_list()
    cdf = pd.read_json('courses/omscentral_courses.json')
    cdf = cdf[cdf.id.isin(course_list)].drop(columns=['deprecated', 'number'])
    return cdf

@st.cache()
def load_reviews():
    rdf = pd.read_json('courses/omscentral_reviews.json')
    cdf = get_course_df()
    rdf.created = pd.to_datetime(rdf.created, unit='ms')
    df = pd.merge(rdf, cdf, left_on='course_id', right_on='id')
    return df

def get_semester(semester_id):
    year, sem = semester_id.split('-')
    if sem == '1':
        sem = 'Spring'
    elif sem == '2':
        sem = 'Summer'
    elif sem == '3':
        sem = 'Fall'
    return sem + " " + year

rdf = load_reviews()
cdf = get_course_df()

course = st.selectbox("Choose Course", sorted(cdf.name))

course_df = rdf[rdf.name == course]
rating, difficulty, workload = course_df.rating.mean(),  course_df.difficulty.mean(),  course_df.workload.mean()

st.header(cdf[cdf.name == course]['id'].iloc[0] + ": "+course)
col1, col2, col3 = st.columns(3)
col1.metric(label="Average Rating", value="{:.2f}".format(rating))
col2.metric(label="Average Difficulty", value="{:.2f}".format(difficulty))
col3.metric(label="Average Workload", value="{:.2f}".format(workload))

fig = px.strip(course_df, width=w, height=h,
           title=f'{course} Reviews',
           x='rating', y='difficulty',
           hover_data=['id', 'name', 'workload', 'difficulty'])
           
st.plotly_chart(fig)
# fig = px.scatter(course_df, width=w, height=h,
#            size=course_df['workload'],
#            title=f'{course} Reviews',
#            opacity=0.5,
#            x='rating', y='difficulty',
#            hover_data=['id', 'name', 'workload', 'difficulty'])
# st.plotly_chart(fig)

st.header("Reviews")
st.markdown('***')
for index, row in course_df.iterrows():

    st.subheader(get_semester(row['semester_id']) + " Review")
    c = st.container()
    col1, col2, col3 = c.columns(3)
    col1.metric(label="Rating", value=row['rating'], delta="{:.2f}".format(row['rating'] - rating))
    col2.metric(label="Difficulty", value=row['difficulty'], delta="{:.2f}".format(row['difficulty'] - difficulty))
    col3.metric(label="Workload", value=row['workload'], delta="{:.2f}".format(row['workload'] - workload))

    c.markdown(row['body'])
    st.markdown('***')
    # st.write('#')