"""
Name: Vicente Ibanez
CS230: SN2
Data: Car listing on Craigslist
URL:

Description: This program offers filtering of data by price (range), by manufacturer, by safety, and displas potential
payment plans for the vehicles.
"""


import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import matplotlib.patheffects as path_effects
import numpy_financial as npf
import numpy as np

# title of webpage
st.title(f"{'Welcome to the Luxury Used Car Store':^s}")
# images at the top of the site, and resizing them + adding them in columns
img = Image.open("/Users/Vinny/Desktop/Summer 2021/CS230/Project File/tesla.jpeg")
img = img.resize((200, 200))
img2 = Image.open("/Users/Vinny/Desktop/Summer 2021/CS230/Project File/ford.jpeg")
img2 = img2.resize((200, 200))
img2 = ImageOps.mirror(img2)
img3 = Image.open("/Users/Vinny/Desktop/Summer 2021/CS230/Project File/chevy.jpeg")
img3 = img3.resize((200, 200))
cols = st.beta_columns([4, 4, 4])
cols[0].image(img2)
cols[1].image(img)
cols[2].image(img3)


def bar_chart(data):
    means = data.groupby('manufacturer').mean()  # group by manu, calculate mean
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('${x:,.2f}'))  # adds $ signs and , to y values
    titl = plt.title("Average Cost of Car by Manufacturer", fontsize=18,
                     path_effects=[path_effects.withSimplePatchShadow()])  # displays title
    titl.set_path_effects([path_effects.PathPatchEffect(offset=(2, -2), hatch='xxxx', facecolor='black'),
                           path_effects.PathPatchEffect(edgecolor='#F63366', linewidth=1.5, facecolor='grey')])
    # https://matplotlib.org/stable/tutorials/advanced/patheffects_guide.html for PathPatchEffect code
    plt.ylabel("Cost USD", color="#F63366", size=13)  # code for y label
    plt.xlabel('Manufacturer')      # title for x label
    if len(means.index) >= 7:  # if x labels are too crowded, it further rotates them
        plt.xticks(rotation=90)
    else:
        plt.xticks(rotation=45)
    plt.bar(means.index, means['price'], color=["violet", "indigo", "red", "darkgrey"])


def pie_chart(data):
    # group by number of instances if the number of manufacturers is more than 1 (pie chart)
    manu_counts = data.groupby('manufacturer', group_keys=True).count()
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('${x:,.2f}'))
    plt.title("Quantity of Cars by Manufacturer", fontsize=18, color="#F63366")

    manufact, quant = [], []
    for i in manu_counts.index:
        manufact.append(i)
        quant.append(int(manu_counts.loc[i, "price"]))
    plt.pie(quant, labels=manufact, autopct='%1.1f%%', shadow=False, colors=("lightblue", "indigo", "red", "grey"))


def histo_chart(df):
    num_bins = 5
    plt.title("Price Range")
    plt.xlabel("Distribution of Cars for Sale by Price")
    plt.ylabel("Number of Cars for Sale")
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}'))  # adds $ signs and , to x values
    plt.hist(df["price"], num_bins, facecolor="violet")


def map_create(df):
    df_maps = df[["lon", "lat"]]  # selected these two categories
    df_maps = df_maps.dropna()  # ignores/removes columns/rows that are missing
    df_maps[["lon", "lat"]] = df_maps[["lon", "lat"]].astype("float")  # converts these columns to floats
    st.map(df_maps)     # shows map


def price_range(df):
    st.header("Price Range Selection")
    # find max and min prices:
    max_price = int(max(df["price"]))
    min_price = int(min(df["price"]))

    # dual price slider to get price range, based off of max/min prices
    price = st.slider("Select the Desired Price Range", min_price, max_price, (0, 45000), int(.02*max_price), format=f"$%d")
    df_price_range = df.query("@price[0] <= price <= @price[1]")  # filters data based on prices specified
    if (df_price_range["price"].count() < 20) and (df_price_range["price"].count() > 0):  # if the data that falls w/i data is less than 20 (but more than 1)
        st.error("Specified range has less than 20 observations. Would you like to expand search?")  # asks to expand
        cols5 = st.beta_columns(5)
        yes = cols5[0].button("Yes: Expand")  # yes expand
        no = cols5[1].button("No: Keep")      # no expand
        if yes:  # if y_n is true
            price = (price[0]*.90, price[1]*1.1)  # increases max by 10%, decreases min by 10%
            st.write(f"New price range: ${int(price[0]):,d} to ${int(price[1]):,d}")  # formatting prices to show new price range
            df_price_range = df.query("@price[0] <= price <= @price[1]")  # filters data on 10% increase price range
            st.write(df_price_range[["manufacturer", "model", "price", "year", "odometer"]])  # columns from data frame shown
            st.pyplot(bar_chart(df_price_range))  # function to get bar chart
        if no:  # if no
            st.write(f"Price range: ${price[0]:,d} to ${price[1]:,d}")  # shows price range kept from user
            st.write(df_price_range[["manufacturer", "model", "price", "year", "odometer"]])  # columns from data frame
            cols7 = st.beta_columns(2)
            cols7[0].pyplot(bar_chart(df_price_range))  # bar chart
            cols7[1].pyplot(histo_chart(df_price_range))  # histogram chart
    elif df_price_range["price"].count() <= 0:  # if # of data is less than 1 for price range
        st.error("No observations. Please expand range.")  # shows error
    else:
        st.write(f"Price range: ${price[0]:,d} to ${price[1]:,d}")  # shows price range w format
        st.write(df_price_range[["manufacturer", "model", "price", "year", "odometer"]])  # shows data
        cols7 = st.beta_columns(2)
        cols7[0].pyplot(bar_chart(df_price_range))  # bar chart
        cols7[1].pyplot(histo_chart(df_price_range))  # histogram chart
        st.write(f"Median price is: ${int(df_price_range['price'].median())}")
    # stack chart to show # of cars from each manufacturer  --> PIVOT CHART!!!!

    # Maps:
    map_create(df_price_range)

    return price


