# -*- coding: utf-8 -*-
# @Time        : 2020/8/7 11:09
# @Author      : tianyunzqs
# @Description : 

import re
import csv
import jieba


seg_tokenizer = jieba.Tokenizer()
province = dict()
city_province = dict()
county_city_province = dict()
location_to_area_code = dict()
area_code_to_location = dict()
location_to_post_code = dict()
post_code_to_location = dict()


def __standardize_province(province_name):
    for k, standard_province in province.items():
        if province_name in k:
            seg_tokenizer.add_word(word=province_name)
            return standard_province
    seg_tokenizer.add_word(word=province_name)
    return province_name


def add_province(province_name, standard=True):
    if not province_name:
        return
    if province_name in province:
        return
    if standard:
        standard_province_name = __standardize_province(province_name)
        province[province_name] = standard_province_name
    if province_name not in province:
        province[province_name] = province_name
        seg_tokenizer.add_word(word=province_name)
    new_province_name = re.sub(r'省$', '', province_name)
    new_province_name = re.sub(r'市$', '', new_province_name)
    new_province_name = re.sub(r'维吾尔自治区$', '', new_province_name)
    new_province_name = re.sub(r'壮族自治区$', '', new_province_name)
    new_province_name = re.sub(r'回族自治区$', '', new_province_name)
    new_province_name = re.sub(r'自治区$', '', new_province_name)
    new_province_name = re.sub(r'特别行政区$', '', new_province_name)
    if new_province_name not in province:
        province[new_province_name] = province_name
        seg_tokenizer.add_word(word=new_province_name)


def __standardize_city(province_name, city_name):
    standard_province = __standardize_province(province_name)
    for k, standard_province_city in city_province.items():
        if city_name in k:
            if standard_province_city[0] == standard_province:
                seg_tokenizer.add_word(word=city_name)
                return standard_province_city
    seg_tokenizer.add_word(word=city_name)
    return standard_province, city_name


def add_city(province_name, city_name, standard=True):
    if not city_name or '省直辖县级行政单位' == city_name:
        return
    if city_name in city_province:
        return
    if standard:
        standard_province_city = __standardize_city(province_name, city_name)
        # 添加省份
        add_province(province_name)
        # 添加市
        if city_name not in city_province:
            city_province[city_name] = standard_province_city
    if city_name not in city_province:
        city_province[city_name] = (province_name, city_name)
        seg_tokenizer.add_word(word=city_name)
    new_city_name = re.sub('(市|盟|地区)$', '', city_name)
    new_city_name = re.sub('土家族苗族自治州$', '', new_city_name)
    new_city_name = re.sub('布依族苗族自治州$', '', new_city_name)
    new_city_name = re.sub('哈尼族彝族自治州$', '', new_city_name)
    new_city_name = re.sub('傣族景颇族自治州$', '', new_city_name)
    new_city_name = re.sub('蒙古族藏族自治州$', '', new_city_name)
    new_city_name = re.sub('苗族侗族自治州$', '', new_city_name)
    new_city_name = re.sub('壮族苗族自治州$', '', new_city_name)
    new_city_name = re.sub('藏族羌族自治州$', '', new_city_name)
    new_city_name = re.sub('柯尔克孜自治州$', '', new_city_name)
    new_city_name = re.sub('傈僳族自治州$', '', new_city_name)
    new_city_name = re.sub('白族自治州$', '', new_city_name)
    new_city_name = re.sub('回族自治州$', '', new_city_name)
    new_city_name = re.sub('蒙古自治州$', '', new_city_name)
    new_city_name = re.sub('藏族自治州$', '', new_city_name)
    new_city_name = re.sub('彝族自治州$', '', new_city_name)
    new_city_name = re.sub('哈萨克自治州$', '', new_city_name)
    new_city_name = re.sub('朝鲜族自治州$', '', new_city_name)
    new_city_name = re.sub('特别行政区$', '', new_city_name)
    if new_city_name not in city_province:
        city_province[new_city_name] = (province_name, city_name)
        seg_tokenizer.add_word(word=new_city_name)


def __standardize_county(province_name, city_name, county_name):
    standard_province_city = __standardize_city(province_name, city_name)
    for k, standard_province_city_county in county_city_province.items():
        if county_name in k:
            vaild_result = {item for item in standard_province_city_county
                            if item[0] == standard_province_city[0] and item[1] == standard_province_city[1]}
            if vaild_result:
                seg_tokenizer.add_word(word=county_name)
                return vaild_result
    seg_tokenizer.add_word(word=county_name)
    return {(standard_province_city[0], standard_province_city[1], county_name)}


