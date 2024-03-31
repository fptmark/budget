import argparse
import pandas as pd
import sys
import matplotlib.pyplot as plt

def pie(start_month, end_month, exclude_descrs, exclude_cats, data_file, category_column, details_category, credit):

    trans_type = "CREDIT" if credit else "DEBIT"

    # Load the data
    data = pd.read_csv(data_file, parse_dates=['Posting Date'])

    # Remove all income
    data = data[data['Details'] == trans_type]

    # Convert posting dates to datetime objects and filter within the year 2024 and the specified month range
    data = data[data['Posting Date'].dt.year == 2024]
    data = data[(data['Posting Date'].dt.month >= start_month) & (data['Posting Date'].dt.month <= end_month)]

    # Exclude transactions related to descriptions in exclude_descr
    for exclude in exclude_descrs:
        data = data[~data['Description'].str.contains(exclude, case=False, na=False)]

    # Exclude transactions related to categories in exclude_cats
    for exclude in exclude_cats:
        data = data[~data[category_column].str.contains(exclude, case=False, na=False)]

    # Convert 'Amount' to a numeric type, coercing errors to NaN (then dropping them)
    data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce')
    data.dropna(subset=['Amount'], inplace=True)

    # Aggregate the data by category
    category_totals = data.groupby(category_column)['Amount'].sum().abs()

    # Compute the total amount
    total_amount = category_totals.sum()

    # generate the title
    title =f'\n\n{trans_type} from {start_month}/2024 to {end_month}/2024'
    excludes = build_string("Excl Descr", exclude_descrs) + " " + build_string("Excl Cats", exclude_cats)
    if len(excludes) > 1:
        title += '\n  ' + excludes
    title += f'\nTotal: ${total_amount:,.0f}'

     # Create the legend labels including the category, percentage, and amount (excluding cents)
    legend_labels = [f'{cat}: {amt/total_amount:.1%} (${int(amt)})' for cat, amt in category_totals.items()]

    # Plot
    plt.subplot(1, 2, 1 if credit else 2)  # column 1 for credit/income, 2 for debit/expenses
    wedges, texts = plt.pie(category_totals, labels=category_totals.index, startangle=140, autopct=None, labeldistance=0.7, radius=0.7)
    plt.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False, fontsize="small")
    plt.title(title)
    plt.axis('equal')

    # Show details for category if requested
    if details_category is not None:
        for category in details_category:
            total = 0
            for _, row in data[data[category_column] == category].iterrows():
                print(row['Posting Date'].date(), row['Description'], "$", -row['Amount'])
                total += row['Amount']
            print("Total = $", -total)

def get_list(arg) :
    values = []
    if arg:
        for value in arg[0].split(','):
            values.append(value.strip())
    return values

def build_string(label, values):
    if values:
        joined_values = " & ".join(f"'{value}'" for value in values)
        return f"{label}: {joined_values}"
    else:
        return ''
    
# Define the parameters for the pie chart
parser = argparse.ArgumentParser(description='Analyze expenses')
parser.add_argument('--start', nargs=1,  metavar=('starting month #'))
parser.add_argument('--end', nargs=1,  metavar=('ending month #'))
parser.add_argument('--data', nargs=1,  metavar=('csv data file'))
parser.add_argument('--details', nargs=1,  metavar=('show details for category'))
parser.add_argument('--ex_desc', nargs=1,  metavar=('list of comma seperated descriptions to exclude'))
parser.add_argument('--ex_cat', nargs=1,  metavar=('list of comma seperated categories to exclude'))
parser.add_argument('--nopie', action='store_true', help='no pie chart')


try:
    args = parser.parse_args()
except:
    sys.exit(0)

start_month = 1 if args.start is None else int(args.start[0])
end_month = start_month if args.end is None else int(args.end[0])
data_file = 'data.csv' if args.data is None else args.data[0]

exclude_descs = get_list(args.ex_desc)
exclude_cats = get_list(args.ex_cat)

# Call the pie chart function
plt.figure(figsize=(20, 10))

pie(start_month, end_month, exclude_descs, exclude_cats, data_file, 'Category', args.details, credit=True)
pie(start_month, end_month, exclude_descs, exclude_cats, data_file, 'Category', args.details, credit=False)

# Display the pie chart
if not args.nopie:
    # Adjust layout to make room for the legends
    plt.subplots_adjust(right=0.85, left=0.00, wspace=0.5)
    plt.show()

