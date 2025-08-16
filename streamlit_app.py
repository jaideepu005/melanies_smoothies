# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie ! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Text input for smoothie name
name_on_order = st.text_input('Name on Smoothie')
st.write('The name of the smoothie will be:', name_on_order)

# ✅ Get the active Snowflake session (provided automatically in Streamlit-in-Snowflake)
session = get_active_session()

# Load fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multi-select for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.collect(),   # convert Snowpark DataFrame to list of rows
    max_selections=5
)

# Show selected ingredients
if ingredients_list:
    # Convert Row objects to strings
    fruits = [row['FRUIT_NAME'] for row in ingredients_list]

    st.text("\n".join(f"{i+1}: {fruit}" for i, fruit in enumerate(fruits)))

    # Build the ingredients string for SQL
    ingredients_string = ', '.join(fruits)

    # SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Button to submit
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
