import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "products"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='products', ascending=False)

    return sum_order_items_df

def create_most_product_df(df):
    most_product_df = df.groupby('product_category_name_english').agg({
        'order_id': 'count'
    }).rename(columns={'order_id': 'order_count'}).reset_index()

    most_product_df = most_product_df.sort_values(by='order_count', ascending=False)

    return most_product_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bystate_df

def create_most_seller_df(df):
    most_seller_df = df.groupby('seller_city').aggregate({'order_id': 'count'}).rename(columns={'order_id': 'order_count'}).sort_values(by='order_count', ascending=False).reset_index()
    return most_seller_df

def create_rfm_df(df):
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], errors='coerce')
    df = df.dropna(subset=['order_approved_at'])
    
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_approved_at": "max",  
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]) 
    recent_date = df["order_approved_at"].max() 
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days 
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Membaca data
all_df = pd.read_csv("dashboard/all_df.csv")

# Mengkonversi kolom tanggal
datetime_columns = ["order_approved_at", "order_purchase_timestamp", "order_delivered_carrier_date",
                    "order_delivered_customer_date", "order_estimated_delivery_date"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Mengurutkan dan mereset index
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar Streamlit
with st.sidebar:
    st.header("Keysya AZ")
    st.image("dashboard/logo.png")
    
    start_date, end_date = st.date_input(
        label='Range Time', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memfilter DataFrame berdasarkan tanggal
main_df = all_df[(all_df["order_approved_at"] >= pd.Timestamp(start_date)) & 
                  (all_df["order_approved_at"] <= pd.Timestamp(end_date))]

# Memanggil fungsi untuk membuat DataFrame
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
most_product_df = create_most_product_df(main_df)
bystate_df = create_bystate_df(main_df)
most_seller_df = create_most_seller_df(main_df) 
rfm_df = create_rfm_df(main_df)

# Menampilkan dashboard
st.header('E-Commerce Dashboard:sparkles:')
st.subheader("Daily Orders")

col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#624E88"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_title("Daily Orders", fontsize=30)
st.pyplot(fig)

# Produk Paling Laku dan tidak Laku
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#624E88", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="products", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors[:5], ax=ax[0])
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="products", y="product_category_name_english", data=sum_order_items_df.sort_values(by="products", ascending=True).head(5), palette=colors[:5], ax=ax[1])
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Produk yang sering sold
st.subheader("Most Sold Products")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y="product_category_name_english", x="order_count", data=most_product_df[:10], color="#624E88", ax=ax)
ax.set_title("Most Sold Products", loc="center", fontsize=30)
ax.set_ylabel("Category Product")
ax.set_xlabel("Number of Orders")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)

# Customer Demografis 
st.subheader("Customer Demographics")

fig, ax = plt.subplots(figsize=(20, 10))
most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df,
    palette=["#624E88" if state == most_common_state else "#D3D3D3" for state in bystate_df['customer_state']]
)

ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel("State")
ax.set_xlabel("Number of Customers")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)

# Seller kota mana yang penjualannya terbanyak
st.subheader("Most Seller City")
most_seller_df = all_df['seller_city'].value_counts()[:5]

plt.figure(figsize=(18, 6))
colors = ["#624E88", "#E5D9F2", "#E5D9F2", "#E5D9F2", "#E5D9F2"]
ax = sns.barplot(x=most_seller_df.index, y=most_seller_df.values, palette=colors)

ax.set_title("Most Seller City", fontsize=30)
ax.set_xlabel("City", fontsize=16)
ax.set_ylabel("Number of Order", fontsize=16)

for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
                (p.get_x() + p.get_width() / 2, p.get_height()), 
                ha='center', va='bottom', fontsize=12, color='black')

st.pyplot(plt)


# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#624E88"] * 5  # Use the same color for all bars

# Plotting Recency
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("Recency (days)", fontsize=18)
ax[0].set_xlabel("Customer ID", fontsize=18)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)
ax[0].set_xticklabels([])  # Remove x-tick labels if needed

# Plotting Frequency
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel("Frequency", fontsize=18)
ax[1].set_xlabel("Customer ID", fontsize=18)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].set_xticklabels([])

# Plotting Monetary
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel("Monetary Value", fontsize=18)
ax[2].set_xlabel("Customer ID", fontsize=18)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].set_xticklabels([])

st.pyplot(fig)

st.caption('Copyright (c) Keysya Alifia Zabina')
