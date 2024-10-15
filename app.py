import pandas as pd
import streamlit as st

# Load the data from Excel files
inflation_data = pd.read_excel('Inflation_event_stock_analysis_resultsOct.xlsx')
income_data = pd.read_excel('Inflation_IncomeStatement_correlation_results.xlsx')

# Set up Streamlit app
st.title('Stock Analysis Based on Inflation Events')

# Create a sidebar for user input
st.sidebar.header('Search for a Stock')
stock_name = st.sidebar.text_input('Enter Stock Symbol:', '')

# User input for expected upcoming inflation
expected_inflation = st.sidebar.number_input('Enter Expected Upcoming Inflation Rate (%):', value=3.65, step=0.01)

# Function to fetch details for a specific stock
def get_stock_details(stock_symbol):
    inflation_row = inflation_data[inflation_data['Symbol'] == stock_symbol]
    income_row = income_data[income_data['Stock Name'] == stock_symbol]

    if not inflation_row.empty and not income_row.empty:
        inflation_details = inflation_row.iloc[0]
        income_details = income_row.iloc[0]

        st.subheader(f'Details for {stock_symbol}')
        
        # Display inflation event data
        st.write("### Inflation Event Data")
        st.write(inflation_row)

        # Generate projections based on expected inflation
        generate_projections(inflation_details, income_details, expected_inflation)
    else:
        st.warning('Stock symbol not found in the data.')

# Function to generate projections based on expected inflation
def generate_projections(inflation_details, income_details, expected_inflation):
    latest_event_value = income_details['Latest Event Value']  # Getting the actual inflation value from income details
    inflation_change = expected_inflation - latest_event_value

    # Create a DataFrame to store the results
    projections = pd.DataFrame(columns=['Parameter', 'Current Value', 'Projected Value', 'Change'])

    # Check if 'Latest Close Price' exists
    if 'Latest Close Price' in inflation_details.index:
        latest_close_price = pd.to_numeric(inflation_details['Latest Close Price'], errors='coerce')
        price_change = inflation_details['Event Coefficient'] * inflation_change
        projected_price = latest_close_price + price_change

        # Append the projected data to the DataFrame
        projections = projections.append({
            'Parameter': 'Projected Stock Price',
            'Current Value': latest_close_price,
            'Projected Value': projected_price,
            'Change': price_change
        }, ignore_index=True)

    # Include all columns from Inflation Event Data in projections
    for column in inflation_details.index:
        if column not in ['Symbol', 'Event Coefficient', 'Latest Close Price']:
            current_value = pd.to_numeric(inflation_details[column], errors='coerce')
            if pd.notna(current_value):  # Ensure current value is valid
                projected_value = current_value * (1 + inflation_change / 100)  # Project based on inflation change
                change = projected_value - current_value
                
                # Append to projections DataFrame
                projections = projections.append({
                    'Parameter': column,
                    'Current Value': current_value,
                    'Projected Value': projected_value,
                    'Change': change
                }, ignore_index=True)

    # Display the projections table
    st.write("### Projected Changes in Inflation Event Data")
    st.dataframe(projections)

# Check if user has entered a stock symbol
if stock_name:
    get_stock_details(stock_name)