def add_county(province_name, city_name, county_name, standard=True):
    if not county_name:
        return
    if standard:
        standard_province_city_county = __standardize_county(province_name, city_name, county_name)
        # 添加省份
        add_province(province_name)
        # 添加市
        add_city(province_name, city_name)
        # 添加区县
        if county_name not in county_city_province:
            county_city_province[county_name] = standard_province_city_county
        else:
            county_city_province[county_name] |= standard_province_city_county
    else:
        if county_name not in county_city_province:
            county_city_province[county_name] = {(province_name, city_name, county_name)}
            seg_tokenizer.add_word(word=county_name)
        else:
            county_city_province[county_name].add((province_name, city_name, county_name))
    if len(county_name) <= 2:
        return
    new_county_name = re.sub('(市|县|地区|区)$', '', county_name)
    if new_county_name not in county_city_province:
        county_city_province[new_county_name] = {(province_name, city_name, county_name)}
        seg_tokenizer.add_word(word=new_county_name)
    else:
        county_city_province[new_county_name].add((province_name, city_name, county_name))


def add_area_code(province_name, city_name, county_name, area_code):
    if province_name not in location_to_area_code:
        location_to_area_code[province_name] = {city_name: {county_name: area_code}}
    else:
        if city_name not in location_to_area_code[province_name]:
            location_to_area_code[province_name][city_name] = {county_name: area_code}
        else:
            if county_name not in location_to_area_code[province_name][city_name]:
                location_to_area_code[province_name][city_name][county_name] = area_code

    if area_code not in area_code_to_location:
        area_code_to_location[area_code] = {province_name: {city_name: {county_name}}}
    else:
        if province_name not in area_code_to_location[area_code]:
            area_code_to_location[area_code][province_name] = {city_name: {county_name}}
        else:
            if city_name not in area_code_to_location[area_code][province_name]:
                area_code_to_location[area_code][province_name][city_name] = {county_name}
            else:
                area_code_to_location[area_code][province_name][city_name].add(county_name)


def add_post_code(province_name, city_name, county_name, post_code):
    if province_name not in location_to_post_code:
        location_to_post_code[province_name] = {city_name: {county_name: post_code}}
    else:
        if city_name not in location_to_post_code[province_name]:
            location_to_post_code[province_name][city_name] = {county_name: post_code}
        else:
            if county_name not in location_to_post_code[province_name][city_name]:
                location_to_post_code[province_name][city_name][county_name] = post_code

    if post_code not in post_code_to_location:
        post_code_to_location[post_code] = {province_name: {city_name: {county_name}}}
    else:
        if province_name not in post_code_to_location[post_code]:
            post_code_to_location[post_code][province_name] = {city_name: {county_name}}
        else:
            if city_name not in post_code_to_location[post_code][province_name]:
                post_code_to_location[post_code][province_name][city_name] = {county_name}
            else:
                post_code_to_location[post_code][province_name][city_name].add(county_name)


def _load_dict():
    data = csv.DictReader(open('../dict_models/xzqhxxb.csv', 'r', encoding='utf-8'))
    for item in data:
        add_province(item['province_name'], standard=False)
        add_city(item['province_name'], item['city_name'], standard=False)
        add_county(item['province_name'], item['city_name'], item['county_name'], standard=False)
        if item['area_code']:
            add_area_code(item['province_name'], item['city_name'], item['county_name'], item['area_code'])
        if item['post_code']:
            add_post_code(item['province_name'], item['city_name'], item['county_name'], item['post_code'])


_load_dict()
seg_tokenizer.initialize()


def resolution(location):
    if not isinstance(location, str) or not location:
        raise Exception('input must string.')
    result = {
        'province': '',
        'city': '',
        'county': '',
        'province_loc': [-1, -1],
        'city_loc': [-1, -1],
        'county_loc': [-1, -1],
        'address': ''
    }

    def __set_province(word, loc):
        result['province'] = province[word]
        result['province_loc'] = [loc, loc + len(word)]

    def __set_city(word, loc):
        result['city'] = city_province[word][1]
        result['city_loc'] = [loc, loc + len(word)]
        if not result['province']:
            result['province'] = city_province[word][0]

    def __set_county(word, loc):
        candidate_province_city_county = list(county_city_province[word])
        for item in candidate_province_city_county:
            if result['province']:
                if item[0] == result['province']:
                    if result['city']:
                        if item[1] == result['city']:
                            result['county'] = item[2]
                            result['county_loc'] = [loc, loc + len(word)]
                            return
                    else:
                        # 如果相同省份，相同区县对应的市有多个（如江苏省南京市鼓楼区和江苏省徐州市鼓楼区），则不填充市
                        if len(set([d[1] for d in candidate_province_city_county if d[0] == result['province']])) == 1:
                            result['city'] = item[1]
                        result['county'] = item[2]
                        result['county_loc'] = [loc, loc + len(word)]
                        return
            else:
                if result['city']:
                    if item[1] == result['city']:
                        if len(set([d[0] for d in candidate_province_city_county if d[1] == result['city']])) == 1:
                            result['province'] = item[0]
                else:
                    if len(candidate_province_city_county) == 1:
                        result['province'], result['city'] = item[0], item[1]
                result['county'] = item[2]
                result['county_loc'] = [loc, loc + len(word)]

    loc = 0
    words = seg_tokenizer.lcut(location)
    for word in words:
        if word in province and not result['province']:
            __set_province(word, loc)
        elif word in city_province and not result['city']:
            __set_city(word, loc)
        elif word in county_city_province and not result['county']:
            __set_county(word, loc)
        loc += len(word)
    if not result['city'] and result['province'] in ('北京市', '上海市', '天津市', '重庆市'):
        result['city'] = result['province']
    vaild_loc = [v[1] for k, v in result.items() if k in ('province_loc', 'city_loc', 'county_loc') and v[1] > -1]
    result['address'] = location[max(vaild_loc):] if vaild_loc else location
    return result


