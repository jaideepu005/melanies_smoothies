# Import python packages

import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie !:cup_with_straw:")
st.write(
  """Choose the furits you want in your custom Smoothie!
  """)



name_on_order = st.text_input('Name on Smoothie')
st.write('The name of the smoothie will be:', name_on_order  )




session = get_active_session()  
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

#st.multiselect(label, options, default=None, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, max_selections=None, placeholder=None, disabled=False, label_visibility="visible", accept_new_options=False, width="stretch")

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
     my_dataframe ,  # Replace 'ingredient_column' with your actual column name
     max_selections=5
)

if ingredients_list:
    # Show numbered list
    st.text("\n".join(f"{i}: {fruit}" for i, fruit in enumerate(ingredients_list)))

    # Build the ingredients string for SQL
    ingredients_string = ', '.join(ingredients_list)  # comma-separated for DB

    # Create the SQL insert (with name_on_order included)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Show the button
    time_to_insert = st.button('Submit Order')

    # If button is clicked, run insert
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")




