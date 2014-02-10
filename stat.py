import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def compute_actual_widths(ax):
    cs = len(ax.containers)
    chperc = len(ax.containers[0].get_children())
    widths = np.zeros(cs * chperc).reshape(chperc, cs)
    for i, container in enumerate(ax.containers):
        for j, child in enumerate(container.get_children()):
            prev_width = 0
            if (i > 0):
                prev_width = widths[j][i - 1]
            widths[j][i] = prev_width + child.get_width()
    return widths


def barh(frame, title='', color='', xlabel='', ylabel='',
         format_str='%s', integer=True, legend_title='',
         figsize=(8, 6), stacked=False, hidevalue=5):

    # plot horizontal bar chart
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    frame.plot(kind='barh', ax=ax, title=title, color=color, stacked=stacked)

    # print value inside each bar
    # stacked bars need some more care
    if (stacked):
        actual_widths = compute_actual_widths(ax)

    for i, container in enumerate(ax.containers):
        for j, child in enumerate(container.get_children()):
            value = child.get_width()
            width = value
            if (stacked):
                width = actual_widths[j][i]
            if (integer):
                text = str(int(value))
            else:
                text = str(value)
            if (value < hidevalue):
                if (stacked):
                    continue
                xloc = width + 1
                text_color = 'black'
                text_ha = 'left'
            else:
                xloc = 0.98 * width
                text_color = 'white'
                text_ha = 'right'
            yloc = child.get_y() + child.get_height() / 2.0
            plt.text(xloc, yloc, format_str % text, ha=text_ha, va='center',
                     color=text_color, style='normal', weight='bold')

    # add x and y axis labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # patch long yticklabels
    yticklabels = ax.get_yticklabels()
    newlabels = [label.get_text().replace(', ', ',\n')
                 for label in yticklabels]
    ax.set_yticklabels(newlabels)

    # add legend title, if defined
    legend = ax.get_legend()
    if (legend):
        legend.set_title(legend_title)

    # save figure as a .png file
    #plt.savefig('stat1.png', bbox_inches='tight', dpi=300)


def stents_plot_basic(data, groupby,
                      dataslice=False, title='', color='m',
                      figsize=(8, 6), xlabel='', ylabel='',
                      integer=True):
    frame = data.groupby(groupby).size()
    frame.sort(axis=0, ascending=False)
    if (dataslice):
        sliced_frame = frame[dataslice[0]:dataslice[1]]
    else:
        sliced_frame = frame
    barh(frame=sliced_frame,
         title=title, color=color,
         figsize=figsize, xlabel=xlabel, ylabel=ylabel,
         integer=integer)


def stents_plot_stacked(data, groupby, sortby,
                        dataslice=False, title='', color='m',
                        figsize=(8, 6), xlabel='', ylabel='',
                        integer=True):
    frame = data.groupby(groupby).size()
    unstacked_frame = frame.unstack()
    unstacked_frame.fillna(value=0, inplace=True)
    sorted_frame = unstacked_frame.sort_index(by=sortby, ascending=False)
    if (dataslice):
        sliced_frame = sorted_frame[dataslice[0]:dataslice[1]]
    else:
        sliced_frame = sorted_frame
    barh(frame=sliced_frame,
         title=title, color=color,
         figsize=figsize, xlabel=xlabel, ylabel=ylabel,
         integer=integer, stacked=True)


def draw_impressions_chart(people):
    conductance = people['impressions.conductance'].value_counts()
    conformability = people['impressions.conformability'].value_counts()
    delivery = people['impressions.delivery'].value_counts()
    flexibility = people['impressions.flexibility'].value_counts()
    recoil = people['impressions.recoil'].value_counts()
    overall = people['impressions.overall'].value_counts()
    names = {
        0: 'проводимость',
        1: 'прилегаемость',
        2: 'система доставки',
        3: 'гибкость',
        4: 'recoil',
        5: 'общие впечатления'
    }
    impressions = pd.concat([conductance, conformability, delivery,
                            flexibility, recoil, overall],
                            axis=1)
    impressions.rename(columns=names, inplace=True)
    impressions.fillna(value=0, inplace=True)
    barh(frame=impressions[1:].transpose(),
         title=u'Впечатления', color='gryb',
         figsize=(10, 10), xlabel=u'Количество процедур стентирования',
         stacked=True, hidevalue=20)


