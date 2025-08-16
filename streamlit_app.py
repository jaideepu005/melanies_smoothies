import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# -------------------------------
# UI Setup
# -------------------------------
st.title("🥤 Customize Your Smoothie ! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name of the smoothie will be:", name_on_order)

# -------------------------------
# Snowflake Session
# -------------------------------
session = get_active_session()

# Load fruit options
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)

# Multiselect fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    [row["FRUIT_NAME"] for row in my_dataframe.collect()],
    max_selections=5,
)

# -------------------------------
# Show Nutrition Info + Build String
# -------------------------------
ingredients_string = ", ".join(ingredients_list)  # ✅ Auto-trimmed clean string

if ingredients_list:
    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + " Nutrition Information")

        search_value = (
            my_dataframe.filter(col("FRUIT_NAME") == fruit_chosen)
            .collect()[0]["SEARCH_ON"]
        )

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_value
        )

        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# -------------------------------
# Submit Order
# -------------------------------
if st.button("Submit Order"):
    if not name_on_order or not ingredients_list:
        st.error("⚠️ Please enter a name and select at least one ingredient.")
    else:
        # Ensure table exists
        session.sql(
            """
            CREATE TABLE IF NOT EXISTS SMOOTHIES.PUBLIC.ORDERS (
                ORDER_ID INTEGER AUTOINCREMENT,
                NAME_ON_ORDER STRING NOT NULL,
                INGREDIENTS STRING NOT NULL,
                ORDER_TS TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
        ).collect()

        # Insert new order safely
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (NAME_ON_ORDER, INGREDIENTS) VALUES (%s, %s)",
            params=(name_on_order.strip(), ingredients_string.strip()),
        ).collect()

        st.success(f"✅ Your Smoothie is ordered, {name_on_order.strip()}!")

        # Show recent orders
        recent = session.sql(
            """
            SELECT ORDER_ID, NAME_ON_ORDER, INGREDIENTS, ORDER_TS
            FROM SMOOTHIES.PUBLIC.ORDERS
            ORDER BY ORDER_TS DESC
            LIMIT 10
            """
        ).to_pandas()
        st.dataframe(recent, use_container_width=True)
