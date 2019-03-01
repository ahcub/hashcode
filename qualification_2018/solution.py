import random
from datetime import datetime
from multiprocessing.pool import Pool
from operator import itemgetter

import sys


def main():
    started_time = datetime.now()
    file_name = sys.argv[1]
    file = open(file_name)
    n = int(file.readline())

    vertical_photos = []
    horizontal_photos = []
    for i in range(n):
        res = file.readline().split()
        if res[0] == 'H':
            horizontal_photos.append((i, set(res[2:])))
        else:
            vertical_photos.append((i, set(res[2:])))

    print('creating vertical slides')
    vertical_slides = get_vertical_slides(started_time, vertical_photos)

    slides = vertical_slides + horizontal_photos
    print('shuffling slides')
    random.shuffle(slides)

    uber_res_slides = []
    prev_s_i = 0
    result_score = 0
    chunk_size_ = 15000
    print('starting the result slides generation')
    with Pool(3) as pool:
        tasks = []
        for s_i in range(0, len(slides) + chunk_size_, chunk_size_):
            if s_i == 0:
                continue
            ss = slides[prev_s_i: s_i]
            print(prev_s_i, s_i)
            prev_s_i = s_i
            tasks.append(pool.apply_async(calcualate_best_slides, (ss, started_time)))

        for task in tasks:
            res_score, result_slides = task.get()
            result_score += res_score
            uber_res_slides.extend(result_slides)
            print('result_score', result_score)
    print('total_time:', datetime.now() - started_time)
    with open('res_' + file_name, 'w') as res_file:
        res_file.write('{}\n'.format(len(uber_res_slides)))
        for el in uber_res_slides:
            res_file.write('{}\n'.format(el))


def get_vertical_slides(started_time, vertical_photos):
    if not vertical_photos:
        return []
    random.shuffle(vertical_photos)
    print('creating vertical combos')
    vertical_slides = []
    prev_i_v_pho = 0
    with Pool(2) as pool:
        tasks = []
        chunk_size = 5000
        for i_v_pho in range(0, len(vertical_photos) + chunk_size, chunk_size):
            if i_v_pho == 0:
                continue
            print('prev_i_v_pho', prev_i_v_pho, 'i_v_pho', i_v_pho)
            v_pho = vertical_photos[prev_i_v_pho:i_v_pho]
            prev_i_v_pho = i_v_pho
            tasks.append(pool.apply_async(create_v_combos, (v_pho, started_time)))
        for task in tasks:
            vertical_slides.extend(task.get())
    return vertical_slides


def create_v_combos(v_pho, started_time):
    comb = []
    for i, (p_id, tags) in enumerate(v_pho):
        for j, (sp_id, s_tags) in enumerate(v_pho[i + 1:], i + 1):
            comb.append(((p_id, sp_id), (i, j), len(tags ^ s_tags)))
        if i % 10000 == 0:
            print('creating combs', datetime.now() - started_time)

    vertical_slides = []
    drawed_photos = set()
    for i, ((p1, p2), tags, score) in enumerate(sorted(comb, key=itemgetter(2))):
        if p1 not in drawed_photos and p2 not in drawed_photos:
            drawed_photos.add(p1)
            drawed_photos.add(p2)
            vertical_slides.append(('{} {}'.format(p1, p2), v_pho[tags[0]][1] | v_pho[tags[1]][1]))
        if i % 10000 == 0:
            print('generating vertical slides', datetime.now() - started_time)

    return vertical_slides


def calcualate_best_slides(ss, started_time):
    res_score = 0
    result_slides = []
    selected_slides = set()
    result_slides.append(ss[0][0])
    selected_slides.add(ss[0][0])
    print('composing slides')
    last_selected_tags = ss[0][1]
    while True:
        scores = []
        for sp_id, s_tags in ss:
            if sp_id not in selected_slides:
                scores.append((sp_id, s_tags, min(len(last_selected_tags - s_tags),
                                                  len(s_tags - last_selected_tags),
                                                  len(last_selected_tags & s_tags))))
        if not scores:
            break
        selected_photo = sorted(scores, key=itemgetter(2))[-1]
        res_score += selected_photo[2]
        last_selected_tags = selected_photo[1]
        result_slides.append(selected_photo[0])
        selected_slides.add(selected_photo[0])
        if (len(result_slides) % 1000) == 0:
            print(datetime.now() - started_time)
            print(len(result_slides))
    return res_score, result_slides


if __name__ == '__main__':
    main()
