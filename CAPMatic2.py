import streamlit as st # type: ignore
import pandas as pd
import plotly.graph_objects as go # type: ignore

# Data yang sama dari file asli
indices = [
    "ASX 200", "CAC 40", "CSI 300", "DAX", "FTSE 100",
    "HSI", "IDX Composite", "KOSPI", "NIKKEI 225", "S&P 500"
]

# Add the expected return data
expected_returns = {
    "ASX 200": {"3_months": 0.088711049, "6_months": 0.184687669, "1_year": 0.400846687},
    "CAC 40": {"3_months": 0.081490585, "6_months": 0.169598312, "1_year": 0.367857255},
    "CSI 300": {"3_months": 0.113100985, "6_months": 0.235657864, "1_year": 0.512281377},
    "DAX": {"3_months": 0.083353539, "6_months": 0.17349152, "1_year": 0.376368866},
    "FTSE 100": {"3_months": 0.069311188, "6_months": 0.144145753, "1_year": 0.31221105},
    "HSI": {"3_months": 0.080845148, "6_months": 0.168249474, "1_year": 0.36490833},
    "IDX Composite": {"3_months": 0.063065897, "6_months": 0.131094315, "1_year": 0.283677062},
    "KOSPI": {"3_months": 0.094934805, "6_months": 0.197694102, "1_year": 0.429282282},
    "NIKKEI 225": {"3_months": 0.070774195, "6_months": 0.147203152, "1_year": 0.318895353},
    "S&P 500": {"3_months": 0.067052231, "6_months": 0.139424975, "1_year": 0.301890146}
}

data_6m = {
    "ASX 200":       {"capm": 0.1846876688037084, "p": 0.5308},
    "CAC 40":        {"capm": 0.16959831188935687, "p": 0.4886},
    "CSI 300":       {"capm": 0.2356578644530229,  "p": 0.5230},
    "DAX":           {"capm": 0.17349152032188458, "p": 0.5095},
    "FTSE 100":      {"capm": 0.14414575331498228, "p": 0.4917},
    "HSI":           {"capm": 0.16824947417296285, "p": 0.3629},
    "IDX Composite": {"capm": 0.13109431524472048, "p": 0.5290},
    "KOSPI":         {"capm": 0.19769410180178457, "p": 0.4117},
    "NIKKEI 225":    {"capm": 0.1472031516218701,  "p": 0.6274},
    "S&P 500":       {"capm": 0.13942497472444942, "p": 0.9975},
}

def create_expected_returns_chart():
    fig = go.Figure()
    
    # Add traces for each period
    periods = ["3_months", "6_months", "1_year"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # Different color for each period
    
    for period, color in zip(periods, colors):
        values = [expected_returns[idx][period] * 100 for idx in indices]  # Convert to percentage
        fig.add_trace(go.Bar(
            name=period.replace('_', ' ').title(),
            x=indices,
            y=values,
            marker_color=color
        ))

    fig.update_layout(
        title="Expected Returns by Period",
        xaxis_title="Indices",
        yaxis_title="Expected Return (%)",
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def compute_weights(chosen_indices):
    fused = {}
    for idx in chosen_indices:
        capm = data_6m[idx]["capm"]
        p = data_6m[idx]["p"]
        fused[idx] = capm * p

    total = sum(fused.values())
    weights = {idx: v / total for idx, v in fused.items()}
    
    return fused, weights

def create_pie_chart(weights):
    fig = go.Figure(data=[go.Pie(
        labels=list(weights.keys()),
        values=[w * 100 for w in weights.values()],
        hole=.3,
        textinfo='label+percent',
        textposition='inside'
    )])
    fig.update_layout(
        title="Portfolio Weight Distribution",
        showlegend=False
    )
    return fig

def main():
    st.set_page_config(page_title="Portfolio Weight Calculator", layout="wide")
    
    # Header with custom styling
    st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        color: #1E88E5;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-font">Portfolio Weight Calculator</p>', unsafe_allow_html=True)
    
    st.write("---")

    # Display the expected returns chart before the selection
    st.subheader("Expected Returns Overview")
    expected_returns_fig = create_expected_returns_chart()
    st.plotly_chart(expected_returns_fig, use_container_width=True)
    
    st.write("---")

    # Sidebar for index selection
    st.sidebar.header("Select Indices")
    selected_indices = st.sidebar.multiselect(
        "Choose your indices:",
        indices,
        default=["S&P 500", "NIKKEI 225"]
    )

    if selected_indices:
        fused, weights = compute_weights(selected_indices)
        
        # Create three columns for the main content
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Portfolio Analysis Results")
            
            # Create a DataFrame for better display
            results_data = []
            for idx in selected_indices:
                results_data.append({
                    "Index": idx,
                    "CAPM_6m": round(data_6m[idx]["capm"], 6),
                    "Probability Up": round(data_6m[idx]["p"], 4),
                    "Fused E[R]": round(fused[idx], 6),
                    "Weight (%)": round(weights[idx] * 100, 2)
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df.style.format({
                'CAPM_6m': '{:.6f}',
                'Probability Up': '{:.4f}',
                'Fused E[R]': '{:.6f}',
                'Weight (%)': '{:.2f}'
            }))

        with col2:
            st.subheader("Weight Distribution")
            fig = create_pie_chart(weights)
            st.plotly_chart(fig)

        # Additional metrics
        st.write("---")
        st.subheader("Portfolio Metrics")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            total_weight = sum(weights.values()) * 100
            st.metric("Total Weight", f"{total_weight:.2f}%")
        
        with metrics_col2:
            avg_capm = sum(data_6m[idx]["capm"] for idx in selected_indices) / len(selected_indices)
            st.metric("Average CAPM", f"{avg_capm:.4f}")
        
        with metrics_col3:
            avg_prob = sum(data_6m[idx]["p"] for idx in selected_indices) / len(selected_indices)
            st.metric("Average Probability Up", f"{avg_prob:.4f}")

    else:
        st.warning("Please select at least one index from the sidebar.")

if __name__ == "__main__":
    main()

