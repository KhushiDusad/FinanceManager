import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyttsx3
import plotly.express as px
from gtts import gTTS
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def export_data(expense_df, export_format):
    if export_format == "CSV":
        file_extension = "csv"
        file_content_type = "text/csv"
        file_name = "expenses.csv"
        expense_df.to_csv(file_name, index=False)
    elif export_format == "Excel":
        file_extension = "xlsx"
        file_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file_name = "expenses.xlsx"
        expense_df.to_excel(file_name, index=False)
    elif export_format == "JSON":
        file_extension = "json"
        file_content_type = "application/json"
        file_name = "expenses.json"
        expense_df.to_json(file_name, orient="records")

    # Provide download link for the exported file
    with open(file_name, "rb") as f:
        file_data = f.read()
    b64_file = base64.b64encode(file_data).decode("utf-8")
    download_link = f'<a href="data:{file_content_type};base64,{b64_file}" download="{file_name}">Download {export_format} File</a>'
    st.markdown(download_link, unsafe_allow_html=True)

def generate_visualizations(expense_df, income=0, total_expenses=0, total_balance=0):
    # Bar Graph
    data = pd.DataFrame({
        "Category": ["Total Income", "Total Expenses", "Total Balance"],
        "Amount": [income, total_expenses, total_balance]
    })

    # Create a horizontal bar chart using Plotly Express
    finance_summary_fig = px.bar(data, x="Amount", y="Category", orientation="h",
                 labels={"Amount": "Amount", "Category": ""},
                 title="Finance Summary")

    category_amounts = expense_df.groupby("Category")["Amount"].sum().reset_index()
    expenses_breakdown_fig = px.pie(category_amounts, values="Amount", names="Category",
                                     title="Expenses Breakdown", hole=0.3)
    
    return finance_summary_fig, expenses_breakdown_fig

def generate_pdfvisualizations(expense_df, income, total_expenses, total_balance):
    # Bar Graph
    bar_chart_fig, ax = plt.subplots(figsize=(8, 6))
    data = {
        "Metrics": ["Total Income", "Total Expenses", "Total Balance"],
        "Amount": [income, total_expenses, total_balance]
    }
    df = pd.DataFrame(data)
    sns.barplot(x="Amount", y="Metrics", data=df, ax=ax)
    plt.xticks(rotation=0)
    plt.title("Finance Summary")
    plt.tight_layout()

    # Pie chart
    pie_chart_fig, ax = plt.subplots(figsize=(8, 6))
    category_amounts = expense_df.groupby("Category")["Amount"].sum()
    ax.pie(category_amounts, labels=category_amounts.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    plt.title("Expenses Breakdown")
    plt.tight_layout()

    return bar_chart_fig, pie_chart_fig

def create_pdf_report(expense_df, income, total_expenses, total_balance, bar_chart_fig, pie_chart_fig, incurrency):
    # Create PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Styles
    styles = getSampleStyleSheet()

    # Add title
    title = Paragraph("Finance Report", styles['Title'])
    content = [title, Spacer(1, 12)]

    # Table for income, expenses, and balance
    data = [
        ["Total Income", f"{incurrency} {income:.2f}"],
        ["Total Expenses", f"{incurrency} {total_expenses:.2f}"],
        ["Total Balance", f"{incurrency} {total_balance:.2f}"],
    ]
    table = Table(data, colWidths=[200, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "grey"),
        ("TEXTCOLOR", (0, 0), (-1, 0), (1, 1, 1)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
    ]))
    content.append(table)
    content.append(Spacer(1, 24))

    # Add bar chart
    bar_chart_image = BytesIO()
    bar_chart_fig.savefig(bar_chart_image, format="png")
    bar_chart_img = Image(bar_chart_image, width=400, height=300)
    content.append(bar_chart_img)
    content.append(Spacer(1, 12))

    # Add pie chart
    pie_chart_image = BytesIO()
    pie_chart_fig.savefig(pie_chart_image, format="png")
    pie_chart_img = Image(pie_chart_image, width=400, height=300)
    content.append(pie_chart_img)
    content.append(Spacer(1, 12))

    # Create a table from the expense DataFrame
    expense_table_data = [["Category", "Date", "Amount"]]
    for _, row in expense_df.iterrows():
        expense_table_data.append([row["Category"], row["Date"].strftime("%Y-%m-%d"), f"{incurrency}{row['Amount']:.2f}"])
    expense_table = Table(expense_table_data)
    expense_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "grey"),
        ("TEXTCOLOR", (0, 0), (-1, 0), (1, 1, 1)),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), (0.95, 0.95, 0.95)),
        ("GRID", (0, 0), (-1, -1), 1, (0.75, 0.75, 0.75)),
    ]))
    content.append(expense_table)

    # Build PDF content
    doc.build(content)

    # Save PDF
    pdf_data = buffer.getvalue()
    with open("finance_report.pdf", "wb") as f:
        f.write(pdf_data)

def get_download_link(file_path, link_text):
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
    return f'<a href="data:application/pdf;base64,{b64_pdf}" download="{file_path}" target="_blank">{link_text}</a>'


