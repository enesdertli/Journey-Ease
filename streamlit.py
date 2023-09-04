import streamlit as st
import pandas as pd
import numpy as np

df1 = pd.DataFrame(
   np.random.randn(10, 10),
   columns=('col %d' % i for i in range(10)))

my_table = st.table(df1)
st.divider()

df2 = pd.DataFrame(
   np.random.randn(10, 10),
   columns=('col %d' % i for i in range(10)))

# Assuming df1 and df2 from the example above still exist...
my_chart = st.line_chart(df1)
my_chart.add_rows(df2)
# Now the chart shown in the Streamlit app contains the data for
# df1 followed by the data for df2.
# Now the table shown in the Streamlit app contains the data for
# df1 followed by the data for df2.