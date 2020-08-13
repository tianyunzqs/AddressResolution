在空余时间收集整理数据集的时候，发现了行政区划的数据集，并正好找到了[DQinYuan](https://github.com/DQinYuan/chinese_province_city_area_mapper)大佬写的一个cpca工具，于是依葫芦画瓢，自己动手实现了一个简易版本（我构思中的一些功能，cpca没有提供，于是才有了该工具）。
# 1.简介
该工具提供的功能如下：  
1. 根据输入的地址解析出省市区，及其下标位置；（与cpca类似）
2. 支持添加省份，添加市，添加区县；（主要是考虑由于历史或地域原因，有些省市区县名字更换或取消或新增，而数据库中未收录）
3. 根据地址查询区号；
4. 根据区号查询地址；
5. 根据地址查询邮政编码；
6. 根据邮政编码查询地址；
7. 支持添加区号和邮政编码。
# 2.代码解析
地址解析的主要代码由`resolution`函数实现，该函数利用`jieba`分词对输入地址进行分词后，依次匹配省市区信息，如果匹配到对应信息，则将其填充到`result`中的对应字段，并记录该字段所在的下标。如果`result`中的省、市字段未在输入原文中出现，而是通过行政区划词典推理得到（某些区县对应的省市信息是唯一的），则那些推理出来的字段下标保持初始化[-1, -1]不变。
```python
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
```
支持用户添加省、市、区县的功能分别由`add_province`、`add_city`、`add_county`函数实现，考虑到用户添加的省、市、区县未必与代码中规定的格式相同，因此在添加到省、市、区县之前都会对用户输入的省、市、区县进行标准化处理（`__standardize_province`、`__standardize_city`,  `__standardize_county`），如此一来即可兼容用户添加的省、市、区县信息。具体实现逻辑可参考Github源码。
# 3.测试示例
**解析地址中的省、市、区县信息**
```python
[In] print(resolution('湖北武汉东西湖区金银潭医院'))
[Out] {'province': '湖北省', 'city': '武汉市', 'county': '东西湖区', 'province_loc': [0, 2], 'city_loc': [2, 4], 'county_loc': [4, 8], 'address': '金银潭医院'}
```
**用户添加省、市、区县信息**
```python
[In] print(resolution('台湾台北市松山区台北松山机场'))
[Out] {'province': '内蒙古自治区', 'city': '赤峰市', 'county': '松山区', 'province_loc': [-1, -1], 'city_loc': [-1, -1], 'county_loc': [5, 8], 'address': '台北松山机场'}
```
由于台湾省未在行政区划词典中（[中华人民共和国民政局全国行政区划查询平台](http://xzqh.mca.gov.cn/map)未收录），而内蒙古也有个松山区，因此会将台湾省的松山机场匹配到内蒙古。
当用户添加台湾省后，就不会存在上述情况。
```python
# 添加省
add_province('台湾省')
[In] print(resolution('台湾台北市松山区台北松山机场'))
[Out] {'province': '台湾省', 'city': '', 'county': '', 'province_loc': [0, 2], 'city_loc': [-1, -1], 'county_loc': [-1, -1], 'address': '台北市松山区台北松山机场'}
# 添加市
[In] add_city('台湾省', '台北市')
[In] print(resolution('台湾台北市松山区台北松山机场'))
[Out] {'province': '台湾省', 'city': '台北市', 'county': '', 'province_loc': [0, 2], 'city_loc': [2, 5], 'county_loc': [-1, -1], 'address': '松山区台北松山机场'}
# 添加区县
[In] add_county('台湾省', '台北市', '松山区')
[In] print(resolution('台湾台北市松山区台北松山机场'))
[Out] {'province': '台湾省', 'city': '台北市', 'county': '松山区', 'province_loc': [0, 2], 'city_loc': [2, 5], 'county_loc': [5, 8], 'address': '台北松山机场'}
```
**查区号**
```python
# 根据地址查询区号
[In] print(query_area_code('湖北武汉东西湖区金银潭医院'))
[Out] {'top1': '027', 'top2': '', 'top3': ''}
# 根据区号查询地址
[In] print(query_area_code('027'))
[Out] {'top1': '湖北省武汉市', 'top2': '湖北省鄂州市华容区', 'top3': ''}
```
ps：湖北省鄂州市华容区正在试行027区号
**查邮政编码**
```python
# 根据地址查询邮政编码
[In] print(query_post_code('湖北武汉东西湖区金银潭医院'))
[Out] {'top1': '430040', 'top2': '', 'top3': ''}
# 根据邮政编码查询地址
[In] print(query_post_code('430040'))
[Out] {'top1': '湖北省武汉市东西湖区', 'top2': '', 'top3': ''}
```
# 后记
代码中的行政区划数据爬取自[中华人民共和国民政局全国行政区划查询平台](http://xzqh.mca.gov.cn/map)  
ps:爬虫代码或数据均可关注公众号【NLPer笔记簿】获取，回复“爬虫”获取爬虫代码；回复“行政区划”获取完整数据。  
公众号【NLPer笔记簿】已连接该工具，可关注公众号体验
![1.png](https://upload-images.jianshu.io/upload_images/20501279-41adbe47239b0f40.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![2.png](https://upload-images.jianshu.io/upload_images/20501279-97876e6113bd7136.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

