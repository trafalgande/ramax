#!/usr/bin/env python
# coding: utf-8

from sys import argv
import pandas as pd
import datetime
import numba
import numpy as np
import copy
from random import *
from sympy.utilities.iterables import multiset_permutations
from collections import defaultdict

ORIGIN_COLS_TO_RENAME = {
    "Мерчендайзер (ФИО)": "merch",
    "Сеть": "chain",
    "Адрес ТТ": "address",
    "Время в ТТ": "time",
    "Рын. формат": "format",
    "Понедельник": "mon",
    "Вторник": "tue",
    "Среда": "wed",
    "Четверг": "thu",
    "Пятница": "fri",
    "Суббота": "sat",
    "Воскресенье": "sun",
    "Кол-во визитов в неделю": "amount",
}

PLAN_COLS_TO_RENAME = {
    "Код ТТ": "TT_code",
    "Активность": "activity",
    "Наименование клиента": "chain",
    "Адрес клиента": "address",
    "Количество посещений": "amount",
    "Закрепленный за клиентом ТП": "merch",
    "Продолжительность посещения": "duration",
}

# MATRIX_FILE = "input_matrix.csv"
# ORIGIN_FILE = "input_origin.csv"
# PLAN_FILE = "input_plan.csv"
# report_1 = "aa.csv"
# data_out = "bb.csv"
MATRIX_FILE = argv[1]
ORIGIN_FILE = argv[2]
PLAN_FILE = argv[3]
report_1 = argv[4]
data_out = argv[5]

# ENCODE = "UTF-8"
ENCODE = "Windows-1251"


def time_to_minutes(string):
    """
    :param string: string in format hh:mm:ss.
    :return: integer equivalent in minutes.
    """
    try:
        h, m, s = string.split(":")
        return int(h) * 60 + int(m) + int(s) / 60
    except ValueError:
        #         print(string)
        return -1


@numba.jit()
def return_times(way):
    """
    Function gets current way and return different time metrics.
    :param way: way, for what we want to calculate time metrics.
    :returns:
        :store_time: float - spend in stores;
        :way_time: float - time in the way;
        :total_time: float - timetotal time;
        :total_check: boolean - True, if the total time < 9 hours and 30 minutes, else False;
        :store_check: boolean - True, if the store time > 5 hours, else False.
    """

    store_time = np.sum(durations[way])
    way_time = 0
    for start, end in zip(way[:-1], way[1:]):
        way_time += 1.0 * matrix[start, end] / 1000
    total_time = store_time + way_time
    # print(total_time)
    total_check = total_time < 571
    store_check = store_time > 299
    return total_time, store_time, way_time, total_check, store_check


def annealing(cur_order, iters=30, delta_t=0.001, t_max=100):
    """
    Conduct simulated annealing optimisation method.
    :param cur_order: np.array - current order (one, that we want to optimize);
    :param iters: int - max iterations amount;
    :param delta_t: float - delta of temperature;
    :param t_max: - max temperature.
    :return:
        :best_order: np.array - optimized order.
        :best_cost: float - cost for this optimized order.
    """
    t_max = max(t_max, 2)  # for protection
    n = len(cur_order)
    cur_order = copy.deepcopy(cur_order)
    cur_cost, _, _, _, _ = return_times(cur_order)
    best_order = copy.deepcopy(cur_order)
    best_cost = cur_cost
    for _ in range(iters):
        for T in np.arange(t_max, 1, -1 * delta_t):
            i1 = randint(0, n - 1)
            i2 = randint(i1 + 1, n)
            cur_order[i1:i2] = np.flip(cur_order[i1:i2])
            new_cost, _, _, _, _ = return_times(cur_order)

            dE = cur_cost - new_cost
            if dE > 0 and np.exp(-dE / T) > random():
                cur_cost = new_cost
                if cur_cost < best_cost:
                    best_cost = cur_cost
                    best_order = copy.deepcopy(cur_order)
            else:
                cur_order[i1:i2] = np.flip(cur_order[i1:i2])
    return np.array(best_order), best_cost


def brute(cur_order, **params):
    """
    Conduct brute-force search  optimization method.
    :param cur_order: np.array - current order (one, that we want to optimize);
    :return:
        :best_order: np.array - optimized order.
        :best_cost: float - cost for this optimized order.
    """
    cur_order = copy.deepcopy(cur_order)
    cur_cost, _, _, _, _ = return_times(cur_order)
    best_order = copy.deepcopy(cur_order)
    best_cost = cur_cost
    for new_order in multiset_permutations(cur_order):
        new_cost, _, _, _, _ = return_times(new_order)
        if new_cost < best_cost:
            best_cost = new_cost
            best_order = copy.deepcopy(new_order)
    return np.array(best_order), best_cost


