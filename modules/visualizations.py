
import pandas as pd
import plotly.express as px


def recommend_charts(df):
    """
    Automatically identify useful charts
    based on the uploaded dataset.
    """

    recommendations = []

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    date_columns = []

    # Detect date columns
    for column in df.columns:

        if (
            pd.api.types.is_datetime64_any_dtype(df[column])
            or "date" in str(column).lower()
            or "time" in str(column).lower()
        ):
            date_columns.append(column)

    # 1. Categorical vs numerical: Bar chart
    if categorical_columns and numeric_columns:

        recommendations.append({
            "type": "bar",
            "title": "Category-wise Analysis",
            "x": categorical_columns[0],
            "y": numeric_columns[0]
        })

    # 2. Date vs numerical: Line chart
    if date_columns and numeric_columns:

        recommendations.append({
            "type": "line",
            "title": "Trend Analysis",
            "x": date_columns[0],
            "y": numeric_columns[0]
        })

    # 3. Categorical distribution: Pie chart
    if categorical_columns:

        recommendations.append({
            "type": "pie",
            "title": "Category Distribution",
            "x": categorical_columns[0]
        })

    # 4. Numerical distribution: Histogram
    if numeric_columns:

        recommendations.append({
            "type": "histogram",
            "title": "Numerical Distribution",
            "x": numeric_columns[0]
        })

    # 5. Numerical relationship: Scatter plot
    if len(numeric_columns) >= 2:

        recommendations.append({
            "type": "scatter",
            "title": "Relationship Analysis",
            "x": numeric_columns[0],
            "y": numeric_columns[1]
        })

    return recommendations


def create_chart(df, recommendation):

    chart_type = recommendation["type"]

    if chart_type == "bar":

        column = recommendation["x"]
        value = recommendation["y"]

        chart_data = (
            df.groupby(column, dropna=False)[value]
            .sum()
            .reset_index()
            .sort_values(value, ascending=False)
            .head(30)
        )

        fig = px.bar(
            chart_data,
            x=column,
            y=value,
            title=recommendation["title"],
            text_auto=True
        )

    elif chart_type == "line":

        column = recommendation["x"]
        value = recommendation["y"]

        chart_data = df[[column, value]].copy()

        chart_data[column] = pd.to_datetime(
            chart_data[column],
            errors="coerce"
        )

        chart_data = (
            chart_data.dropna()
            .groupby(column)[value]
            .sum()
            .reset_index()
            .sort_values(column)
        )

        fig = px.line(
            chart_data,
            x=column,
            y=value,
            title=recommendation["title"],
            markers=True
        )

    elif chart_type == "pie":

        column = recommendation["x"]

        chart_data = (
            df[column]
            .fillna("Missing")
            .value_counts()
            .head(10)
            .reset_index()
        )

        chart_data.columns = [column, "Count"]

        fig = px.pie(
            chart_data,
            names=column,
            values="Count",
            title=recommendation["title"]
        )

    elif chart_type == "histogram":

        column = recommendation["x"]

        fig = px.histogram(
            df,
            x=column,
            title=recommendation["title"],
            nbins=30
        )

    elif chart_type == "scatter":

        fig = px.scatter(
            df,
            x=recommendation["x"],
            y=recommendation["y"],
            title=recommendation["title"]
        )

    else:
        return None

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig
