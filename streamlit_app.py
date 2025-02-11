import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Constants for GCP Storage pricing (euros)
GCP_STORAGE_PRICES = {
    "standard": 0.0203,  # per GB/month
    "nearline": 0.01,
    "coldline": 0.004,
    "archive": 0.0012
}

GCP_RETRIEVAL_PRICES = {
    "nearline": 0.01,
    "coldline": 0.02,
    "archive": 0.05
}

GCP_OPERATION_PRICES = {
    "class_a": 0.05 / 10000,  # per 10,000 operations
    "class_b": 0.004 / 10000
}

# Constants for AWS S3 pricing (euros)
AWS_STORAGE_PRICES = {
    "standard": 0.024,
    "ia": 0.0125,
    "glacier_ir": 0.004,
    "glacier": 0.004,
    "deep_archive": 0.00099
}

AWS_RETRIEVAL_PRICES = {
    "ia": 0.01,
    "glacier_ir": 0.03,
    "glacier": 0.03,
    "deep_archive": 0.05
}

AWS_OPERATION_PRICES = {
    "put": 0.005 / 1000,  # per 1,000 requests
    "get": 0.0004 / 1000,
    "lifecycle": 0.0 
}

def calculate_gcp_costs(storage_gb, storage_class, transfer_out_gb, get_requests, put_requests):
    # Storage cost
    storage_cost = storage_gb * GCP_STORAGE_PRICES[storage_class]
    
    # Retrieval cost
    retrieval_cost = 0
    if storage_class in GCP_RETRIEVAL_PRICES:
        retrieval_cost = transfer_out_gb * GCP_RETRIEVAL_PRICES[storage_class]
    
    # Operation costs
    class_a_ops = put_requests  # Class A operations include PUT, POST, LIST
    class_b_ops = get_requests  # Class B operations include GET
    operation_cost = (class_a_ops * GCP_OPERATION_PRICES["class_a"] + 
                     class_b_ops * GCP_OPERATION_PRICES["class_b"])
    
    # Network egress
    network_cost = calculate_network_egress(transfer_out_gb)
    
    total_cost = storage_cost + retrieval_cost + operation_cost + network_cost
    return {
        "storage": storage_cost,
        "retrieval": retrieval_cost,
        "operations": operation_cost,
        "network": network_cost,
        "total": total_cost
    }

def calculate_aws_costs(storage_gb, storage_class, transfer_out_gb, get_requests, put_requests):
    # Storage cost
    storage_cost = storage_gb * AWS_STORAGE_PRICES[storage_class]
    
    # Retrieval cost
    retrieval_cost = 0
    if storage_class in AWS_RETRIEVAL_PRICES:
        retrieval_cost = transfer_out_gb * AWS_RETRIEVAL_PRICES[storage_class]
    
    # Operation costs
    operation_cost = (put_requests * AWS_OPERATION_PRICES["put"] + 
                     get_requests * AWS_OPERATION_PRICES["get"])
    
    # Network egress
    network_cost = calculate_network_egress(transfer_out_gb)
    
    total_cost = storage_cost + retrieval_cost + operation_cost + network_cost
    return {
        "storage": storage_cost,
        "retrieval": retrieval_cost,
        "operations": operation_cost,
        "network": network_cost,
        "total": total_cost
    }

def calculate_network_egress(gb):
    # Simplified tiered pricing for network egress
    if gb <= 1:
        return 0
    elif gb <= 10240:  # 10TB
        return gb * 0.085
    elif gb <= 51200:  # 50TB
        return 10240 * 0.085 + (gb - 10240) * 0.065
    else:
        return 10240 * 0.085 + 40960 * 0.065 + (gb - 51200) * 0.05

# Streamlit UI
st.set_page_config(page_title="Cloud Storage Cost Comparison", layout="wide")
st.title("GCP vs AWS Storage Cost Comparison")

st.markdown("""
Compare storage costs between Google Cloud Storage and Amazon S3.
Prices are shown in Euros (€).
""")

# Input parameters
with st.sidebar:
    st.header("Input Parameters")
    
    # Storage inputs
    st.subheader("Storage")
    storage_gb = st.number_input("Storage Amount (GB)", min_value=0.0, value=1000.0)
    
    # Data transfer
    st.subheader("Data Transfer")
    transfer_out_gb = st.number_input("Monthly Data Transfer Out (GB)", min_value=0.0, value=100.0)
    
    # Requests
    st.subheader("API Requests")
    get_requests = st.number_input("GET Requests per month", min_value=0, value=100000)
    put_requests = st.number_input("PUT Requests per month", min_value=0, value=10000)

# Create columns for GCP and AWS
col1, col2 = st.columns(2)

with col1:
    st.header("Google Cloud Storage")
    gcp_class = st.selectbox(
        "Storage Class",
        ["standard", "nearline", "coldline", "archive"],
        help="""
        - Standard: Frequently accessed data
        - Nearline: Once per month access
        - Coldline: Once per quarter access
        - Archive: Once per year access
        """
    )
    
    gcp_costs = calculate_gcp_costs(storage_gb, gcp_class, transfer_out_gb, get_requests, put_requests)
    
    st.write("Monthly Costs Breakdown:")
    st.write(f"Storage: €{gcp_costs['storage']:.2f}")
    st.write(f"Retrieval: €{gcp_costs['retrieval']:.2f}")
    st.write(f"Operations: €{gcp_costs['operations']:.2f}")
    st.write(f"Network Egress: €{gcp_costs['network']:.2f}")
    st.write(f"Total: €{gcp_costs['total']:.2f}")

with col2:
    st.header("Amazon S3")
    aws_class = st.selectbox(
        "Storage Class",
        ["standard", "ia", "glacier_ir", "glacier", "deep_archive"],
        help="""
        - Standard: Frequently accessed data
        - IA: Infrequent Access
        - Glacier IR: Instant Retrieval
        - Glacier: Flexible Retrieval
        - Deep Archive: Long-term storage
        """
    )
    
    aws_costs = calculate_aws_costs(storage_gb, aws_class, transfer_out_gb, get_requests, put_requests)
    
    st.write("Monthly Costs Breakdown:")
    st.write(f"Storage: €{aws_costs['storage']:.2f}")
    st.write(f"Retrieval: €{aws_costs['retrieval']:.2f}")
    st.write(f"Operations: €{aws_costs['operations']:.2f}")
    st.write(f"Network Egress: €{aws_costs['network']:.2f}")
    st.write(f"Total: €{aws_costs['total']:.2f}")

# Comparison chart
comparison_data = {
    'Cost Component': ['Storage', 'Retrieval', 'Operations', 'Network', 'Total'],
    'GCP': [
        gcp_costs['storage'],
        gcp_costs['retrieval'],
        gcp_costs['operations'],
        gcp_costs['network'],
        gcp_costs['total']
    ],
    'AWS': [
        aws_costs['storage'],
        aws_costs['retrieval'],
        aws_costs['operations'],
        aws_costs['network'],
        aws_costs['total']
    ]
}

df = pd.DataFrame(comparison_data)

fig = go.Figure(data=[
    go.Bar(name='GCP', x=df['Cost Component'], y=df['GCP']),
    go.Bar(name='AWS', x=df['Cost Component'], y=df['AWS'])
])

fig.update_layout(
    title='Cost Comparison: GCP vs AWS',
    yaxis_title='Cost (€)',
    barmode='group'
)

st.plotly_chart(fig)

# Savings analysis
total_diff = abs(gcp_costs['total'] - aws_costs['total'])
cheaper_provider = "GCP" if gcp_costs['total'] < aws_costs['total'] else "AWS"
savings_percentage = (total_diff / max(gcp_costs['total'], aws_costs['total'])) * 100

st.header("Savings Analysis")
st.write(f"{cheaper_provider} is cheaper by €{total_diff:.2f} ({savings_percentage:.1f}%)")