def search(cur_order, **params):
    """
    Conduct optimization method, that is chosen depending on the length of input array.
    :param cur_order: np.array - current order (one, that we want to optimize);
    :return:
        :best_order: np.array - optimized order.
        :best_cost: float - cost for this optimized order.
    """
    if len(cur_order) > 7:
        return annealing(cur_order, **params)
    else:
        return brute(cur_order, **params)


def check(points):
    """
    Function check corectness of the found order.
    :param points: cur order of merchandiser.
    """
    min_store_time = 100000000
    for day in week:
        store_time = 0
        total_time = 0
        first = True
        for i in range(len(points)):
            p = points[i]
            if p in day2way[day]:
                if first:
                    first = False
                    store_time += code2duration[p]
                    total_time += +code2duration[p]

                else:
                    store_time += code2duration[p]
                    total_time += (
                            1.0 * matrix[points[i - 1], p] / 1000 + code2duration[p]
                    )
        if store_time > 0:
            min_store_time = min(min_store_time, store_time)
        if total_time > 570:
            if min_store_time < 000:
                return 11
            return -1

    if min_store_time < 000:
        return 1
    return 0


def score_calc(points):
    """
    Calculates current order's score.
    :param points: current order.
    :return:
        :total_time: total time of the work;
        :store_time: time at store.
    """
    store_time = 0
    total_time = 0
    for day in week:

        first = True
        for i in range(len(points)):
            p = points[i]

            if p in day2way[day]:
                if first:
                    first = False
                    store_time += code2duration[p]
                    total_time += code2duration[p]
                else:
                    store_time += code2duration[p]
                    total_time += (
                            1.0 * matrix[points[i - 1], p] / 1000 + code2duration[p]
                    )
    return total_time, store_time


def return_metrics(day2merch2way):
    """
    Returns the metrics for the answer report.
    :param day2merch2way: dict of dicts day_of_week->merchandiser->current_way
    :return: all the necessary metrics
    """
    unique_merch = set()
    unique_TT = set()
    merch2dist = defaultdict(list)
    # Metric order: total_time, store_time, way_time, total_check, store_check
    sum_dist = 0
    sum_time = 0
    amount_of_days = 0
    #     print(day2merch2way)
    for day in day2merch2way:
        unique_merch.update(day2merch2way[day].keys())
        if len(day2merch2way[day].keys()) > 0:
            amount_of_days += 1
            for merch in day2merch2way[day].keys():
                unique_TT.update(day2merch2way[day][merch])
                (
                    total_time,
                    store_time,
                    way_time,
                    total_check,
                    store_check,
                ) = return_times(day2merch2way[day][merch])
                sum_dist += way_time
                sum_time += total_time / 60
                merch2dist[merch].append(way_time * 1000)
    TT_amount = len(unique_TT)  # Число ТТ
    merch_amount = len(unique_merch)  # Число Мерчендайзеров
    avg_dist = (
            sum_dist / amount_of_days / merch_amount
    )  # Суммарная средняя траектория всех ТП, км
    sum_dist  # Суммарная траектория всех маршрутов всех ТП, км
    avg_time = (
            sum_time / amount_of_days / merch_amount
    )  # Средняя длительность рабочего дня для ТП
    sum_time  # Общая продолжительность работы всех ТП, час

    return TT_amount, merch_amount, avg_dist, sum_dist, avg_time, sum_time


def add_minutes(date, minutes):
    """
    Add minutes to the date (in datetime format).
    """
    return date + datetime.timedelta(0, minutes * 60)


def get_date(date):
    """
    Returns date in dd.mm.yyyy - string format from date parameter (in datetime format).
    """
    return date.strftime("%d.%m.%Y")


def get_time(date):
    """
    Returns time in HH.MM - string format from date parameter (in datetime format).
    """
    return date.strftime("%H:%M")


def get_dayofweek(date):
    """
    Returns day of week in string format from date parameter (in datetime format).
    """
    return date.strftime("%A")


def min_to_hours(time):
    """
    Returns hours in HH.MM - string format from integer time in hours.
    """
    time /= 60

    hours = int(time)
    minutes = (time * 60) % 60

    return "%d:%02d" % (hours, minutes)


# =====================================
# READING FILES AND MERGING TO DATAFRAME
# =====================================
print("Reading files...")

