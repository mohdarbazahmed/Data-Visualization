import streamlit as st
import pandas as pd
import hashlib
import pycountry
import altair as alt
from PIL import Image
from datetime import date
import plotly.express as px
from streamlit_option_menu import option_menu

def create_user(first, last, username, gender, country, mobile, email, password, agree, is_super_user): 
    hashed_password = hash_password(password)
    data={
        'first':[first],
        'last':[last],
        'username' : [username],
        'gender': [gender],
        'country': [country],
        'mobile':[mobile], 
        'email': [email],
        'password' : [hashed_password],
        'agree': [agree],
        'is_super_user':[is_super_user]
        }
    df = pd.DataFrame(data)
    with open("users.csv", 'a') as f:
        df.to_csv(f,header=f.tell()==0, index=False)

def authenticate_user(email, password):
    user_data = pd.read_csv("users.csv") 
    if email in list(user_data['email']):
        if password == list(user_data[user_data['email']==email]['password'])[0]: 
            return list(user_data[user_data['email']==email]['is_super_user'])[0]
        else:
            return None
    else:
        return None

@st.cache_data(persist=True)
def hash_password(password):
    password = password.encode('utf-8')
    hashed_password = hashlib.sha256(password).hexdigest()
    return hashed_password

def user_login():
    st.title("Welcome to Our Company") 
    st.image("login_page_image.gif",width=350)
    quote = "Success only comes to those who dare to attempt." 
    author = " - Mallika Tripathi" 
    st.write(f" {quote} {author}")

    with st.sidebar:
        st.title("User Login System")
        create_account=st.checkbox("Create New Account") 
    if create_account:
        st.subheader("Create New Account")
        first_name, last_name, user = st.columns(3) 
        first = first_name.text_input("First Name") 
        last = last_name.text_input("Last Name") 
        username = user.text_input("Username")

        gen, coun, mobile_number= st.columns(3)
        gender = gen.selectbox ('Pick your gender', ["Male", "Female", "Other"])
        countries = list(pycountry.countries) 
        country_names = [country.name for country in countries] 
        selected_country = coun.selectbox("Country",country_names) 
        mobile = mobile_number.text_input("Mobile Number")

        email_id, pw, pw2 = st.columns (3)
        email=email_id.text_input("Email Id")
        password = pw.text_input("Password", type="password") 
        confirm_password = pw2.text_input(" Confirm Password", type = "password")

        agree = st.checkbox("I Agree Terms and Conditions") 
        is_super_user = st.checkbox("Superuser")

        if password != confirm_password: 
            st.error("Password do not match")
        else:
            if st.button('Sign Up'):
                if not first or not last or not username or not mobile or not email or not password or not agree: 
                    st.error("Please provide valid inputs for all required fileds") 
                    return 
                else:
                    create_user(first, last, username, gender, selected_country, mobile, email, password, agree, is_super_user) 
                    st.success("You have successfully created an account")
    else:
        with st.sidebar:
            st.text("Please sigin here")
            email = st.text_input("Email") 
            password = st.text_input('Password', type="password") 
            if st.button("Sign In"):
                user_type = authenticate_user(email, password) 
                st.session_state.logged_in=False
                df = pd.read_csv('users.csv') 
                user_type = None

                user = df.loc[df['email']==email]
                if user.empty:
                    st.error("Invalid Email or Password")
                else:
                    hashed_password = hash_password(password)
                    if hashed_password != user['password'].iloc[0]: 
                        st.error('Invalid Email or Password') 
                    else:
                        if user['is_super_user'].iloc[0]: 
                            st.success('Signed in as Superuser') 
                            user_type = 'is_super_user' 
                        else:
                            st.success('Signed in as Normal ser') 
                            user_type != 'is_super_user'

                        st.session_state.logged_in = True
                        st.session_state.user_type = user_type

            Forgot_Password = st.checkbox("Forgot Password")
        if Forgot_Password:
            st.subheader('Reset your Password')
            email = st.text_input('Email', key=Forgot_Password)
            new_password = st.text_input("New Password", type="password") 
            confirm_password= st.text_input(" Confirm Password", type="password")

            if new_password != confirm_password:
                st.error('Password do not match')
            else:
                if st.button("Reset Password"): 
                    df = pd.read_csv("users.csv") 
                    user = df.loc[df['email']==email]
                    if user.empty:
                        st.error('Invalid Email')
                    else:
                        df.loc[df['email']==email, 'password'] = hash_password(new_password)
                        df.to_csv("users.csv",index=False)
                        st.success("Password Reset Successfully")

