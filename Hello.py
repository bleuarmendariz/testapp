import streamlit as st
import pandas as pd
import openpyxl

def confidence(row):
    if row['Spot Time Frame'] == 15:
        if row['spot/dest expansion'] == 2020 and row['Spot # of Companies'] >= 13:
            return 'Very High'
        elif row['spot/dest expansion'] == 2020 and (row['Spot # of Companies'] < 13 and row['Spot # of Reports'] > 20): 
            return 'High'
        elif row['spot/dest expansion'] == 2030 and row['Spot # of Companies'] > 13:
            return 'High'
        elif row['spot/dest expansion'] == 2030 and (row['Spot # of Companies'] < 13 and row['Spot # of Reports'] > 20): 
            return 'Med High'
        elif row['spot/dest expansion'] == 3030: 
            return 'Med'
        elif row['spot/dest expansion'] == 3040: 
            return 'Med Low'
        else:
            return 'Low'
    elif row['Spot Time Frame'] == 30:
        if row['spot/dest expansion'] == 2020 and row['Spot # of Companies'] > 13:
            return 'Med'
        elif row['spot/dest expansion'] == 2030 and row['Spot # of Companies'] < 22:
            return 'Med Low'
        elif row['spot/dest expansion'] == 2020 and row['Spot # of Companies'] < 13:
            return 'Med Low'
        else:
            return "Low"
    elif row['Spot Time Frame'] == 60:
        if row['spot/dest expansion'] == 2020: 
            return 'Med low'
    else:
        return "Low"
        

def auto_adjust(df):
    df['PC-Miler Practical Mileage'] = df['PC-Miler Practical Mileage'].astype(int)
    df['suggested_rate'] = df.apply(lambda x: x['Spot Avg Linehaul Rate'] * 1.13 if x['Spot High Linehaul Rate'] - x['Spot Avg Linehaul Rate'] > x['Spot Avg Linehaul Rate'] - x['Spot Low Linehaul Rate'] else x['Spot Avg Linehaul Rate'] * 1.18, axis = 1)
    df['Margin'] = (df['suggested_rate'] * df['PC-Miler Practical Mileage']) - (df['Spot Avg Linehaul Rate'] * df['PC-Miler Practical Mileage'])
    df['adj'] = df.apply(lambda x: (150 / x['PC-Miler Practical Mileage']) + x['Spot Avg Linehaul Rate'] if x.Margin < 150 else( (850 / x['PC-Miler Practical Mileage'] + x['Spot Avg Linehaul Rate']) if x.Margin > 850 else x['suggested_rate']), axis = 1)
    df['Spot Origin Geo Expansion'] = df['Spot Origin Geo Expansion'].str.extract('(\d+)')
    df['Spot Destination Geo Expansion'] = df['Spot Destination Geo Expansion'].str.extract('(\d+)')
    df['spot/dest expansion'] = df['Spot Origin Geo Expansion'] + df['Spot Destination Geo Expansion']
    df['spot/dest expansion'] = df['spot/dest expansion'].astype(int)
    df['Spot # of Companies'] = df['Spot # of Companies'].astype(int)
    df['Spot # of Reports'] = df['Spot # of Reports'].astype(int)
    df['Spot Time Frame'] = df['Spot Time Frame'].astype(int)
    df['Confidence'] = df.apply(confidence, axis =1)
    df['Final ADJ'] = df.apply(final_adj, axis = 1)
    return df

def convert_df(df):
    return df.to_csv().encode('utf-8')

def final_adj(row):
    if row['Confidence'] == 'Very High':
        return row['adj']
    elif row['Confidence'] == 'High':
        return row['adj']
    elif row['Confidence'] == 'Med High':
        return row['adj'] + max(25/row['PC-Miler Practical Mileage'],row['Spot Avg Linehaul Rate'] * .03 )
    elif row['Confidence'] == 'Med':
        return row['adj'] + max(40/row['PC-Miler Practical Mileage'],row['Spot Avg Linehaul Rate'] * .04 )
    elif row['Confidence'] == 'Med Low':
        return row['adj'] + max(50/row['PC-Miler Practical Mileage'],row['Spot Avg Linehaul Rate'] * .05 )
    elif row['Confidence'] == 'Low':
        return row['adj'] + max(75/row['PC-Miler Practical Mileage'],row['Spot Avg Linehaul Rate'] * .07 )

st.set_page_config(page_title="DAT Auto Adjuster", page_icon="📈")
st.markdown("# DAT Auto Adjuster")
st.sidebar.header("DAT Auto Adjuster")

uploaded_file = st.file_uploader("Upload the multilane template!")

df = pd.read_csv(uploaded_file)

st.write(auto_adjust(df))

csv = convert_df(df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='completed_multilane.csv',
    mime='text/csv',
)