def draw_all():

    mpl.rcParams['font.family'] = 'fantasy'
    mpl.rcParams['font.fantasy'] = 'Arial'

    path = './st.csv'
    stents = pd.read_csv(path, index_col=1, encoding='UTF-8', sep='\t')
    people = stents.groupby(level=0).first()

    # Пол
    gender = people['patient.sex'].value_counts()
    barh(frame=gender, title=u'Пол пациентов', color='gb',
         xlabel='Количество пациентов')

    # Средний возраст
    mean_age = people.groupby('patient.sex').mean()['patient.age']
    barh(frame=mean_age, title=u'Средний возраст пациентов', color='bg',
         xlabel='Возраст')

    # Диагноз
    stents_plot_basic(data=stents,
                      groupby='hospitalization.diagnosis',
                      dataslice=(0, 10),
                      title=u'Диагнозы', color='m',
                      xlabel='Количество пациентов')

    stents_plot_stacked(data=stents,
                        groupby=['hospitalization.diagnosis', 'patient.sex'],
                        sortby=u'муж.',
                        dataslice=(0, 10), figsize=(14, 10),
                        title=u'Распределение диагнозов по полам',
                        color='bg',
                        xlabel='Количество пациентов')

    # Локализация стеноза
    stents_plot_basic(data=stents,
                      groupby='stents.segmentNo',
                      title=u'Локализация стеноза',
                      color='m',
                      xlabel=u'Количество установленных стентов',
                      ylabel=u'Номер сегмента')

    stents_plot_stacked(data=stents,
                        groupby=['stents.segmentNo', 'patient.sex'],
                        sortby=u'муж.',
                        title=u'Распределение локализации стеноза по полам',
                        color='bg', figsize=(14, 10),
                        xlabel='Количество установленных стентов',
                        ylabel=u'Номер сегмента')

    # Тип стеноза
    stents_plot_basic(data=stents, groupby='stents.stenosisType',
                      title=u'Типы стеноза', color='m',
                      xlabel=u'Количество установленных стентов',
                      ylabel=u'Тип стеноза')

    stents_plot_stacked(data=stents,
                        groupby=['stents.stenosisType', 'patient.sex'],
                        sortby=u'муж.',
                        title=u'Распределение типов стеноза по полам',
                        color='bg',
                        xlabel='Количество установленных стентов',
                        ylabel=u'Тип стеноза')

    stents_plot_basic(data=stents,
                      groupby='stents.tortuosityDeg',
                      dataslice=(0, 10),
                      title=u'Извитость', color='m',
                      xlabel='Количество пациентов',
                      ylabel='Степень извитости')

    stents_plot_basic(data=stents,
                      groupby='stents.tortuosityDeg',
                      dataslice=(0, 10),
                      title=u'Кальциноз', color='m',
                      xlabel='Количество пациентов',
                      ylabel='Степень кальциноза')

    frame = stents['stents.predilatation'].value_counts()
    barh(frame=frame, title=u'Предилятация', color='gc',
         xlabel='Количество процедур стентирования')

    frame = stents['stents.postdilatation'].value_counts()
    barh(frame=frame, title=u'Постдилятация', color='gc',
         xlabel='Количество процедур стентирования')

    frame = stents['stents.hResults.success'].value_counts()
    barh(frame=frame, title=u'Результат процедуры', color='gr',
         xlabel='Количество процедур стентирования')

    frame = stents['stents.hResults.replaced'].value_counts()
    barh(frame=frame, title=u'Замена стента', color='gr',
         xlabel='Количество процедур стентирования')

    frame = stents['stents.stent.type'].value_counts()
    barh(frame=frame, title=u'Тип стента', color='gc',
         xlabel='Количество процедур стентирования')

    draw_impressions_chart(people)

    corr_task8(stents)
    print('\n')
    corr_task13(stents)
    print('\n')
    corr_task14(stents)
    print('\n')
    corr_task15(stents)
    print('\n')


