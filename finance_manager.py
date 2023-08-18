import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyttsx3
from gtts import gTTS

def main():
    st.title("Personal Finance Manager")

    # Input for Income
    st.header("Income")
    income = st.number_input("Enter your income:", value=0.0, step=1.0)

    # Initialize or load the expense DataFrame
    if 'expense_df' not in st.session_state:
        st.session_state.expense_df = pd.DataFrame(columns=["Category", "Amount"])

    # Input for Expenses
    st.header("Expenses")
    expense_category = st.text_input("Enter expense category:")
    expense_amount = st.number_input("Enter expense amount:", value=0.0, step=1.0)
    add_expense = st.button("Add Expense")

    # Add expense to the DataFrame if the button is clicked
    if add_expense:
        new_expense = pd.DataFrame({"Category": [expense_category], "Amount": [expense_amount]})
        st.session_state.expense_df = pd.concat([st.session_state.expense_df, new_expense], ignore_index=True)

    # Create dashboard layout with columns
    col1, col2, col3 = st.columns(3)

    with col1:
        # Display Expense Log
        st.header("Expense Log")
        if not st.session_state.expense_df.empty:
            st.dataframe(st.session_state.expense_df)

    with col2:
        # Visualization: Expense Categories - Bar Chart
        st.header("Expense Categories")
        if not st.session_state.expense_df.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x="Amount", y="Category", data=st.session_state.expense_df, ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

    with col3:
        # Visualization: Expense Categories - Pie Chart
        st.header("Expenses Breakdown")
        if not st.session_state.expense_df.empty:
            category_amounts = st.session_state.expense_df.groupby("Category")["Amount"].sum()
            fig, ax = plt.subplots()
            ax.pie(category_amounts, labels=category_amounts.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

    # Calculate and display Total Balance
    total_expenses = st.session_state.expense_df["Amount"].sum()
    total_balance = income - total_expenses

    # Display Total Balance section
    st.header("Total Balance")
    st.write(f"Total Income: ${income}")
    st.write(f"Total Expenses: ${total_expenses:.2f}")
    st.write(f"Total Balance: ${total_balance:.2f}")
    
    if st.button("Explain Expenses"):
        text_to_speech = "Here are your expenses:\n"
        for _, row in st.session_state.expense_df.iterrows():
            text_to_speech += f"For {row['Category']}, you spent ${row['Amount']:.2f}\n"

        tts = gTTS(text_to_speech)
        tts.save("expenses.mp3")

        st.audio("expenses.mp3")

if __name__ == "__main__":
    main()