def sign_out():
    st.session_state.logged_in = False
    st.session_state.user_type = None

def create_super_chart(data,rating_filter, actor_filter, director_filter, from_date, to_date,rank_filter):

    #Add a column for movie rank based on box office earnings
    data["Rank"] = data["Box Office"].rank(ascending=False)

    #Filter the data based on the selected options
    if actor_filter == "All" and director_filter =="All" and rating_filter == "All":
        filtered_df = data[(data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif actor_filter == "All" and director_filter =="All": 
        filtered_df = data[(data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) & 
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif actor_filter == "All" and rating_filter == "All":
        filtered_df = data[(data[ 'Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif director_filter == "All" and rating_filter == "All":
        filtered_df = data[(data['Actor'] == actor_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif actor_filter == "All":
        filtered_df = data[(data['Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif director_filter == "All":
        filtered_df =data[(data['Actor'] == actor_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif rating_filter == "All":
        filtered_df = data[(data['Actor'] == actor_filter) &
        (data['Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    else:
        filtered_df == data[(data['Actor'] == actor_filter) & 
        (data['Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]

    Movie_vs_Box_Office_Earnings, Box_Office_Rank_vs_Year = st.columns(2) 
    with Movie_vs_Box_Office_Earnings:
        # Create a chart for box office earnings by movie title 
        box_office_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X("Box Office:Q", axis=alt.Axis(title="Box Office Earnings")), 
        y=alt.Y("Movie:N", sort="-x", axis=alt.Axis(title="Movie Title")),
        color=alt.Color("Year:N", scale=alt.Scale(scheme="category20"), legend=alt.Legend(title="Year"))
        ).properties(
        width=400,
        height=220,
        title="Movie vs. Box Office Earnings"
        )
        st.altair_chart(box_office_chart, use_container_width=True)

    with Box_Office_Rank_vs_Year:
        rank_chart = alt.Chart(filtered_df).mark_circle(size=100).encode( 
        x=alt.X("Year:N", axis=alt.Axis(title="Year")),
        y=alt.Y("Rank:Q", sort="x", axis=alt.Axis(title="Rank")), 
        color=alt.Color("Actor:N", legend=alt.Legend (title="Actor"))
        ).properties(
        width=400,
        height=220,
        title="Box Office Rank vs. Year")
        st.altair_chart(rank_chart, use_container_width=True)

    Budget_vs_Box_Office_Earnings, Box_Office_by_Year = st.columns(2)
    with Budget_vs_Box_Office_Earnings:
        # Create a bar chart showing the budget and box office earnings for each movie
        fig = px.bar(filtered_df, x='Movie', y=['Budget','Box Office'], title="Budget vs. Box Office Earnings")
        fig.update_layout(barmode="group", xaxis_tickangle=-45, xaxis_title="Movie Title", 
        yaxis_title="Amount (USD)", legend_title="Legend",width=400, height=220)
        st.plotly_chart(fig, use_container_width=True)
    with Box_Office_by_Year:
        yearly_chart= px.bar(filtered_df, x='Year', y=['Box Office'], title="Box Office by Year") 
        yearly_chart.update_layout(xaxis_tickangle=-45, xaxis_title="Year", 
        yaxis_title="Box Office", legend_title="Legend",width=400,height=220) 
        st.plotly_chart(yearly_chart, use_container_width=True)

def show_super_data():
    st.success("Signed in successfully") 
    super_user_title, signout = st.columns([4,1])
    with super_user_title:
        st.subheader("Super User Dashboard")
    with signout:
        menu_expander=st.expander("Menu")
    if menu_expander.button("sign out"):
        sign_out()

    st.sidebar.title("Upload CSV File")
    uploaded_file = st.sidebar.file_uploader('Choose a file', type='csv')
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        # Create a list of unique actors and directors
        actor_options=["All"]+sorted(data["Actor"].unique().tolist()) 
        director_options=["All"]+sorted(data["Director"].unique().tolist()) 
        rating_options = ["All"]+sorted(data['Rating'].unique().tolist())

        Logo, Rating, Actor, Director, From_Date, To_Date, Rank = st.columns([1,2,2,2,2,2,2])
        with Logo:
            logo3 = "https://cdn1.iconfinder.com/data/icons/market-research-astute-vol-2/512/Syndicated_Research-512.png"
            logo_container = st.empty()
        with logo_container.container():
            st.markdown(f'<div class="logo-container"><img src="{logo3}" width="70"></a></div>', unsafe_allow_html=True)
        with Rating:
            rating_filter = st.selectbox("Select rating", rating_options)
        with Actor:
            actor_filter = st.selectbox("Select actor", actor_options)
        with Director:
            director_filter = st.selectbox("Select director", director_options)
        with From_Date:
            from_date = st.date_input("From Date", value=date(1962,1,1),min_value=date(1962,1,1),max_value=date(2015,12,31))
        with To_Date:
            to_date = st.date_input("To Date", value=date(2015,12,31),min_value=date(1962,1,1),max_value=date(2015,12,31))
        with Rank:
            rank_filter = st.slider("Select rank", 1, len(data), (1, len(data)))
        create_super_chart(data, rating_filter, actor_filter, director_filter, from_date, to_date, rank_filter)
        
    else:
        st.warning("Please upload a CSV file.")

def create_normal_chart(data,rating_filter, actor_filter, director_filter, from_date, to_date,rank_filter):

    #Add a column for movie rank based on box office earnings
    data["Rank"]= data["Box Office"].rank(ascending=False)

    #Filter the data based on the selected options
    if actor_filter == "All" and director_filter =="All" and rating_filter == "All":
        filtered_df = data[(data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif actor_filter == "All" and director_filter =="All": 
        filtered_df = data[(data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) & 
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif actor_filter == "All" and rating_filter == "All":
        filtered_df = data[(data[ 'Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif director_filter == "All" and rating_filter == "All":
        filtered_df = data[(data['Actor'] == actor_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif actor_filter == "All":
        filtered_df = data[(data['Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif director_filter == "All":
        filtered_df =data[(data['Actor'] == actor_filter)&
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    elif rating_filter == "All":
        filtered_df = data[(data['Actor'] == actor_filter) &
        (data['Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]
    else:
        filtered_df == data[(data['Actor'] == actor_filter)& 
        (data['Director'] == director_filter) &
        (data['Year'] >= from_date.year) &
        (data['Year'] <= to_date.year) &
        (data['Rating'] == rating_filter) &
        (data['Rank'] >= rank_filter[0]) &
        (data['Rank'] <= rank_filter[1])]

    Budget_vs_Box_Office_Earnings, Box_Office_by_Year = st.columns(2)
    with Budget_vs_Box_Office_Earnings:
        # Create a bar chart showing the budget and box office earnings for each movie
        fig = px.bar(filtered_df, x='Movie', y=[ 'Box Office','Budget'], title="Budget vs. Box Office Earnings")
        fig.update_layout(barmode="group", xaxis_tickangle=-45, xaxis_title="Movie Title", 
        yaxis_title="Amount (USD)", legend_title="Legend",width=400, height=220)
        st.plotly_chart(fig, use_container_width=True)
    with Box_Office_by_Year:
        yearly_chart= px.bar(filtered_df, x='Year', y=['Box Office'], title="Box Office by Year") 
        yearly_chart.update_layout(xaxis_tickangle=-45, xaxis_title="Year", 
        yaxis_title="Box Office", legend_title="Legend",width=400,height=220) 
        st.plotly_chart(yearly_chart, use_container_width=True)

def show_normal_data():
    st.success("Signed in successfully") 
    normal_user_title, signout = st.columns([4,1])
    with normal_user_title:
        st.subheader("Normal User Dashboard")
    with signout:
        st.button("Sign out",on_click=sign_out)

    st.sidebar.title("Upload CSV File")
    uploaded_file = st.sidebar.file_uploader('Choose a file', type='csv')
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        # Create a list of unique actors and directors
        actor_options=["All"]+sorted(data["Actor"].unique().tolist()) 
        director_options=["All"]+sorted(data["Director"].unique().tolist()) 
        rating_options = ["All"]+sorted(data['Rating'].unique().tolist())

        Logo, Rating, Actor, Director, From_Date, To_Date, Rank = st.columns([1,2,2,2,2,2,2])
        with Logo:
            logo3 = "https://cdn1.iconfinder.com/data/icons/market-research-astute-vol-2/512/Syndicated_Research-512.png"
            logo_container = st.empty()
        with logo_container.container():
            st.markdown (f'<div class="logo-container"><img src="{logo3}" width="70"></a></div>', unsafe_allow_html=True)
        with Rating:
            rating_filter = st.selectbox("Select rating", rating_options)
        with Actor:
            actor_filter = st.selectbox("Select actor", actor_options)
        with Director:
            director_filter = st.selectbox("Select director", director_options)
        with From_Date:
            from_date = st.date_input("From Date", value=date(1962,1,1), min_value=date(1962,1,1), max_value=date(2015,12,31))
        with To_Date:
            to_date = st.date_input("To Date", value=date(2015,12,31), min_value=date(1962,1,1), max_value=date(2015,12,31))
        with Rank:
            rank_filter = st.slider("Select rank", 1, len(data), (1, len(data)))
        create_normal_chart(data, rating_filter, actor_filter, director_filter, from_date, to_date, rank_filter)

    else:
        st.warning("Please upload a CSV file.")

st.set_page_config(page_title="Welcome to our company",page_icon=":wave:", layout="wide")

def app():
    st.sidebar.header("Welcome to Our Company") 
    st.sidebar.image("Sidebar_image.gif")
    with st.sidebar:
        selected = option_menu(
        menu_title=None,
        options=["Home", "Projects", "User Login","Contact",], 
        icons=['house', 'book', 'bi bi-bar-chart-line', 'envelope'], 
        menu_icon="cast", 
        default_index=0,
        )

    if selected =="Home":
        st.title("Welcome to Our Company")
        left_image = Image.open("main_page_left_image.gif") 
        Center_image = Image.open('main_page_center_image.gif')
        right_image = Image.open('main_page_right_Image.gif')

        img1, img2, img3 = st.columns(3)
        with img1:
            st.image(left_image, use_column_width=True)
        with img2:
            st.image(Center_image, use_column_width=True)
        with img3: 
            st.image(right_image, use_column_width=True)

        st.header("Meet our Team")
        st.write("Our team is made of experiences developers, designers, and project managers who are passionate about creating great software.")

    elif selected =="Projects":
        st.title("Welcome to Our Company")
        st.header("Products and Services")
        st.write("- Cognitive Business Operations")
        st.write("- Data and Analytics") 
        st.write("- Sustainability Services")
        st.write("- Cloud")
        st.header("Industries")
        st.write("- Banking")
        st.write("- Education")
        st.write("- Energy, Resources, and Utilities")
        st.write("- Healthcare")

    elif selected == "Contact":
        st.header("Get in Touch")
        st.write("If you're interested in learning more about how we can help your business, please don't hesitate to get in touch with us.")
        st.header('Social Media')
        st.write("Follow us on Facebook and Instagram: ")

        # Add CSS to position the logos
        st.markdown(
            """
        <style>
        .logo-container {
        position: absolute;
        top: 0;
        right: 0;
        display: flex;
        align-items: center;
        Justify-content: flex-end;
        height: 30px;
        width: 100%;
        padding-right: 800px;
        box-sizing: border-box;
        }
        .logo-container img { 
            margin-left: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
        )

        #Add logos to the container
        fb_logo ="https://cdn3.iconfinder.com/data/icons/capsocial-round/500/facebook-512.png"
        fb_link ="https://www.facebook.com/"
        insta_logo = "https://cdn4.iconfinder.com/data/icons/social-messaging-ui-color-shapes-2-free/128/social-instagram-new-square2-512.png"
        insta_link ="https://www.instagram.com/"
        twitter_logo='https://cdn3.iconfinder.com/data/icons/social-media-2169/24/social_media_social_media_logo_twitter-512.png'
        twitter_link= 'https://twitter.com/'

        logo_container = st.empty()
        with logo_container.container():
            st.markdown(f'<div class="logo-container"><a href="{fb_link}"><img src="{fb_logo}" width="40"></a><a href="{insta_link}"><img src="{insta_logo}" width="40"></a><a href="{twitter_link}"><img src="{twitter_logo}" width="40"></a></div>', unsafe_allow_html=True)

    elif selected == "User Login":

        if not hasattr(st.session_state, 'logged_in'): 
            st.session_state.logged_in= False

        if not st.session_state.logged_in: 
            user_login()

        if st.session_state.logged_in:
            if st.session_state.user_type == "is_super_user": 
                with st.container():
                    show_super_data()
            else:
                with st.container(): 
                    show_normal_data()
        else:
            st.error(" Please Sign in to access this content.")
app()