# crawl_zigbang.py
from encodings import utf_8
import requests
import json
from pprint import pprint

# ! 찾은 방정보에서 추출할 데이터 다시 정리
# ! 웹에서 필터할 정보를 생각해보고 추출할 데이터를 정하자

SUBWAY_LIST_URL="https://apis.zigbang.com/property/biglab/subway/all?"
ROOM_LIST_URL="https://apis.zigbang.com/v3/items/ad/{subway_id}?subway_id={subway_id}&radius=1&sales_type=&deposit_s=0&rent_s=0&floor=1~%7Crooftop%7Csemibase&domain=zigbang&detail=false"
ROOM_INFO_URL="https://apis.zigbang.com/v2/items/{room_id}"


빌라_LIST_URL = "https://apis.zigbang.com/v2/items?domain=zigbang&needHasNoFiltered=true&new_villa=true&radius=1&sales_type_in=%EC%A0%84%EC%84%B8&subway_id={subway_id}"
빌라_INFO_URL = "https://apis.zigbang.com/v2/items/{villa_id}"

아파트_LIST_URL = "https://apis.zigbang.com/property/biglab/apartments/list?type=subway&id={subway_id}&serviceType[0]=apt&serviceType[1]=offer&serviceType[2]=preOffer&limit=5&order=viewCount"
아파트_INFO_URL = "https://apis.zigbang.com/apt/danjis/{apt_id}"

#오피스텔은 공인중개사로 검색해서 추천매물, 일반매물 리스트를 가져온다.
오피스텔_LIST_URL = "https://apis.zigbang.com/v2/officetels?radius=1&subway_id={subway_id}" 
오피스텔_INFO_URL = "https://apis.zigbang.com/v2/items/{op_id}"



 
지하철역리스트 = ['중곡역','군자역','어린이대공원역','건대입구역','뚝섬유원지역','구의역','강변역','광나루역','아차산역']

# 지하철 정보 수집
def getSubwayId( subway_name ):
    REQUEST_URL = SUBWAY_LIST_URL
 
    req = requests.get( SUBWAY_LIST_URL )
    if req.status_code == 200:
        data = json.loads( req.text )
 
        subway_info = [ item['id'] for item in data if item['name'] == subway_name ]
 
        if len(subway_info) > 0:
            return subway_info[0]
 
    return None
 
# 매물 목록 수집
def getRoomList( subway_id ):
    REQUEST_URL = ROOM_LIST_URL.format( subway_id=subway_id )
 
    req = requests.get( REQUEST_URL )
    if req.status_code == 200:
        data = json.loads( req.text )
 
        return [ item["simple_item"]["item_id"] for item in data["list_items"] if 'ad_agent' not in item ]
 
    return list()
 
# 매물 상세정보 수집
def getRoomInfo( room_id ):
    REQUEST_URL = ROOM_INFO_URL.format( room_id=room_id )
 
    req = requests.get( REQUEST_URL )
    if req.status_code == 200:
        data = json.loads( req.text )
 
        return data
    
    return None
 
