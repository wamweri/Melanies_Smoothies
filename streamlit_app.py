import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie:")

st.write(
    "The name on your Smoothie will be:",
    name_on_order
)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Bring back both the friendly fruit name and the API search value
my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# Convert the Snowpark dataframe into a Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Show only the friendly fruit names in the multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Find the API search value for the selected fruit
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        # Display nutrition information for each selected fruit
        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Build the Snowflake INSERT statement
    my_insert_stmt = """insert into smoothies.public.orders
                        (ingredients, name_on_order)
                        values ('""" + ingredients_string + """',
                                '""" + name_on_order + """')"""

    # Keep this temporarily while following the course
    st.write(my_insert_stmt)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered for {name_on_order}!",
            icon="✅"
        )