matrix = np.genfromtxt(MATRIX_FILE, delimiter=",")

origin = pd.read_csv(ORIGIN_FILE, encoding=ENCODE)
origin = origin.rename(columns=ORIGIN_COLS_TO_RENAME)
origin["duration"] = origin["time"].apply(time_to_minutes)

plan = pd.read_csv(PLAN_FILE, encoding=ENCODE)
plan = plan.drop([0]).reset_index()
plan = plan.drop(
    [
        "index",
        "Широта",
        "Долгота",
        "Код сети",
        "День посещения",
        "Начало посещения",
        "Конец посещения",
        "Название/адрес",
    ],
    axis=1,
)
plan = plan.rename(columns=PLAN_COLS_TO_RENAME)
plan.amount = plan.amount.astype(int)
plan.TT_code = plan.TT_code.astype(int) - 1

merged_info = pd.concat(
    [plan.add_prefix("plan_"), origin.add_prefix("origin_")], axis=1
)
assert sum(merged_info.plan_address != merged_info.origin_address) == 0
assert sum(merged_info.plan_merch != merged_info.origin_merch) == 0
assert sum(merged_info.plan_chain != merged_info.origin_chain) == 0
assert sum(merged_info.plan_amount != merged_info.origin_amount) == 0
assert sum(merged_info.plan_activity != 1) == 0

# Там в origin.time есть несколько странных значений с AM,
# и из нее не понятно, как преобразовывать в origin_duration,
# НО! Воспользуемся duration из plan.
merged_info = merged_info.drop(
    [
        "plan_address",
        "plan_merch",
        "plan_chain",
        "plan_amount",
        "plan_activity",
        "origin_time",
        "origin_duration",
    ],
    axis=1,
)
# merged_info = add_lat_long(merged_info, "origin_address", True)


# =====================================
# CONSTRUCTING USEFUL DICTS and ARRAYS
# =====================================
print("Constructing dictionaries...")

address2code = dict(merged_info[["origin_address", "plan_TT_code"]].to_numpy())
code2address = dict(merged_info[["plan_TT_code", "origin_address"]].to_numpy())
code2duration = dict(merged_info[["plan_TT_code", "plan_duration"]].to_numpy())
code2chain = dict(merged_info[["plan_TT_code", "origin_chain"]].to_numpy())
code2freq = dict(merged_info[["plan_TT_code", "origin_amount"]].to_numpy())
merch2way = dict(merged_info.groupby("origin_merch")["plan_TT_code"].apply(np.array))

week = [
    "origin_mon",
    "origin_tue",
    "origin_wed",
    "origin_thu",
    "origin_fri",
    "origin_sat",
    "origin_sun",
]

day2merch2way = dict()
day2way = dict()
for day in week:
    day2way[day] = np.array(merged_info[merged_info[day].notna()].plan_TT_code.tolist())
    day2merch2way[day] = (
        merged_info[merged_info[day].notna()]
            .groupby(["origin_merch"])["plan_TT_code"]
            .apply(np.array)
    )

durations = np.array(list(code2duration.values()))
return_times(np.array([i for i in range(5)]))

# =====================================
# FIRST STAGE
# (constructing optimized way for all).
# =====================================
print("First stage (Rostik's one)...")

path, score = search(np.array([i for i in range(204)]))
path_stored = copy.deepcopy(path)
best_score = 1000000
best_store_time = 0
best_points = []
for i in range(204):
    cur_merch = 0
    cur_score = 0
    now_points = []
    saved = []
    saved_j = 0
    result = []

    score = 0
    j = 0
    while j <= 204:

        j += 1
        point = path[(i + j) % 204]
        res = check(now_points + [point])

        if res == 0:
            now_points = now_points + [point]
            saved = now_points
            saved_j = j
            cur_merch += 1
        elif res == 1:
            now_points = now_points + [point]

        elif res == -1:
            if saved:
                result.append(saved[:] + [])
                now_points = []
                saved = []
                j = saved_j
                cur_merch += 1
            else:
                break
        elif res == 11:
            break
        if j == 204:
            R = 0
            S = 0
            for merch_points in result:
                t_time, s_time = score_calc(merch_points)
                R += t_time
                S += s_time
            if R < best_score:
                best_score = R
                best_points = result
                best_store_time = S


print("Done first stage!")
print(best_score, best_points, len(best_points), best_store_time)
points_overall = set()
for point in best_points:
    points_overall.update(point)

print(f'Check length: {len(points_overall)}')


# =====================================
# DICTS FOR ANSWERS
# =====================================
print("Making answers...")

