from datetime import datetime
from operator import itemgetter

file_name = 'c_memorable_moments.txt'
file = open(file_name)
n = int(file.readline())

photos = []
vertical_photos = []
horizontal_photos = []
for i in range(n):
    res = file.readline().split()
    if res[0] == 'H':
        horizontal_photos.append((i, set(res[2:])))
    else:
        vertical_photos.append((i, set(res[2:])))

comb = []
for i, (p_id, tags) in enumerate(vertical_photos):
    for sp_id, s_tags in vertical_photos[i+1:]:
        comb.append(((p_id, sp_id), (tags | s_tags), len(tags ^ s_tags)))

vertical_slides = []
drawed_photos = set()
print('composing vertical pairs')
for (p1, p2), tags, score in sorted(comb, key=itemgetter(2)):
    if p1 not in drawed_photos and p2 not in drawed_photos:
        drawed_photos.add(p1)
        drawed_photos.add(p2)
        vertical_slides.append(('{} {}'.format(p1, p2), tags))

slides = vertical_slides + horizontal_photos

result_slides = []
selected_slides = set()

result_slides.append(slides[0][0])
selected_slides.add(slides[0][0])
result_score = 0

print('composing slides')
last_selected_tags = slides[0][1]
started_time = datetime.now()
while True:
    scores = []
    for sp_id, s_tags in slides:
        if sp_id not in selected_slides:
            scores.append((sp_id, s_tags, min(len(last_selected_tags - s_tags), len(s_tags - last_selected_tags), len(last_selected_tags & s_tags))))
    if not scores:
        break
    selected_photo = sorted(scores, key=itemgetter(2))[-1]
    result_score += selected_photo[2]
    last_selected_tags = selected_photo[1]
    result_slides.append(selected_photo[0])
    selected_slides.add(selected_photo[0])
    if (len(result_slides) % 100) == 0:
        print(datetime.now() - started_time)
        print(len(result_slides))

print('result_score', result_score)
with open('res' + file_name, 'w') as res_file:
    res_file.write('{}\n'.format(len(result_slides)))
    for el in result_slides:
        res_file.write('{}\n'.format(el))
