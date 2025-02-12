import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

st.title("Excel Data Processor")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

def process_data(df):
    a=8
    df.columns=df.iloc[2]
    df=df[3:]
    df = df.reset_index(drop=True)
    df['Schedule']=df['Schedule'].fillna(method='ffill')
    df = df.loc[:, df.columns.notna()]

    df['Pending']=df['Total']-df['OB']
    df['Loss']=df['Receipts']-(0.92)*df['Sales']

    filtered_df_1=df[(df['Loss']<0) & (df['Schedule']!='SENDER') & (df['Schedule']!='SVC STAFF')]
    filtered_df=df[(df['Pending']>0) & (df['Schedule']!='SENDER') & (df['Schedule']!='SVC STAFF')]

    filtered_df = filtered_df.sort_values(by='Pending', ascending=False)    

    filtered_df_1 = filtered_df_1.sort_values(by='Loss', ascending=True)

    grouped=filtered_df.groupby('Schedule', as_index=False).agg({'Pending': 'sum', 'Sales': 'sum'})
    grouped_1=filtered_df_1.groupby('Schedule', as_index=False)['Loss'].sum()

   
    grouped['Pending']=grouped['Pending'].astype(int)

    grouped_1['Loss']=grouped_1['Loss'].astype(int)

    return df , filtered_df ,filtered_df_1 , grouped , grouped_1 
    


# Function to create a plot
def grouped_create_plot(grouped): 
    st.bar_chart(
    grouped,
    x="Schedule",
    y=["Pending","Sales"],
    color=["#FF0000","#00FFFF"],  # Optional
    )

# Function to create Loss plot
def grouped_create_plot_1(grouped_1):
    fig, ax = plt.subplots()
    grouped_1['Loss'] = abs(grouped_1['Loss'])
    ax.pie(grouped_1['Loss'], labels=grouped_1['Schedule'], autopct='%1.1f%%', startangle=140)
    ax.set_title('Loss Distribution by Schedule')
    ax.axis('equal')  
    st.pyplot(fig)  
#Function to create bar graph
#def revenue_balance():

if uploaded_file:
    # Read the uploaded Excel file
    df = pd.read_excel(uploaded_file)

    
    df , filtered_df,filtered_df_1  , grouped ,grouped_1= process_data(df)
    # Dropdown for options
    option = st.selectbox("Select an option:", [ "Each Schedule","All Schedule"])  # Add more options as needed
    plot_buf = None
    processed_data = None
    if option=="Each Schedule":
        option1 = st.selectbox("Select an option:", list(filtered_df['Schedule'].unique()))
        processed_data=filtered_df[filtered_df['Schedule']==option1]
        processed_data.drop(columns=['Loss'],inplace=True)
        st.write("Balance Data:")
        processed_data_filtered=processed_data[["Name","Total","Pending"]]
        st.dataframe(
            processed_data_filtered,
            column_config={
                "Name": st.column_config.TextColumn("Schedule", width="medium"),    
                "Total": st.column_config.NumberColumn("Current balance", width="medium"),
                "Pending": st.column_config.NumberColumn("Pending amount", width="medium"),
            },
            use_container_width=True,  # Expands to full width
        )

        processed_data=filtered_df_1[filtered_df_1['Schedule']==option1][:10]

        st.write("Loss Data:")
        st.dataframe(processed_data)


        
    elif option=="All Schedule":
        # Create side-by-side grouped bar chart
        grouped_melted = grouped.melt(id_vars=["Schedule"], var_name="Category", value_name="Value")
        chart = (
        alt.Chart(grouped_melted)
        .mark_bar()
        .encode(
        x=alt.X("Schedule:N", title="Schedule", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Value:Q", title="Amount"),
        color="Category:N",  # Differentiates Sales and Revenue
        xOffset="Category:N",  # Ensures side-by-side bars instead of stacking
        tooltip=["Schedule", "Category", "Value"],
            )
        )
        # Display the chart in Streamlit
        st.altair_chart(chart, use_container_width=True)

        processed_data=grouped  

        st.write("Processed Data:")
        st.dataframe(processed_data)

    
    
