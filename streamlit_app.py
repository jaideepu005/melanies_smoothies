import streamlit as st
import requests  # <-- needed for the API call
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Page title
st.title(f":cup_with_straw: Customize Your Smoothie ! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie')
st.write('The name of the smoothie will be:', name_on_order)

# Get Snowflake session
session = get_active_session()

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Collect rows into Python list of Row objects
fruit_rows = my_dataframe.collect()

# Extract fruit names into a plain Python list
fruit_names = [row['FRUIT_NAME'] for row in fruit_rows]

# Show multiselect for fruit choices
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# If user selected ingredients, display them and fetch nutrition info
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Call API for nutrition data
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)

        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Could not fetch data for {fruit_chosen}")

    # Remove trailing comma + space
    ingredients_string = ingredients_string.rstrip(', ')

    # SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Insert order when user clicks submit
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