def main():
    st.title("Personal Finance Manager")

    currency = ["USD", "EUR", "GBP", "JPY", "INR", "KRW"]

    # Input for Income
    st.header("Income")
    income, incurrency = st.columns(2)
    with income:
        income = st.number_input("Enter your income:", value=0.0, step=1.0, key="income")
    with incurrency:
        incurrency = st.selectbox("Select currency:", currency)

    if income < 0:
        st.warning("Income cannot be negative.")
        return

    # Initialize or load the expense DataFrame
    if 'expense_df' not in st.session_state:
        st.session_state.expense_df = pd.DataFrame(columns=["Category", "Amount", "Date"])

    # Input for Expenses
    st.header("Expenses")
    expense_category = st.text_input("Enter expense category:", key="expense_category")
    expense_amount = st.number_input("Enter expense amount:", value=0.0, step=1.0, key="expense_amount")
    expense_date = st.date_input("Expense Date:", key="expense_date")
    add_expense = st.button("Add Expense", key="add_expense")

    total_expenses = st.session_state.expense_df["Amount"].sum()
    total_balance = income - total_expenses

    # Add expense to the DataFrame if the button is clicked and validate against negative values and balance
    if add_expense:
        if expense_amount < 0:
            st.warning("Expense amount cannot be negative.")
        elif expense_amount > total_balance:
            st.warning("Expense amount cannot exceed total balance.")
        elif not expense_category:
            st.warning("Expense category is required.")
        else:
            # Check if the category already exists on the same date
            existing_expense_index = st.session_state.expense_df[
                (st.session_state.expense_df["Category"] == expense_category) &
                (st.session_state.expense_df["Date"] == expense_date)].index

            if not existing_expense_index.empty:
                existing_index = existing_expense_index[0]
                st.session_state.expense_df.loc[existing_index, "Amount"] = expense_amount
            else:
                new_expense = pd.DataFrame({"Category": [expense_category], "Amount": [expense_amount], "Date": [expense_date]})
                st.session_state.expense_df = pd.concat([st.session_state.expense_df, new_expense], ignore_index=True)

    # Sort the expense DataFrame by date
    st.session_state.expense_df.sort_values(by="Date", inplace=True)

    total_expenses = st.session_state.expense_df["Amount"].sum()
    total_balance = income - total_expenses

     # Create dashboard layout with columns
    col1, col2 = st.columns(2)

    with col1:
        # Display Expense Log
        st.header("Expense Log")
        if not st.session_state.expense_df.empty:
            st.text(st.session_state.expense_df.to_string(index=False))

    with col2:
        # Visualization: Expenses Breakdown - Pie Chart
        st.header("Expenses Breakdown")
        if not st.session_state.expense_df.empty:
            _, expenses_breakdown_fig = generate_visualizations(st.session_state.expense_df)
            st.plotly_chart(expenses_breakdown_fig)

        # Visualization: Finance Summary - Bar Chart
    st.header("Finance Summary")
    if not st.session_state.expense_df.empty:
        finance_summary_fig, _ = generate_visualizations(st.session_state.expense_df, income, total_expenses, total_balance)
        st.plotly_chart(finance_summary_fig)
    
    # Expense Trends Over Time
    st.header("Expense Trends Over Time")
    if not st.session_state.expense_df.empty:
        expense_trend_df = st.session_state.expense_df.groupby("Date")["Amount"].sum().reset_index()
        expense_trend_fig = px.line(expense_trend_df, x="Date", y="Amount",
                                    labels={"Amount": "Total Amount", "Date": "Expense Date"},
                                    title="Expense Trends Over Time")
        st.plotly_chart(expense_trend_fig)

    # Display Total Balance section
    st.header("Total Balance")
    st.write(f"Total Income: {incurrency} {income:.2f}")
    st.write(f"Total Expenses: {incurrency} {total_expenses:.2f}")
    st.write(f"Total Balance: {incurrency} {total_balance:.2f}")
    
    export_format = st.selectbox("Select export format:", ["CSV", "Excel", "JSON"])
    export_button = st.button("Export Data")
    
    if export_button:
        if not st.session_state.expense_df.empty:
            export_data(st.session_state.expense_df, export_format)
            st.success(f"Data exported as {export_format} successfully!")

    colm1, colm2= st.columns(2)
    with colm1:
        explain_expenses = st.button("Explain Expenses", key="Explain_Expenses")
        if explain_expenses:
            text_to_speech = "Here's the breakdown of your expenses:\n"
            category_amounts = st.session_state.expense_df.groupby("Category")["Amount"].sum().reset_index()
            for _, row in category_amounts.iterrows():
                text_to_speech += f"For {row['Category']}, you spent {incurrency} {row['Amount']:.2f}\n"
    
            text_to_speech += f"Your total expenses are {incurrency} {total_expenses:.2f}"
            tts = gTTS(text_to_speech)
            tts.save("expenses.mp3")
            st.audio("expenses.mp3")

    with colm2:
        if st.button("Generate PDF Report") and not st.session_state.expense_df.empty:
            bar_chart_fig, pie_chart_fig = generate_pdfvisualizations(st.session_state.expense_df, income, total_expenses, total_balance)
            create_pdf_report(st.session_state.expense_df, income, total_expenses, total_balance, bar_chart_fig, pie_chart_fig, incurrency)
            st.success("PDF Report generated successfully!")
            st.markdown(get_download_link("finance_report.pdf", "Download PDF Report"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()