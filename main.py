# This is the main entry point for the GUI application.

import streamlit as st
import pandas as pd

def generate_bqe_link(marketplace_id, concatenated_asins):
    """Generate the BQE link based on the marketplace ID and ASINs.""" 
    bqe_link = f"https://browse-query-editor-na.aka.amazon.com/?browseNodeFilter=category-node-merchant-facing&catalogAttributes=item_name%2Cbrand%2Cdepartment%2Cstyle%2Cmodel_name%2Cmodel_number%2Ccolor%2Csize%2Cproduct_type&marketplaceId={marketplace_id}&pageSize=500&protocolVersion=imsv2&retailAsins=N&showImages=Y&useSuggestedBrowseNode=N&userQuery={concatenated_asins}&variationParentOnly=N&websiteSearchable=N"
    
    return bqe_link  # Return the constructed BQE link


def main():

    st.set_page_config(
        page_title="BOT AUDITOR",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.example.com/help',
            'Report a bug': "https://www.example.com/bug",
            'About': "This is a Streamlit app for auditing."
        }
    )

    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: #f0f0f0;  /* Change to your desired background color */
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;  /* Change to your desired sidebar color */
        }
        .stButton > button {
            background-color: orange;  /* Button background color */
            color: white;  /* Button text color */
        }
        .stButton > button:hover {
            background-color: darkorange;  /* Button hover color */
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.title("Welcome to the BOT AUDITOR!")

    st.write("Upload a CSV or Excel file:")
    filter_criteria = st.sidebar.text_input("Filter rows by keyword:")

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        # Read the file based on its type
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        # Check for required columns
        required_columns = ['example_asin_1', 'example_asin_2', 'example_asin_3', 'parent_item_id', 'marketplace_id']  # Include parent_item_id and marketplace_id

        if not all(col in df.columns for col in required_columns):
            st.error("The uploaded file does not contain the required columns: 'example_asin_1', 'example_asin_2', 'example_asin_3', 'parent_item_id', 'marketplace_id'. Please upload a valid file.")
            return

        auditors_column = 'Auditors'  # Specify the Auditors column
        if auditors_column in df.columns:
            auditor_values = df[auditors_column].unique()  # Get unique values from the Auditors column
        selected_auditor = st.sidebar.selectbox("Select Auditor", auditor_values, key="auditor_selection")  # Dropdown for selecting an auditor
        line_item_count = df[df[auditors_column] == selected_auditor].shape[0]  # Count the number of line items for the selected auditor
        st.write(f"Number of line items for {selected_auditor}: {line_item_count}")  # Display the count of line items

        # Filter the DataFrame based on the selected auditor and filter criteria
        if filter_criteria:
            df = df[df.apply(lambda row: row.astype(str).str.contains(filter_criteria, case=False).any(), axis=1)]

        df = df[df[auditors_column] == selected_auditor]  # Filter the DataFrame based on the selected auditor

        # Highlight selected rows
        selected_rows = st.multiselect("Select Rows", range(len(df)), key="row_selection")  # Multi-select for selecting multiple rows
        highlighted_df = df.copy()
        highlighted_df['Highlight'] = highlighted_df.index.isin(selected_rows)  # Create a highlight column

        # Display the editable DataFrame with highlighted rows
        st.dataframe(highlighted_df.style.apply(lambda row: ['background: yellow' if row['Highlight'] else '' for _ in range(len(highlighted_df.columns))], axis=1), use_container_width=True)

        # Summary view of selected rows
        if selected_rows:
            st.write(f"Total Selected Rows: {len(selected_rows)}")
            st.write("Selected ASINs:")
            for selected_row in selected_rows:
                asin_values = df[required_columns].iloc[selected_row].tolist()  # Get ASINs from the selected row
                st.write(asin_values)

        if st.button("Perform Batch Action", key="batch_action_button", help="Click to perform actions on selected rows"):
            for selected_row in selected_rows:
                asin_values = df[required_columns].iloc[selected_row].tolist()  # Get ASINs from the selected row
                concatenated_asins = '+'.join(map(str, asin_values))  # Convert all ASINs to strings and concatenate them
                marketplace_id = int(df['marketplace_id'].iloc[selected_row])  # Fetch the marketplace_id value as an integer
                
                # Call the generate_bqe_link function to create the link
                bqe_link = generate_bqe_link(marketplace_id, concatenated_asins)
                
                st.markdown(f"<a href='{bqe_link}' target='_blank'>Open BQE for ASINs: {concatenated_asins}</a>", unsafe_allow_html=True)  # Open the link in a new window

        if st.button("Vermont", key="vermont_button", help="Click to perform Vermont action"):
            parent_item_id = df['parent_item_id'].iloc[selected_row]  # Fetch the parent_item_id value
            marketplace_id = int(df['marketplace_id'].iloc[selected_row])  # Fetch the marketplace_id value as an integer
            vermont_link = f"https://vermont.amazon.com/orphan-tool/{marketplace_id}/{parent_item_id}"  # Construct the link using the marketplace_id and parent_item_id

            st.markdown(f"<a href='{vermont_link}' target='_blank'>Open Vermont Link</a>", unsafe_allow_html=True)  # Open the link in a new window

    st.markdown("<footer style='text-align: center; padding: 10px;'><p><a href='https://www.example.com' target='_blank'>© srisksk</a></p></footer>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
