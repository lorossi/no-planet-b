import plotly.express as px
import pandas as pd


def plot_set_layout(fig):
    fig.update_layout(
        font={
            "family": "Gilroy",
            "size": 18,
        },
        title={
            "text": "Temperature anomalies over the years",
            "y": 0.99,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )


def main():
    df = pd.read_csv("dataset/1880-2021.csv")
    df["Datetime"] = pd.to_datetime(df["Year"], format="%Y%m")

    labels = {
        "Datetime": "Date",
        "Value": "Anomaly",
        "count": "Occasions"
    }

    fig = px.histogram(
        df, x="Value",
        labels=labels,
    )
    plot_set_layout(fig)
    fig.show()

    fig = px.density_heatmap(
        df, x="Datetime", y="Value",
        nbinsx=100,
        nbinsy=100,
        labels=labels
    )
    plot_set_layout(fig)
    fig.show()

    fig = px.scatter(
        df, x="Datetime", y="Value", color="Value",
        color_continuous_scale=["blue", "red"],
        trendline="lowess",
        trendline_options=dict(frac=0.25),
        trendline_color_override="red",
        labels=labels

    )
    plot_set_layout(fig)
    fig.show()


if __name__ == "__main__":
    main()
