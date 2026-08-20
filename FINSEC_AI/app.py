import streamlit as st
import sqlite3
from datetime import date
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "finsec.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT,
    amount REAL,
    category TEXT,
    payment_method TEXT,
    description TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    monthly_budget REAL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO settings
(id, monthly_budget)
VALUES (1, 42000)
""")

conn.commit()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="FINSEC AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM STYLE
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    font-size: 23px;
    font-weight: 600;
    margin-top: 4px;
}

.developer {
    font-size: 17px;
    color: #9ca3af;
    margin-top: 5px;
    margin-bottom: 25px;
}

.card {
    padding: 20px;
    border-radius: 12px;
    background: #111827;
    border: 1px solid #273244;
}

.small-text {
    color: #9ca3af;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <h1 style="font-size:30px;">
        💰 FINSEC AI
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Smart Expense & Fraud Detection"
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "💳 Transactions",
            "🚨 Fraud Alerts",
            "💰 Budget & Insights",
            "📁 Data Management",
            "ℹ️ About"
        ]
    )

    st.markdown("---")

    st.caption(
        "Developed by Sahil Suman"
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="main-title">
        💰 FINSEC AI
    </div>

    <div class="subtitle">
        Smart Expense & Fraud Detection System
    </div>

    <div class="developer">
        Developed by <b style="color:white;">
        Sahil Suman
        </b>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD TRANSACTIONS
# =========================================================

df = pd.read_sql_query(
    """
    SELECT *
    FROM transactions
    ORDER BY id DESC
    """,
    conn
)

if not df.empty:

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )


# =========================================================
# COMMON DATA
# =========================================================

if not df.empty:

    total_spending = float(
        df["amount"].sum()
    )

    average_transaction = float(
        df["amount"].mean()
    )

    highest_expense = float(
        df["amount"].max()
    )

    total_transactions = len(df)

else:

    total_spending = 0
    average_transaction = 0
    highest_expense = 0
    total_transactions = 0


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.header("📊 Financial Dashboard")

    st.write(
        "Monitor your spending, budget and transaction risk."
    )

    st.markdown("---")

    # -----------------------------------------------------
    # TOP METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Total Spending",
            f"₹{total_spending:,.2f}"
        )

    with col2:

        st.metric(
            "📊 Average Transaction",
            f"₹{average_transaction:,.2f}"
        )

    with col3:

        st.metric(
            "🔝 Highest Expense",
            f"₹{highest_expense:,.2f}"
        )

    with col4:

        st.metric(
            "🧾 Transactions",
            total_transactions
        )

    st.markdown("---")

    # -----------------------------------------------------
    # BUDGET
    # -----------------------------------------------------

    budget_row = cursor.execute("""
    SELECT monthly_budget
    FROM settings
    WHERE id = 1
    """).fetchone()

    monthly_budget = float(
        budget_row[0]
    )

    current_month = date.today().strftime(
        "%Y-%m"
    )

    if not df.empty:

        current_month_df = df[
            df["transaction_date"]
            .dt.strftime("%Y-%m")
            == current_month
        ]

    else:

        current_month_df = pd.DataFrame()

    if not current_month_df.empty:

        monthly_spending = float(
            current_month_df["amount"].sum()
        )

    else:

        monthly_spending = 0

    remaining_budget = (
        monthly_budget -
        monthly_spending
    )

    if monthly_budget > 0:

        budget_percentage = (
            monthly_spending /
            monthly_budget
        ) * 100

    else:

        budget_percentage = 0

    st.subheader("💰 Monthly Budget")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Budget",
            f"₹{monthly_budget:,.0f}"
        )

    with col2:

        st.metric(
            "Spent",
            f"₹{monthly_spending:,.0f}"
        )

    with col3:

        st.metric(
            "Remaining",
            f"₹{remaining_budget:,.0f}"
        )

    with col4:

        st.metric(
            "Used",
            f"{budget_percentage:.1f}%"
        )

    st.progress(
        min(
            budget_percentage / 100,
            1.0
        )
    )

    if budget_percentage >= 100:

        st.error(
            "🚨 Monthly budget exceeded!"
        )

    elif budget_percentage >= 80:

        st.warning(
            "⚠️ You have used more than 80% "
            "of your monthly budget."
        )

    else:

        st.success(
            "🟢 Spending is currently within budget."
        )

    st.markdown("---")

    # -----------------------------------------------------
    # CHARTS
    # -----------------------------------------------------

    if not df.empty:

        col1, col2 = st.columns(2)

        with col1:

            category_data = (
                df.groupby("category")["amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                title="💳 Spending by Category"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            daily_data = (
                df.groupby(
                    df["transaction_date"]
                    .dt.strftime("%Y-%m-%d")
                )["amount"]
                .sum()
                .reset_index()
            )

            daily_data.columns = [
                "Date",
                "Amount"
            ]

            fig = px.bar(
                daily_data,
                x="Date",
                y="Amount",
                title="📅 Daily Spending"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.info(
            "Add transactions to view dashboard charts."
        )


# =========================================================
# TRANSACTIONS
# =========================================================

elif page == "💳 Transactions":

    st.header("💳 Transaction Management")

    st.subheader("➕ Add New Transaction")

    col1, col2 = st.columns(2)

    with col1:

        transaction_date = st.date_input(
            "Transaction Date",
            value=date.today()
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Shopping",
                "Travel",
                "Entertainment",
                "Bills",
                "Healthcare",
                "Education",
                "Electronics",
                "Other"
            ]
        )

    with col2:

        payment_method = st.selectbox(
            "Payment Method",
            [
                "UPI",
                "Debit Card",
                "Credit Card",
                "Cash",
                "Net Banking"
            ]
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Amazon purchase"
        )

    if st.button(
        "💾 Save Transaction",
        use_container_width=True
    ):

        if amount <= 0:

            st.error(
                "❌ Please enter a valid amount."
            )

        else:

            cursor.execute("""
            INSERT INTO transactions
            (
                transaction_date,
                amount,
                category,
                payment_method,
                description
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                str(transaction_date),
                amount,
                category,
                payment_method,
                description
            ))

            conn.commit()

            st.success(
                "✅ Transaction saved successfully!"
            )

            st.rerun()

    st.markdown("---")

    st.subheader("📋 Transaction History")

    if not df.empty:

        # SEARCH

        col1, col2, col3 = st.columns(3)

        with col1:

            search = st.text_input(
                "🔍 Search",
                placeholder="Search description..."
            )

        with col2:

            filter_category = st.selectbox(
                "🏷️ Category",
                ["All"] + sorted(
                    df["category"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        with col3:

            filter_payment = st.selectbox(
                "💳 Payment Method",
                ["All"] + sorted(
                    df["payment_method"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        filtered_df = df.copy()

        if search:

            filtered_df = filtered_df[
                filtered_df["description"]
                .fillna("")
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if filter_category != "All":

            filtered_df = filtered_df[
                filtered_df["category"]
                == filter_category
            ]

        if filter_payment != "All":

            filtered_df = filtered_df[
                filtered_df["payment_method"]
                == filter_payment
            ]

        st.caption(
            f"Showing {len(filtered_df)} "
            f"of {len(df)} transactions"
        )

        if not filtered_df.empty:

            for _, row in filtered_df.iterrows():

                col1, col2, col3, col4, col5, col6 = st.columns(
                    [
                        1.5,
                        1.5,
                        1.5,
                        1.5,
                        2.5,
                        0.8
                    ]
                )

                with col1:

                    st.write(
                        row["transaction_date"]
                        .strftime("%Y-%m-%d")
                    )

                with col2:

                    st.write(
                        f"₹{row['amount']:,.2f}"
                    )

                with col3:

                    st.write(
                        row["category"]
                    )

                with col4:

                    st.write(
                        row["payment_method"]
                    )

                with col5:

                    st.write(
                        row["description"]
                        if row["description"]
                        else "-"
                    )

                with col6:

                    if st.button(
                        "🗑️",
                        key=f"delete_{row['id']}"
                    ):

                        cursor.execute(
                            """
                            DELETE FROM transactions
                            WHERE id = ?
                            """,
                            (
                                int(row["id"]),
                            )
                        )

                        conn.commit()

                        st.success(
                            "Transaction deleted!"
                        )

                        st.rerun()

                st.divider()

        else:

            st.info(
                "No transactions match the selected filters."
            )

    else:

        st.info(
            "No transactions recorded yet."
        )


# =========================================================
# FRAUD ALERTS
# =========================================================

elif page == "🚨 Fraud Alerts":

    st.header("🚨 AI Fraud Detection")

    st.write(
        "FINSEC AI analyzes transaction amounts "
        "and identifies unusual spending patterns."
    )

    if len(df) >= 2:

        median_amount = float(
            df["amount"].median()
        )

        if median_amount <= 0:

            median_amount = 1

        results = []

        ml_predictions = {}

        # -------------------------------------------------
        # MACHINE LEARNING
        # -------------------------------------------------

        if len(df) >= 10:

            model = IsolationForest(
                contamination="auto",
                random_state=42
            )

            model.fit(
                df[["amount"]]
            )

            predictions = model.predict(
                df[["amount"]]
            )

            for index, prediction in zip(
                df.index,
                predictions
            ):

                ml_predictions[index] = prediction

        # -------------------------------------------------
        # RISK CALCULATION
        # -------------------------------------------------

        for index, row in df.iterrows():

            amount = float(
                row["amount"]
            )

            ratio = (
                amount /
                median_amount
            )

            risk_score = 0

            reasons = []

            if ratio >= 20:

                risk_score += 85

                reasons.append(
                    "Amount is extremely higher "
                    "than the typical transaction."
                )

            elif ratio >= 10:

                risk_score += 70

                reasons.append(
                    "Amount is significantly higher "
                    "than normal spending."
                )

            elif ratio >= 5:

                risk_score += 50

                reasons.append(
                    "Amount is much higher "
                    "than the typical transaction."
                )

            elif ratio >= 3:

                risk_score += 30

                reasons.append(
                    "Amount is above the usual "
                    "spending pattern."
                )

            if index in ml_predictions:

                if ml_predictions[index] == -1:

                    risk_score += 15

                    reasons.append(
                        "Machine learning detected "
                        "an unusual pattern."
                    )

            risk_score = min(
                risk_score,
                100
            )

            if risk_score >= 75:

                level = "🔴 HIGH RISK"

            elif risk_score >= 40:

                level = "🟡 SUSPICIOUS"

            else:

                level = "🟢 NORMAL"

            if not reasons:

                reasons.append(
                    "Transaction is within "
                    "the normal spending range."
                )

            results.append({
                "id": int(row["id"]),
                "risk_score": risk_score,
                "risk_level": level,
                "reason": " ".join(reasons)
            })

        risk_df = pd.DataFrame(
            results
        )

        high_risk = risk_df[
            risk_df["risk_score"] >= 75
        ]

        suspicious = risk_df[
            risk_df["risk_score"] >= 40
        ]

        normal = risk_df[
            risk_df["risk_score"] < 40
        ]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🔴 High Risk",
                len(high_risk)
            )

        with col2:

            st.metric(
                "🟡 Suspicious",
                len(suspicious)
            )

        with col3:

            st.metric(
                "🟢 Normal",
                len(normal)
            )

        st.markdown("---")

        if not suspicious.empty:

            for _, risk in suspicious.iterrows():

                transaction = df[
                    df["id"] ==
                    risk["id"]
                ].iloc[0]

                if risk["risk_score"] >= 75:

                    st.error(
                        f"🔴 HIGH RISK — "
                        f"Risk Score: "
                        f"{risk['risk_score']}%"
                    )

                else:

                    st.warning(
                        f"🟡 SUSPICIOUS — "
                        f"Risk Score: "
                        f"{risk['risk_score']}%"
                    )

                st.write(
                    f"💰 **Amount:** "
                    f"₹{transaction['amount']:,.2f}"
                )

                st.write(
                    f"🏷️ **Category:** "
                    f"{transaction['category']}"
                )

                st.write(
                    f"💳 **Payment:** "
                    f"{transaction['payment_method']}"
                )

                st.write(
                    f"📅 **Date:** "
                    f"{transaction['transaction_date'].strftime('%Y-%m-%d')}"
                )

                st.write(
                    f"💡 **Reason:** "
                    f"{risk['reason']}"
                )

                st.markdown("---")

        else:

            st.success(
                "🟢 No suspicious transactions detected."
            )

    else:

        st.info(
            "Add at least 2 transactions "
            "to enable fraud detection."
        )


# =========================================================
# BUDGET & INSIGHTS
# =========================================================

elif page == "💰 Budget & Insights":

    st.header("💰 Budget & Spending Insights")

    budget_row = cursor.execute("""
    SELECT monthly_budget
    FROM settings
    WHERE id = 1
    """).fetchone()

    monthly_budget = float(
        budget_row[0]
    )

    col1, col2 = st.columns([2, 1])

    with col1:

        new_budget = st.number_input(
            "Set Monthly Budget (₹)",
            min_value=1000.0,
            value=monthly_budget,
            step=1000.0
        )

    with col2:

        st.write("")
        st.write("")

        if st.button(
            "💾 Update Budget",
            use_container_width=True
        ):

            cursor.execute("""
            UPDATE settings
            SET monthly_budget = ?
            WHERE id = 1
            """, (new_budget,))

            conn.commit()

            st.success(
                "Budget updated!"
            )

            st.rerun()

    current_month = date.today().strftime(
        "%Y-%m"
    )

    if not df.empty:

        current_month_df = df[
            df["transaction_date"]
            .dt.strftime("%Y-%m")
            == current_month
        ]

    else:

        current_month_df = pd.DataFrame()

    if not current_month_df.empty:

        monthly_spending = float(
            current_month_df["amount"].sum()
        )

    else:

        monthly_spending = 0

    remaining_budget = (
        monthly_budget -
        monthly_spending
    )

    if monthly_budget > 0:

        budget_percentage = (
            monthly_spending /
            monthly_budget
        ) * 100

    else:

        budget_percentage = 0

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Monthly Budget",
            f"₹{monthly_budget:,.0f}"
        )

    with col2:

        st.metric(
            "💸 Spent",
            f"₹{monthly_spending:,.0f}"
        )

    with col3:

        st.metric(
            "💵 Remaining",
            f"₹{remaining_budget:,.0f}"
        )

    with col4:

        st.metric(
            "📊 Budget Used",
            f"{budget_percentage:.1f}%"
        )

    st.progress(
        min(
            budget_percentage / 100,
            1.0
        )
    )

    if budget_percentage >= 100:

        st.error(
            "🚨 Budget exceeded!"
        )

    elif budget_percentage >= 80:

        st.warning(
            "⚠️ You have used more than 80% "
            "of your budget."
        )

    else:

        st.success(
            "🟢 You are currently within budget."
        )

    st.markdown("---")

    st.subheader("💡 Spending Insights")

    if not current_month_df.empty:

        category_spending = (
            current_month_df
            .groupby("category")["amount"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        top_category = (
            category_spending.index[0]
        )

        top_category_amount = float(
            category_spending.iloc[0]
        )

        average_transaction = float(
            current_month_df["amount"].mean()
        )

        transaction_count = len(
            current_month_df
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.info(
                f"🏷️ **Top Category**\n\n"
                f"**{top_category}**\n\n"
                f"₹{top_category_amount:,.2f}"
            )

        with col2:

            st.info(
                f"📊 **Average Transaction**\n\n"
                f"₹{average_transaction:,.2f}"
            )

        with col3:

            st.info(
                f"🧾 **Transactions This Month**\n\n"
                f"{transaction_count}"
            )

        if budget_percentage >= 80:

            st.warning(
                "💡 Your spending is approaching "
                "the monthly budget limit."
            )

        elif top_category_amount > (
            monthly_spending * 0.50
        ):

            st.warning(
                f"💡 More than 50% of your spending "
                f"is in {top_category}."
            )

        else:

            st.success(
                "💡 Your spending is reasonably "
                "distributed across categories."
            )

    else:

        st.info(
            "Add transactions to generate insights."
        )


# =========================================================
# DATA MANAGEMENT
# =========================================================

elif page == "📁 Data Management":

    st.header("📁 Data Management")

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # IMPORT
    # -----------------------------------------------------

    with col1:

        st.subheader("📥 Import CSV")

        uploaded_file = st.file_uploader(
            "Upload transaction CSV",
            type=["csv"]
        )

        if uploaded_file is not None:

            try:

                imported_df = pd.read_csv(
                    uploaded_file
                )

                required_columns = [
                    "transaction_date",
                    "amount",
                    "category",
                    "payment_method",
                    "description"
                ]

                missing_columns = [
                    column
                    for column in required_columns
                    if column not in imported_df.columns
                ]

                if missing_columns:

                    st.error(
                        "Missing columns: "
                        + ", ".join(
                            missing_columns
                        )
                    )

                else:

                    st.success(
                        f"{len(imported_df)} rows detected."
                    )

                    st.dataframe(
                        imported_df.head(10),
                        use_container_width=True
                    )

                    if st.button(
                        "📥 Import into FINSEC AI",
                        use_container_width=True
                    ):

                        imported_count = 0

                        for _, row in imported_df.iterrows():

                            try:

                                amount = float(
                                    row["amount"]
                                )

                                if amount <= 0:
                                    continue

                                cursor.execute("""
                                INSERT INTO transactions
                                (
                                    transaction_date,
                                    amount,
                                    category,
                                    payment_method,
                                    description
                                )
                                VALUES (?, ?, ?, ?, ?)
                                """, (
                                    str(
                                        row["transaction_date"]
                                    ),
                                    amount,
                                    str(
                                        row["category"]
                                    ),
                                    str(
                                        row["payment_method"]
                                    ),
                                    str(
                                        row["description"]
                                    )
                                ))

                                imported_count += 1

                            except (
                                ValueError,
                                TypeError
                            ):
                                continue

                        conn.commit()

                        st.success(
                            f"✅ {imported_count} "
                            f"transactions imported!"
                        )

                        st.rerun()

            except Exception as e:

                st.error(
                    f"Could not read CSV: {e}"
                )

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    with col2:

        st.subheader("📤 Export CSV")

        export_df = pd.read_sql_query(
            """
            SELECT
                transaction_date,
                amount,
                category,
                payment_method,
                description
            FROM transactions
            ORDER BY id DESC
            """,
            conn
        )

        if not export_df.empty:

            csv_data = export_df.to_csv(
                index=False
            )

            st.write(
                f"📊 {len(export_df)} "
                f"transactions available"
            )

            st.download_button(
                "📤 Download CSV",
                data=csv_data,
                file_name="finsec_transactions.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:

            st.info(
                "No transactions available."
            )

    st.markdown("---")

    st.subheader("📄 CSV Format")

    st.code(
        """transaction_date,amount,category,payment_method,description
2026-08-20,500,Food,UPI,Lunch
2026-08-20,2500,Shopping,UPI,Clothes
2026-08-20,1200,Travel,Credit Card,Cab
2026-08-20,3000,Bills,Net Banking,Electricity""",
        language="csv"
    )


# =========================================================
# ABOUT
# =========================================================

elif page == "ℹ️ About":

    st.header("ℹ️ About FINSEC AI")

    st.markdown(
        """
        ## 💰 FINSEC AI

        **Smart Expense & Fraud Detection System**

        FINSEC AI is a Python-based financial analytics
        application designed to help users monitor expenses,
        manage budgets and identify unusual transactions.

        ### 🚀 Key Technologies

        - Python
        - Streamlit
        - SQLite
        - Pandas
        - Plotly
        - Scikit-learn
        - Isolation Forest

        ### ⭐ Features

        - Expense tracking
        - Monthly budget management
        - Financial dashboard
        - Spending insights
        - Transaction filtering
        - CSV import/export
        - Anomaly detection
        - Risk scoring
        - Transaction history

        ### 👨‍💻 Developer

        **Sahil Suman**

        B.Tech CSE — Artificial Intelligence

        """

    )

    st.success(
        "FINSEC AI is a portfolio project "
        "focused on financial analytics and anomaly detection."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "💰 FINSEC AI • Smart Expense & Fraud Detection System • "
    "Developed by Sahil Suman"
)