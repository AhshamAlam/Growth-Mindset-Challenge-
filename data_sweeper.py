# Imports
import streamlit as st
import os
from io import BytesIO
import pandas as pd

# --- App configuration ---
st.set_page_config(page_title="Data Sweeper", page_icon="⚡", layout="wide")
st.title("Data Sweeper")
st.subheader("Clean and convert your data between CSV and Excel formats with ease!")


# --- File Upload ---
input_files = st.file_uploader(
    label="Upload one or more CSV or Excel files:",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# --- File Processing ---
if input_files:
    for data_file in input_files:
        extension = os.path.splitext(data_file.name)[-1].lower()
        session_key = f"{data_file.name}_content"

        # Load file into session_state if not already present
        if session_key not in st.session_state:
            if extension == ".csv":
                st.session_state[session_key] = pd.read_csv(data_file)
            elif extension == ".xlsx":
                st.session_state[session_key] = pd.read_excel(data_file)
            else:
                st.error(f"Unsupported file format: {extension}")
                continue

        df_data = st.session_state[session_key]

        # Display file information
        st.markdown(f"### 📄 File: `{data_file.name}`")
        st.text(f"Size: {data_file.size / 1024:.2f} KB")
        st.markdown("**Preview:**")
        st.dataframe(df_data.head())

        # --- Data Cleaning ---
        st.subheader("🧽 Clean Your Data")
        if st.checkbox(f"Enable cleaning for `{data_file.name}`"):
            clean_col1, clean_col2 = st.columns(2)

            # Remove Duplicates
            with clean_col1:
                if st.button(f"Remove duplicates from `{data_file.name}`"):
                    st.session_state[session_key].drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed.")

            # Fill Missing Values
            with clean_col2:
                if st.button(f"Fill missing values in `{data_file.name}`"):
                    nums_only = st.session_state[session_key].select_dtypes(include='number').columns
                    st.session_state[session_key][nums_only] = st.session_state[session_key][nums_only].fillna(
                        st.session_state[session_key][nums_only].mean()
                    )
                    st.success("✅ Missing values filled.")

        # --- Column Selection ---
        st.subheader("🧾 Choose Columns to Keep")
        selected_columns = st.multiselect(
            label=f"Select columns to include from `{data_file.name}`:",
            options=df_data.columns.tolist(),
            default=df_data.columns.tolist()
        )

        # --- Basic Visualization ---
        st.subheader("📈 Quick Visual")
        if st.checkbox(f"Show charts for `{data_file.name}`"):
            numeric_df = st.session_state[session_key][selected_columns].select_dtypes(include='number')

            # Clean column names to be strings and remove leading/trailing spaces
            numeric_df.columns = [
                f"col_{i+1}" if col == "" else str(col).strip() for i, col in enumerate(numeric_df.columns)
            ]

            # Ensure numeric data and handle conversion
            numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce')

            if not numeric_df.empty and numeric_df.shape[1] > 1:
                st.bar_chart(numeric_df.iloc[:, :2])
            else:
                st.info("ℹ️ Only one numeric column available for visualization or no valid numeric data.")

        # --- File Conversion ---
        st.subheader("📤 Convert and Download")
        format_choice = st.radio(
            label=f"Choose output format for `{data_file.name}`:",
            options=["CSV", "Excel"],
            key=f"format_option_{data_file.name}"
        )

        if st.button(f"Convert `{data_file.name}` now"):
            download_buffer = BytesIO()
            export_data = st.session_state[session_key][selected_columns]

            # Write to buffer based on format
            if format_choice == "CSV":
                export_data.to_csv(download_buffer, index=False)
                out_filename = data_file.name.replace(extension, ".csv")
                out_mime = "text/csv"
            else:
                export_data.to_excel(download_buffer, index=False)
                out_filename = data_file.name.replace(extension, ".xlsx")
                out_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            download_buffer.seek(0)

            # --- Download Button ---
            st.download_button(
                label=f"⬇️ Download `{out_filename}`",
                data=download_buffer,
                file_name=out_filename,
                mime=out_mime
            )
            st.success("🎉 File is ready for download!")