# 매물 상세정보를 입맞대로 파싱
def parseRoomInfo( room_info, find_text=None ):
    # parsed_data = {
    #     "url": 'https://www.zigbang.com/home/oneroom/items/{}'.format( room_info["item"].get("item_id") )
    #     , "item_id": room_info["item"].get("item_id")
    #     , "제목": room_info["item"].get("title")
    #     , "주소": ( room_info["item"].get("local1"), room_info["item"].get("local2"), room_info["item"].get("local3"), room_info["item"].get("local4") )
    #     , "설명": {
    #         "요약": room_info["item"].get("agent_comment")
    #         , "상세내용": room_info["item"].get("description")
    #     }
    #     , "정보": {
    #         "사진": room_info["item"].get("images")
    #         , "전세/월세": room_info["item"].get("sales_type")
    #         , "방": room_info["item"].get("service_type")
    #         , "층수": "{}/{}".format( room_info["item"].get("floor"),  room_info["item"].get("floor_all") )
    #     }
    #     , "비용": {
    #         "관리비": room_info["item"].get("manage_cost")
    #         , "보증금액": room_info["item"].get("보증금액")
    #         , "월세금액": room_info["item"].get("월세금액")
    #     }
    #     , "면적": {
    #         "공급면적_m2": room_info["item"].get("공급면적_m2")
    #         , "대지권면적_m2": room_info["item"].get("대지권면적_m2")
    #         , "전용면적_m2": room_info["item"].get("전용면적_m2")
    #     }
    #     , "중개사": room_info["agent"].get("owner")
    # }

    # room_info["객체명"].get("속성명")
    parsed_data = {
        '제목': room_info['item'].get('title'),
        '주소': room_info['item'].get('address'),
        '지번주소': room_info['item'].get('jibunAddress'),

        # 좌표가 정확하진 않아.. 마커클러스터할땐 이거쓰고, 상세하게 보여줄때는 지번주소로 검색
        '좌표': room_info['item'].get('random_location'), 
        '정보': {
            '사진': room_info['item'].get('images'),
            '썸네일': room_info['item'].get('image_thumbnail'),
            '전세/월세': room_info['item'].get('sales_type'),
            '방': room_info['item'].get('service_type'),
            '층수': room_info['item'].get('floor'), # '1','2','3', '반지하', '옥탑방' 
            '총층수': room_info['item'].get('floor_all'),
            '상세내용': room_info['item'].get('description'),

            # 타입 코드 :
            # 원룸인경우 01 = 분리형, 02 = 오픈형, 03 = 복층형, 04 = 투룸, 05 = 쓰리룸+, 06 = 포룸+
            '타입': room_info['item'].get('room_type'),
            '화장실': room_info['item'].get('bathroom_count'),
            '주택타입': room_info['item'].get('residence_type'), # 다세대주택, 주택, 공동주택

            #'주차가능', '1대가능' 이런식으로 써있다. 그대로 이용하면 될듯
            '주차': room_info['item'].get('parking'),
            '엘리베이터': room_info['item'].get('elevator'), # true / false
            '즉시입주': room_info['item'].get('movein_date'),
            '준공': room_info['item'].get('approve_date'), # 얘는 날짜 타입이 제각각... 따로 조정필요
            '방향': room_info['item'].get('room_direction'), # "S" ,"SW" 이런식

            #  확정 01 에어컨,   02 = 냉장고,     03 세탁기,   04 = 가스레인지,
            #       05 = 인덕션, 06 = 전자레인지, 07 = 책상,   08 = 책장, 
            #       09 = 침대,   10 = 옷장,       11 = 신발장, 12 = 싱크대
            '옵션': room_info['item'].get('options') 
        },
        '비용':{
            '관리비': room_info['item'].get('manage_cost'),
            
            # 관리비 옵션코드는 같은 코드를 공유한다.
            #  확정 03 = 수도, 04 = 인터넷, 05 = 티비
            '관리비포함': room_info['item'].get('manage_const_inc'),

            # 01 02 03 전기 가스 수도
            # 01 02 03 04 05 전기, 가스, 수도, 인터넷, 티비
            '관리비별도': room_info['item'].get('manage_const_not_inc'),
            '보증금액': room_info['item'].get('보증금액'),
            '월세금액': room_info['item'].get('월세금액')
        },
        '면적':{
            '공급면적_m2': room_info['item'].get('공급면적_m2'),
            '대지권면적_m2': room_info['item'].get('대지권면적_m2'),
            '전용면적_m2': room_info['item'].get('전용면적_m2')
        },
        '중개사': {
            '이름': room_info['agent'].get('agent_title'),
            '주소': room_info['agent'].get('agent_address'),
            '전화': room_info['agent'].get('agent_phone'),
            '소개': room_info['agent'].get('agent_intro'),
            '직원정보': room_info['agent'].get('owner'),
        },
        '지하철': room_info['subways']
    }

    # if find_text is not None:
    #     if  parsed_data['설명']['상세내용'].find( find_text ) > 0:
    #         return parsed_data
    #     return None
    return parsed_data

방_리스트 = [] 
# 지하철 정보 수집
def 크롤링(subway_name):    
    # subway_name = '아차산역'
    subway_id = getSubwayId( subway_name )
    
    if subway_id is not None:
        # 매물 id 목록 수집 요청
        room_list = getRoomList( subway_id ) # 수유역=96
        count = 0;
        for room_id in room_list:
            # 매물 상세 정보 수집 요청
            room_info = getRoomInfo( room_id )
            # 매물 상세정보를 입맞대로 파싱
            parend_room_info = parseRoomInfo( room_info)
    
            if parend_room_info is not None: 
                방_리스트.append(parend_room_info)
                
            count = count + 1
            if(count == 3) : return
        
    else:
        return

# 크롤링 실행 ( 테스트 성공하고, 파일에 데이터를 저장하고 싶다면 이 함수를 사용)
def start():
    for subway in 지하철역리스트:
        크롤링(subway)
        file_name = '{subway_name}.txt'
        f = open(file_name.format(subway_name = subway),'w', encoding='UTF-8')
        str = repr(방_리스트)
        f.write(str)
        f.close()

def test():
    크롤링('아차산역')
    pprint(방_리스트)
test()