def financial_planning(data, price_tuple=(8000, 15000), loan_amount=12000):
    # calculates and displays monthly payments (IR and Yrs based on averages from online)
    st.header("Financial and Safety")
    INTEREST_RATE = .053
    YEARS = 6
    monthly_pmt = npf.pmt(INTEREST_RATE / 12, YEARS * 12, -1 * loan_amount)
    st.write(f"{YEARS*12} monthly payments of ${monthly_pmt:,.2f}")
    st.write(f"Loan Amount: ${loan_amount:,.2f}, Interest: {YEARS*100}%, Years: {YEARS}")

    # filter data with price range using price range tuple
    df_price_range_financial = data.query("@price_tuple[0] <= price <= @price_tuple[1]")

    # safety information
    safety_level = st.radio("Select Desired Level of Saftey", ('low', 'medium', 'high'))

    condition = {}
    for condi in data["condition"]:
        condition[condi] = 1
    # print(condition)  To see the range of conditions
    df_price_safety_range = df_price_range_financial
    if safety_level == 'low':
        condi = ["salvage", "good"]
        df_price_safety_range = df_price_range_financial.query("@condi[0] == condition & @condi[0] == condition & @condi[0] == condition")
    elif safety_level == 'medium':
        condi = ["good", "fair", "like new"]
        df_price_safety_range = df_price_range_financial.query("@condi[0] == condition & @condi[0] == condition")
    elif safety_level == 'high':
        condi = ["excellent", "new", "like new"]
        df_price_safety_range = df_price_range_financial.query("@condi[0] == condition & @condi[0] == condition & @condi[0] == condition")
    st.write(f"Mean Price and Odometer, in Price and Safety Range ${price_tuple[0]:,d} to ${price_tuple[1]:,d}")

    cols8 = st.beta_columns(2)
    table = (pd.pivot_table(df_price_safety_range, index=["manufacturer"], columns=["condition"], values=["price"], aggfunc=np.mean)).astype(int).style.format('${0:,.2f}')
    cols8[0].dataframe(table)
    table2 = (pd.pivot_table(df_price_safety_range, index=["manufacturer"], columns=["condition"], values=["odometer"], aggfunc=np.mean)).astype(int).style.format('{0:,.0f}')
    cols8[1].dataframe(table2)


def manufacturer_options(df):
    st.header("Manufacturer Options")
    car_type_df, car_type_list, car_type_choice = {}, [], []  # empty lists/dicts
    for i in df["manufacturer"]:                   # stores every unique manufacturer name, dict won't repeat keys
        car_type_df[i] = "Manufacturer"
    car_type_list = [str(i).capitalize() for i in car_type_df]  # list of all manufacturers, with first letter capital
    manufacturer_choices = st.multiselect("Select the manufacturer you are interested in.", car_type_list, default="Tesla")
    # ^^^ Streamlit multiple choice drop down box to select types of cars. Tesla set as default selection ^^^
    manufacturer_choices = [str(i).lower() for i in manufacturer_choices]  # used change capital letter to lower for query
    df_manufacturer = df.query(f'manufacturer.isin(@manufacturer_choices)')  # returns data on manufacturers selected
    # display state, image?, paint_color, type, odometer, condition, model, manufacturer, year, price

    # displays info
    st.write(df_manufacturer[["year", "price", "model", "manufacturer", "type", "odometer"]])

    # Creates a bar chart
    st.set_option('deprecation.showPyplotGlobalUse', False)

    # creates pie/bar chart if more than 1 manufacturer is selected, else it only creates bar
    if len(manufacturer_choices) > 1:
        cols4 = st.beta_columns(2)
        cols4[0].pyplot(bar_chart(df_manufacturer))
        cols4[1].pyplot(pie_chart(df_manufacturer))

    #  extra info on specified car
    cols2 = st.beta_columns(3)
    cols2[0].subheader("Enter the index number for more information on the listed sale")  # enter index # for desired car
    specfic_listing = cols2[1].number_input('', step=1, value=3236)
    st.write(df.loc[specfic_listing][["state", "condition", "url", "cylinders", "drive", "fuel", "transmission", "posting_date", "VIN"]])


def main():
    # Reads file
    with open("/Users/Vinny/Desktop/Summer 2021/CS230/Project File/vehicles_copy.csv", 'r') as csv_file:
        data = pd.read_csv(csv_file)
    # price range section
    price_tuple = price_range(data)
    # spacing between sections
    st.markdown("""---""")
    cols6 = st.beta_columns(3)
    cols6[0].subheader("Enter Price of Car:")
    selected_price = cols6[1].number_input('', step=1, value=0)
    st.markdown("""---""")
    if selected_price <= 0:
        financial_planning(data, price_tuple)
    else:
        financial_planning(data, price_tuple, selected_price)
    st.markdown("""---""")
    st.markdown("""---""")
    manufacturer_options(data)


main()