def corr_task8(stents):
    # Task 8
    frame = stents[['hospitalization.diagnosis',
                    'stents.segmentNo',
                    'stents.tortuosityDeg',
                    'stents.calcificationDeg']]
    # Replace strings with categories
    frame['hospitalization.diagnosis'] = pd.Categorical.from_array(
        frame['hospitalization.diagnosis']).labels
    frame['stents.tortuosityDeg'] = pd.Categorical.from_array(
        frame['stents.tortuosityDeg']).labels
    frame['stents.calcificationDeg'] = pd.Categorical.from_array(
        frame['stents.calcificationDeg']).labels
    names = {
        'hospitalization.diagnosis': 'Диагноз',
        'stents.segmentNo': 'Номер сегмента',
        'stents.tortuosityDeg': 'Извитость',
        'stents.calcificationDeg': 'Кальциноз'
    }
    frame.rename(columns=names, inplace=True)
    corr = frame.corr()
    print('Таблица коэффициентов корреляций к пункту 8 задания\n\n%s' % corr)


def corr_task13(stents):
    # Task 13
    frame = stents[['stents.stent.len',
                    'stents.stent.dia',
                    'stents.segmentNo',
                    'stents.stenosisType',
                    'stents.tortuosityDeg',
                    'stents.calcificationDeg']]
    # Replace strings with categories
    frame['stents.stenosisType'] = pd.Categorical.from_array(
        frame['stents.stenosisType']).labels
    frame['stents.tortuosityDeg'] = pd.Categorical.from_array(
        frame['stents.tortuosityDeg']).labels
    frame['stents.calcificationDeg'] = pd.Categorical.from_array(
        frame['stents.calcificationDeg']).labels
    avg_len = frame['stents.stent.len'].mean()
    avg_dia = frame['stents.stent.dia'].mean()
    names = {
        'stents.stent.len': 'Длина стента',
        'stents.stent.dia': 'Диаметр стента',
        'stents.stenosisType': 'Тип стеноза',
        'stents.segmentNo': 'Номер сегмента',
        'stents.tortuosityDeg': 'Извитость',
        'stents.calcificationDeg': 'Кальциноз'
    }
    frame.rename(columns=names, inplace=True)
    corr = frame.corr()
    print('Средняя длина стента:   %.2f мм' % avg_len)
    print('Средний диаметр стента: %.2f мм\n' % avg_dia)
    print('Таблица коэффициентов корреляций к пункту 13 задания\n\n%s' % corr)


def corr_task14(stents):
    # Task 14
    frame = stents[['patient.sex',
                    'patient.age',
                    'hospitalization.diagnosis',
                    'stents.stenosisType',
                    'stents.segmentNo',
                    'stents.tortuosityDeg',
                    'stents.calcificationDeg',
                    'stents.hResults.success',
                    'stents.hResults.replaced',
                    'stents.predilatation',
                    'stents.postdilatation',
                    'stents.stent.type']]
    # Replace strings with categories
    frame['patient.sex'] = pd.Categorical.from_array(
        frame['patient.sex']).labels
    frame['hospitalization.diagnosis'] = pd.Categorical.from_array(
        frame['hospitalization.diagnosis']).labels
    frame['stents.stenosisType'] = pd.Categorical.from_array(
        frame['stents.stenosisType']).labels
    frame['stents.tortuosityDeg'] = pd.Categorical.from_array(
        frame['stents.tortuosityDeg']).labels
    frame['stents.calcificationDeg'] = pd.Categorical.from_array(
        frame['stents.calcificationDeg']).labels
    frame['stents.hResults.success'] = pd.Categorical.from_array(
        frame['stents.hResults.success']).labels
    frame['stents.hResults.replaced'] = pd.Categorical.from_array(
        frame['stents.hResults.replaced']).labels
    frame['stents.predilatation'] = pd.Categorical.from_array(
        frame['stents.predilatation']).labels
    frame['stents.postdilatation'] = pd.Categorical.from_array(
        frame['stents.postdilatation']).labels
    frame['stents.stent.type'] = pd.Categorical.from_array(
        frame['stents.stent.type']).labels
    names = {
        'patient.sex': 'Пол',
        'patient.age': 'Возраст',
        'hospitalization.diagnosis': 'Диагноз',
        'stents.stenosisType': 'Тип стеноза',
        'stents.segmentNo': 'Номер сегмента',
        'stents.tortuosityDeg': 'Извитость',
        'stents.calcificationDeg': 'Кальциноз',
        'stents.hResults.success': 'Процедура успешна',
        'stents.hResults.replaced': 'Замена стента',
        'stents.predilatation': 'Предилятация',
        'stents.postdilatation': 'Постдилятация',
        'stents.stent.type': 'Тип стента'
    }
    frame.rename(columns=names, inplace=True)
    corr = frame.corr()
    print('Таблица коэффициентов корреляций к пункту 14 задания\n\n%s' % corr)


