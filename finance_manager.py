import streamlit as st
import pandas as pd

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

    # Display Expense Log
    st.header("Expense Log")
    if not st.session_state.expense_df.empty:
        st.dataframe(st.session_state.expense_df)

    # Calculate and display Total Balance
    total_expenses = st.session_state.expense_df["Amount"].sum()
    total_balance = income - total_expenses
    st.header("Total Balance")
    st.write(f"Total Income: ${income}")
    st.write(f"Total Expenses: ${total_expenses:.2f}")
    st.write(f"Total Balance: ${total_balance:.2f}")

if __name__ == "__main__":
    main()