def query_area_code(location):
    result = {'top1': '', 'top2': '', 'top3': ''}
    location = location.strip()
    # 根据地址查询区号
    std_loc = resolution(location)
    if std_loc['province'] and std_loc['province'] in location_to_area_code:
        if std_loc['city'] and std_loc['city'] in location_to_area_code[std_loc['province']]:
            if std_loc['county'] and std_loc['county'] in location_to_area_code[std_loc['province']][std_loc['city']]:
                result['top1'] = location_to_area_code[std_loc['province']][std_loc['city']][std_loc['county']]
                return result
            elif '' in location_to_area_code[std_loc['province']][std_loc['city']]:
                result['top1'] = location_to_area_code[std_loc['province']][std_loc['city']]['']
                return result
            else:
                city_number = set(location_to_area_code[std_loc['province']][std_loc['city']].values())
                if len(city_number) == 1:
                    result['top1'] = list(city_number)[0]
                    return result

    # 根据区号查询地址
    if location in area_code_to_location:
        province_map = area_code_to_location[location]
        if len(province_map) == 1:
            city_map = list(province_map.values())[0]
            if len(city_map) == 1:
                county_map = list(city_map.values())[0]
                if '' in county_map:
                    result['top1'] = list(province_map.keys())[0] + list(city_map.keys())[0]
                    return result
                elif len(county_map) == 1:
                    result['top1'] = list(province_map.keys())[0] + list(city_map.keys())[0] + list(county_map)[0]
                    return result
            else:
                city_map_sorted = sorted(city_map.items(), key=lambda x: len(x[1]), reverse=True)
                for i, (city_name, county_names) in enumerate(city_map_sorted):
                    if i > 2:
                        return result
                    if '' in county_names:
                        result['top' + str(i + 1)] = list(province_map.keys())[0] + city_name
                    elif len(county_names) == 1:
                        result['top' + str(i + 1)] = list(province_map.keys())[0] + city_name + list(county_names)[0]
    return result


def query_post_code(location):
    result = {'top1': '', 'top2': '', 'top3': ''}
    location = location.strip()
    # 根据地址查询邮政编码
    std_loc = resolution(location)
    if std_loc['province'] and std_loc['province'] in location_to_post_code:
        if std_loc['city'] and std_loc['city'] in location_to_post_code[std_loc['province']]:
            if std_loc['county'] and std_loc['county'] in location_to_post_code[std_loc['province']][std_loc['city']]:
                result['top1'] = location_to_post_code[std_loc['province']][std_loc['city']][std_loc['county']]
                return result
            elif '' in location_to_post_code[std_loc['province']][std_loc['city']]:
                result['top1'] = location_to_post_code[std_loc['province']][std_loc['city']]['']
                return result
            else:
                city_number = set(location_to_post_code[std_loc['province']][std_loc['city']].values())
                if len(city_number) == 1:
                    result['top1'] = list(city_number)[0]
                    return result

    # 根据邮政编码查询地址
    if location in post_code_to_location:
        province_map = post_code_to_location[location]
        if len(province_map) == 1:
            city_map = list(province_map.values())[0]
            if len(city_map) == 1:
                county_map = list(city_map.values())[0]
                if '' in county_map:
                    result['top1'] = list(province_map.keys())[0] + list(city_map.keys())[0]
                    return result
                elif len(county_map) == 1:
                    result['top1'] = list(province_map.keys())[0] + list(city_map.keys())[0] + list(county_map)[0]
                    return result
            else:
                city_map_sorted = sorted(city_map.items(), key=lambda x: len(x[1]), reverse=True)
                for i, (city_name, county_names) in enumerate(city_map_sorted):
                    if i > 2:
                        return result
                    if '' in county_names:
                        result['top' + str(i + 1)] = list(province_map.keys())[0] + city_name
                    elif len(county_names) == 1:
                        result['top' + str(i + 1)] = list(province_map.keys())[0] + city_name + list(county_names)[0]
    return result


if __name__ == '__main__':
    print(resolution('湖北武汉东西湖区金银潭医院'))
    print(resolution('台湾台北市松山区台北松山机场'))
    add_province('台湾省')
    print(resolution('台湾台北市松山区台北松山机场'))
    add_city('台湾省', '台北市')
    print(resolution('台湾台北市松山区台北松山机场'))
    add_county('台湾省', '台北市', '松山区')
    print(resolution('台湾台北市松山区台北松山机场'))

    print(query_area_code('湖北武汉东西湖区金银潭医院'))
    print(query_area_code('027'))

    print(query_post_code('湖北武汉东西湖区金银潭医院'))
    print(query_post_code('430040'))