def corr_task15(stents):
    # Task 15
    frame = stents[['stents.rResults.problems',
                    'patient.sex',
                    'patient.age',
                    'hospitalization.diagnosis',
                    'stents.stenosisType',
                    'stents.segmentNo',
                    'stents.tortuosityDeg',
                    'stents.calcificationDeg',
                    'stents.hResults.success',
                    'stents.hResults.replaced',
                    'stents.predilatation',
                    'stents.postdilatation',
                    'stents.stent.type']]
    # Replace strings with categories
    frame['stents.rResults.problems'] = pd.Categorical.from_array(
        frame['stents.rResults.problems']).labels
    frame['patient.sex'] = pd.Categorical.from_array(
        frame['patient.sex']).labels
    frame['hospitalization.diagnosis'] = pd.Categorical.from_array(
        frame['hospitalization.diagnosis']).labels
    frame['stents.stenosisType'] = pd.Categorical.from_array(
        frame['stents.stenosisType']).labels
    frame['stents.tortuosityDeg'] = pd.Categorical.from_array(
        frame['stents.tortuosityDeg']).labels
    frame['stents.calcificationDeg'] = pd.Categorical.from_array(
        frame['stents.calcificationDeg']).labels
    frame['stents.hResults.success'] = pd.Categorical.from_array(
        frame['stents.hResults.success']).labels
    frame['stents.hResults.replaced'] = pd.Categorical.from_array(
        frame['stents.hResults.replaced']).labels
    frame['stents.predilatation'] = pd.Categorical.from_array(
        frame['stents.predilatation']).labels
    frame['stents.postdilatation'] = pd.Categorical.from_array(
        frame['stents.postdilatation']).labels
    frame['stents.stent.type'] = pd.Categorical.from_array(
        frame['stents.stent.type']).labels
    names = {
        'stents.rResults.problems': 'Отд. осложнения',
        'patient.sex': 'Пол',
        'patient.age': 'Возраст',
        'hospitalization.diagnosis': 'Диагноз',
        'stents.stenosisType': 'Тип стеноза',
        'stents.segmentNo': 'Номер сегмента',
        'stents.tortuosityDeg': 'Извитость',
        'stents.calcificationDeg': 'Кальциноз',
        'stents.hResults.success': 'Процедура успешна',
        'stents.hResults.replaced': 'Замена стента',
        'stents.predilatation': 'Предилятация',
        'stents.postdilatation': 'Постдилятация',
        'stents.stent.type': 'Тип стента'
    }
    frame.rename(columns=names, inplace=True)
    corr = frame.corr()
    print('Таблица коэффициентов корреляций к пункту 15 задания\n\n%s' % corr)


def exp():
    mpl.rcParams['font.family'] = 'fantasy'
    mpl.rcParams['font.fantasy'] = 'Arial'

    path = './st.csv'

    stents = pd.read_csv(path, index_col=1, encoding='UTF-8', sep='\t')
    # people = stents.groupby(level=0).first()


draw_all()
#exp()
