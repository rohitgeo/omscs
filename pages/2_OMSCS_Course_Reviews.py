import streamlit as st
import pandas as pd
import plotly.express as px

w, h = 1000, 800

st.set_page_config(layout="wide")

st.markdown("# OMSCS Course Reviews")
st.sidebar.markdown("# About this app")
st.sidebar.markdown("This is an open source project and you are very welcome to **contribute** with [pull requests](https://gitHub.com/rohitgeo/omscs/pulls). This app is maintained by [Rohit Singh](https://www.linkedin.com/in/rohitgeo/). Follow me on Twitter to be notified of updates.")

st.sidebar.markdown("[![Star](<https://img.shields.io/github/stars/rohitgeo/omscs.svg?logo=github&style=social>)](<https://gitHub.com/rohitgeo/omscs>) [![Follow](<https://img.shields.io/twitter/follow/geonumist?style=social>)](<https://www.twitter.com/geonumist>)")

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
cc_df = cdf[cdf.name == course]
st.header(cc_df.iloc[0]['id'] + ": "+course)
mdstr = ""
for alias in eval(list(cc_df.aliases)[0]):
    mdstr += f"[![](https://badgen.net/badge/aka/{alias}/blue)]({cc_df.iloc[0]['link']})  "

if cc_df.iloc[0]['foundational'] == 'true':
    mdstr += f"[![](https://badgen.net/badge/foundational/True/green)]({cc_df.iloc[0]['link']}) "
else:
    mdstr += f"[![](https://badgen.net/badge/foundational/False/red)]({cc_df.iloc[0]['link']}) "

mdstr += f"[![](https://badgen.net/badge/www/{cc_df.iloc[0]['id']}/yellow)]({cc_df.iloc[0]['link']})"

st.markdown(mdstr)

col1, col2, col3 = st.columns(3)
col1.metric(label="Average Rating", value="{:.2f}".format(rating))
col2.metric(label="Average Difficulty", value="{:.2f}".format(difficulty))
col3.metric(label="Average Workload", value="{:.2f}".format(workload))

fig = px.strip(course_df, width=w, height=h,
           title=f'{course} Reviews',
           x='rating', y='difficulty',
           hover_data=['id', 'name', 'workload', 'difficulty'])
fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0.01
            ))            
st.plotly_chart(fig, use_container_width=True)           

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
    