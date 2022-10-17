import json

# file = 'C:\\서울_행정동.json'
file = './서울_행정동.json'
with open(file, 'r', encoding="UTF-8") as f:
    json_data = json.load(f)

# print(json_data)

행정동리스트 = []
for i in json_data:
    obj = {
        '시군구': i['시군구'],
        '읍면동': i['읍면동'],
        '위도': i['위도'],
        '경도': i['경도']
        }
    행정동리스트.append(obj)
    
print(행정동리스트)





