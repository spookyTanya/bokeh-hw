from bokeh.plotting import figure, show, output_file, save
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup, CustomJS, FactorRange
from bokeh.layouts import column
import pandas as pd


pd.set_option('display.max.columns', 20)


def data_prep() -> pd.DataFrame:
    data = pd.read_csv('Titanic-Dataset.csv')

    data['Age'] = data['Age'].fillna(data['Age'].mean())
    data['Cabin'] = data['Cabin'].fillna('Unknown')
    data['Embarked'] = data['Embarked'].fillna('Unknown')

    data['AgeGroup'] = data['Age'].apply(lambda x: 'Child' if x < 18 else ('Young Adult' if x < 27 else ('Adult' if x < 65 else 'Senior')))

    rates = data.groupby('AgeGroup')['Survived'].mean()
    data['SurvivalRate'] = data['AgeGroup'].map(rates)
    return data


def age_group_survival(data: pd.DataFrame):
    grouped = data.groupby('AgeGroup').agg({
        'SurvivalRate': 'mean'
    }).reset_index()

    colors = {
        'Child': '#34344A',
        'Young Adult': '#80475E',
        'Adult': '#A3E7FC',
        'Senior': '#EDCB96'
    }

    grouped['Color'] = grouped['AgeGroup'].map(colors)

    source = ColumnDataSource(grouped)

    p = figure(
        title='Survival rates across age groups',
        x_axis_label='Age groups',
        y_axis_label='Survival Rate',
        x_range=grouped['AgeGroup'],
        tools=[HoverTool()],
        tooltips="Survival rate of @AgeGroup group is @SurvivalRate",
    )

    p.vbar(x='AgeGroup', top='SurvivalRate', legend_field='AgeGroup', width=0.5, bottom=0, color='Color', source=source)

    checkbox_group = CheckboxGroup(labels=list(data['AgeGroup'].unique()), active=list(range(len(data['AgeGroup'].unique()))))
    callback = CustomJS(args=dict(source=source, original_source=source.data, p=p, checkbox_group=checkbox_group), code='''
            var active = checkbox_group.active.map(i => checkbox_group.labels[i]);
            var original_data = original_source;
            var new_data = { 'AgeGroup': [], 'SurvivalRate': [], 'Color': [] };

            for (var i = 0; i < original_data['AgeGroup'].length; i++) {
                if (active.includes(original_data['AgeGroup'][i])) {
                    new_data['AgeGroup'].push(original_data['AgeGroup'][i]);
                    new_data['SurvivalRate'].push(original_data['SurvivalRate'][i]);
                    new_data['Color'].push(original_data['Color'][i]);
                }
            }

            source.data = new_data;
            p.x_range.factors = new_data['AgeGroup'];
            source.change.emit();
    ''')

    checkbox_group.js_on_change('active', callback)
    layout = column(checkbox_group, p)
    show(layout)

    p.ygrid.band_fill_color = "#65743A"
    p.ygrid.band_fill_alpha = 0.1
    p.xgrid.bounds = (2, 4)

    output_file(filename="task1.html", title="task 1")
    save(layout)


def class_and_gender(data: pd.DataFrame):
    grouped = data.groupby(['Pclass', 'Sex']).agg({
        'SurvivalRate': 'mean'
    }).reset_index()

    color_map = {'female': '#CEB1BE', 'male': '#A3E7FC'}
    grouped['Color'] = grouped['Sex'].map(color_map)

    pclass_values = sorted(grouped['Pclass'].unique())
    sex_values = sorted(grouped['Sex'].unique())
    factors = [(str(pclass), sex) for pclass in pclass_values for sex in sex_values]

    grouped['Pclass_Sex'] = list(map(lambda x: (str(x[0]), x[1]), zip(grouped['Pclass'], grouped['Sex'])))

    source = ColumnDataSource(grouped)

    p = figure(
        title='Survival Rates by Class and Gender',
        x_axis_label='Pclass - Sex',
        y_axis_label='Survival Rate',
        x_range=FactorRange(*factors),
        tools=[HoverTool()],
        tooltips="Survival rate for @Sex from @Pclass class is @SurvivalRate"
    )

    p.vbar(
        x='Pclass_Sex',
        top='SurvivalRate',
        source=source,
        color='Color',
        width=0.4,
        line_color="white"
    )

    checkbox_group = CheckboxGroup(labels=list(data['Sex'].unique()), active=list(range(len(data['Sex'].unique()))))
    callback = CustomJS(args=dict(source=source, original_source=source.data, p=p, checkbox_group=checkbox_group), code='''
               var active = checkbox_group.active.map(i => checkbox_group.labels[i]);
               var original_data = original_source;
               var new_data = { 'Pclass_Sex': [], 'SurvivalRate': [], 'Color': [], 'Sex': [], 'Pclass': [] };

               for (var i = 0; i < original_data['Sex'].length; i++) {
                   if (active.includes(original_data['Sex'][i])) {
                       new_data['Pclass_Sex'].push(original_data['Pclass_Sex'][i]);
                       new_data['SurvivalRate'].push(original_data['SurvivalRate'][i]);
                       new_data['Color'].push(original_data['Color'][i]);
                       new_data['Sex'].push(original_data['Sex'][i]);
                       new_data['Pclass'].push(original_data['Pclass'][i]);
                   }
               }

               source.data = new_data;
               p.x_range.factors = new_data['Pclass_Sex'];
               source.change.emit();
       ''')

    checkbox_group.js_on_change('active', callback)
    layout = column(checkbox_group, p)
    show(layout)

    output_file(filename="task2.html", title="task 2")
    save(layout)


def fare_survival(data: pd.DataFrame):
    p = figure(width=400, height=400, title="Fare vs. Survival Status by Class", x_axis_label='Fare', y_axis_label='Survival Rate')

    colors = {
        1: '#FFC857',
        2: '#2E4052',
        3: '#B9314F'
    }

    for pclass in data['Pclass'].sort_values().unique():
        filtered = data[data['Pclass'] == pclass]
        grouped = filtered.groupby('Fare').agg({
            'SurvivalRate': 'mean'
        }).reset_index()
        grouped['ClassName'] = f"{pclass} Class"
        source = ColumnDataSource(grouped)

        p.scatter(
            x='Fare',
            y='SurvivalRate',
            source=source,
            alpha=0.8,
            legend_label=f"Class {pclass}",
            color=colors.get(pclass),
            size=8)

    p.add_tools(HoverTool(tooltips=[
        ("Fare", "@Fare"),
        ("Survival Rate", "@SurvivalRate"),
        ("Class", "@ClassName")
    ]))

    show(p)

    output_file(filename="task3.html", title="task 3")
    save(p)


# 1
titanic_data = data_prep()
print(titanic_data.head())

# 2
age_group_survival(titanic_data)
class_and_gender(titanic_data)
fare_survival(titanic_data)