week2code = []
for day in week:
    week2code.append(merged_info.dropna(axis=0, subset=[day]).plan_TT_code.tolist())

rost_day2merch2way = defaultdict(lambda: defaultdict(list))

for i, points in enumerate(best_points):  # Для каждого мерчендайзера
    for day, day2code in zip(week, week2code):  # для каждого дня недели
        for p in points:  # берем точку мерчендайзера
            if p in day2code:
                rost_day2merch2way[day][f"МЕРЧЕНДАЙЗЕР_{i}"].append(p)

new_day2merch2way = defaultdict(lambda: defaultdict(list))

for day in rost_day2merch2way:
    print(day)
    for merch in rost_day2merch2way[day].keys():
        if len(rost_day2merch2way[day][merch]) > 0:
            best_order, best_cost = search(
                np.array(rost_day2merch2way[day][merch]), iters=5, delta_t=0.01
            )
            new_day2merch2way[day][merch] = best_order

print("Aggregating results...")

before = return_metrics(day2merch2way)
after = return_metrics(new_day2merch2way)
results = np.zeros([4, 6])
results[:2] = np.array([before, after])
results[2] = results[0] - results[1]
results[3] = results[2] / results[0] * 100
results = pd.DataFrame(
    results.T,
    index=[
        "Число ТТ",
        "Число Мерчендайзеров",
        "Суммарная средняя траектория всех ТП, км",
        "Суммарная траектория всех маршрутов всех ТП, км",
        "Средняя длительность рабочего дня для ТП",
        "Общая продолжительность работы всех ТП, час",
    ],
    columns=[
        "До оптимизации",
        "После оптимизации",
        "Дельта",
        "Относительное изменение, %",
    ],
)

start_dates = [
    datetime.datetime(2020, 5, 18, 9, 0, 0),
    datetime.datetime(2020, 5, 19, 9, 0, 0),
    datetime.datetime(2020, 5, 21, 9, 0, 0),
    datetime.datetime(2020, 5, 22, 9, 0, 0),
    datetime.datetime(2020, 5, 23, 9, 0, 0),
]

name_to_date = {
    "origin_mon": datetime.datetime(2020, 5, 18, 9, 0, 0),
    "origin_tue": datetime.datetime(2020, 5, 19, 9, 0, 0),
    "origin_thu": datetime.datetime(2020, 5, 21, 9, 0, 0),
    "origin_fri": datetime.datetime(2020, 5, 22, 9, 0, 0),
    "origin_sat": datetime.datetime(2020, 5, 23, 9, 0, 0),
}

new_answer_data = pd.DataFrame(
    columns=[
        "Дата посещения",
        "День недели",
        "Торговый представитель",
        "Номер точки маршрута",
        "Название точки",
        "Адрес точки",
        "Время прибытия",
        "Продолжительность посещения",
        "Частота посещения ( раз в неделю)",
        "Дистанция до следующей",
    ]
)

for day in new_day2merch2way:
    if len(new_day2merch2way[day].keys()) > 0:
        for merch in new_day2merch2way[day].keys():
            cur_date = name_to_date[day]
            size = len(new_day2merch2way[day][merch])
            for i in range(size):
                point = new_day2merch2way[day][merch][i]
                answer = []
                answer.append(get_date(cur_date))  # Дата посещения
                answer.append(get_dayofweek(cur_date))  # День недели
                answer.append(merch)  # Торговый представитель
                answer.append(i + 1)  # Номер точки маршрута
                answer.append(code2chain[point])  # Название точки
                answer.append(code2address[point].replace("\xa0", " "))  # Адрес точки
                answer.append(get_time(cur_date))  # Время прибытия
                answer.append(
                    min_to_hours(code2duration[point])
                )  # Продолжительность посещения
                answer.append(code2freq[point])  # Частота посещения ( раз в неделю)
                cur_date += datetime.timedelta(0, code2duration[point] * 60)
                if i + 1 < size:
                    next_point = new_day2merch2way[day][merch][i + 1]
                    answer.append(
                        matrix[point, next_point] / 1000
                    )  # Дистанция до следующей
                    cur_date += datetime.timedelta(
                        0, matrix[point, next_point] / 1000 * 60
                    )
                else:
                    answer.append(-1)
                new_answer_data = new_answer_data.append(
                    pd.DataFrame([answer], columns=new_answer_data.columns),
                    ignore_index=True,
                )

results.to_csv(report_1, encoding=ENCODE)
new_answer_data.to_csv(data_out, index=False, encoding=ENCODE)
