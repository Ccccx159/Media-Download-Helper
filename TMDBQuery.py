#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, json, re, os
import log

TMDB_API_TOKEN = os.getenv('TMDB_API_TOKEN')

TMDB_API_HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer {}".format(TMDB_API_TOKEN),
}


def get_detail_by_tmdb(info):
    log.logger.debug('开始查询 TMDB 获取 {} 媒体信息!'.format(info['name']))
    search_url = (
        "https://api.themoviedb.org/3/search/{}?query={}&language=zh-CN&page=1".format(
            info["type"], info["name"]
        )
    )
    try:
        res = requests.get(search_url, headers=TMDB_API_HEADERS)
        res.raise_for_status()
    except:
        raise Exception("query by tmdb failed")
        return 'Error', None, '查询 TMDB 失败, 检查网络连接或者 API token 是否正确!'
    tmdb_id = res.json()['results'][0]['id']
    caption = (
        '#影视更新\n'
        + '\[{type_ch}]\n'
        + '片名： *{title}* ({year})\n'
        + '{episode}'
        + '评分： {rating}\n\n'
        + '上映日期： {rel}\n\n'
        + '内容简介： {intro}\n\n'
        + '相关链接： [TMDB](https://www.themoviedb.org/{type}/{tmdbid}?language=zh-CN)\n'
    )
    if info['type'] == 'movie':
        return get_movie_info(tmdb_id, caption)
    elif info['type'] == 'tv':
        info['name'] = res.json()['results'][0]['name']
        return get_tv_info(info, tmdb_id, caption)
    else:
        return 'Error', None, '下载文件类型未知, 无法从 TMDB 获取信息!'
    


def get_movie_info(tmdb_id, caption):
    movie_url = 'https://api.themoviedb.org/3/movie/{}?language=zh-CN'.format(tmdb_id)
    res = requests.get(movie_url, headers=TMDB_API_HEADERS)
    log.logger.debug(res)
    res.raise_for_status()
    movie_detail = res.json()
    caption = caption.format(
        type_ch='电影',
        title=movie_detail['title'],
        year=movie_detail['release_date'].split('-')[0],
        rating=movie_detail['vote_average'],
        rel=movie_detail['release_date'],
        intro=movie_detail['overview'],
        tmdbid=tmdb_id,
        type='movie',
        episode='',
    )
    poster_url = 'https://image.tmdb.org/t/p/w500' + movie_detail['poster_path']
    return 'Success', caption, poster_url


def get_tv_info(info, tmdb_id, caption):
    season = info['series']
    e_match = re.search(r'E\d{2}\b', season)
    if e_match:
        episode = e_match.group()
        season = season.split(episode)[0]
        series = '/season/{}/episode/{}'.format(season[1:], episode[1:])
    else:
        series = '/season/{}'.format(season[1:])
    # 先查询一次 season 信息,获取 poster_path,因为 episode 信息中没有 poster_path
    tv_url = 'https://api.themoviedb.org/3/tv/{}/season/{}?language=zh-CN'.format(tmdb_id, season[1:])
    res = requests.get(tv_url, headers=TMDB_API_HEADERS)
    log.logger.debug(res)
    tv_poster_path = res.json()['poster_path']
    # 查询 season 或 episode 信息
    tv_url = 'https://api.themoviedb.org/3/tv/{}{}?language=zh-CN'.format(
        tmdb_id, series
    )
    res = requests.get(tv_url, headers=TMDB_API_HEADERS)
    log.logger.debug(res)
    res.raise_for_status()
    tv_detail = res.json()
    # print(json.dumps(tv_detail, indent=4))
    caption = caption.format(
        type_ch='剧集',
        title=info['name'] + ' ' + tv_detail['name'],
        year=tv_detail['air_date'].split('-')[0],
        rating=tv_detail['vote_average'],
        rel=tv_detail['air_date'],
        intro=tv_detail['overview'],
        tmdbid=tmdb_id,
        type='tv',
        episode=(
            '已更新至 第{}季 第{}集\n'.format(tv_detail['season_number'], tv_detail['episode_number'])
            if e_match
            else '已更新至 第{}季\n'.format(tv_detail['season_number'])
        ),
    )
    poster_url = 'https://image.tmdb.org/t/p/w500' + tv_poster_path
    return 'Success', caption, poster_url