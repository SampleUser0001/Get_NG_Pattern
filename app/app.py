# -*- coding: utf-8 -*-
import os
import sys
import json
import glob
import MeCab
from difflib import SequenceMatcher , Differ

OUTPUT_NG_PATTERN = '/app/output/ng_pattern'

# jsonファイルの読み込み
CHAT_KEYS = ["authorExternalChannelId","user","timestampUsec","time","authorbadge","text","purchaseAmount","type","video_id","Chat_No"]
DICT_CHAT_CHANNNELID = 0
DICT_CHAT_TEXT = 5
DICT_CHAT_KEY = 9

# 形態素解析結果
MORPHOLOGICAL_ANALYSIS_KEYS = ["mplg_words","mplg_text","mplg_soup"]
INDEX_MPLG_WORDS = 0
INDEX_MPLG_TEXT = 1
INDEX_MPLG_SOUP = 2

# 形態素解析結果差分
SIMILARITY_DIFF_KEYS = ["origin_authorExternalChannelId", "diff_chat_no", "diff_authorExternalChannelId", "similarity"]
INDEX_SIMILARITY_ORIGIN_CHANNEL_ID = 0
INDEX_SIMILARITY_DIFF_CHAT_NO = 1
INDEX_SIMILARITY_DIFF_CHANNEL_ID = 2
INDEX_SIMILARITY = 3

# 辞書ファイルパス
DIC_PATH = ' -d /usr/local/mecab/lib/mecab/dic/mecab-ipadic-neologd'

def read_comment_json(input_file):
    """ コメントjsonを読み込む
    """
    return_dict = {}

    with open(INPUT_FILE, mode='r') as f:
        comments = json.load(f)
        for comment in comments:
            return_dict[comment[CHAT_KEYS[DICT_CHAT_KEY]]] = comment

    return return_dict

def morphological_analysis(comments_dict):
    """ 形態素解析を行い、dict型で返す。
    形態素解析結果はCHAT_KEYS[DICT_CHAT_KEY]の値をキーにしたdict型で返す。
    """
    return_dict = {}
    for key in comments_dict:
        # コメントを取得
        comment = comments_dict[key][CHAT_KEYS[DICT_CHAT_TEXT]]

        # print(comment)

        # 形態素解析を行う
        words, text = mplg_edit(comment)
        soup = mplg(comment)

        # dict型に変換して返す。
        mplg_result = {
            MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_WORDS]: words ,
            MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_TEXT]: text ,
            MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_SOUP]: soup }
        return_dict[key] = mplg_result

    return return_dict

def mplg(text):
    """ 形態素解析を行う。
    """
    m = MeCab.Tagger(DIC_PATH)
    soup = m.parse (text)
    return soup

def mplg_edit(text):
    """ 形態素解析を行う。必要な項目だけ取得する。
    TODO: 必要な項目を絞り込む
    """
    output_words = []
    output_text  = ''
    # 辞書へのパス
    m = MeCab.Tagger(DIC_PATH)
    soup = m.parse (text)
    for row in soup.split("\n"):
        word =row.split("\t")[0]
        if word == "EOS":
            break
        else:
            pos = row.split("\t")[1]
            slice = pos.split(",")
            if len(word) > 1:
                if slice[0] == "名詞":
                    output_words.append(word)
                    output_text = output_text + ' ' + word
                elif slice[0] in [ "形容詞" , "動詞", "副詞"]:
                    if slice[5] == "基本形":
                        output_words.append(slice[-3])#活用していない原型を取得
                        output_text = output_text + ' ' + slice[-3]
    return output_words,output_text

def get_over_length_keys(mplg_dict, length):
    """ コメントの形態素解析結果のサイズがlength以上のkeyの一覧を返す。
    """
    return_list = []
    for key in mplg_dict:
        if len(mplg_dict[key][MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_SOUP]].splitlines()) > length:
            return_list.append(key)
    return return_list

def merge_mplg(mplg_dict, threshold, keys):
    """ 類似度がsimilarity以上の要素をまとめる
    """

    return_keys_dict = {}
    
    for key in keys:
        for dict_key in return_keys_dict:
            similarity = SequenceMatcher(
                None,
                mplg_dict[key][MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_SOUP]],
                mplg_dict[dict_key][MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_SOUP]]).ratio()
            if similarity > threshold:
                return_keys_dict[dict_key].append(key)
                break

        # 類似パターンが見つからない。パターンの一つとして登録する。
        return_keys_dict[key] = []

    return return_keys_dict

def output_ng_pattern(output_dir, keys, mplg_dict):
    """ 形態素解析結果をファイルに書き出す
    """
    for key in keys:
        with open(output_dir + '/' + key + '.txt' , mode='w') as f:
            f.write(mplg_dict[key][MORPHOLOGICAL_ANALYSIS_KEYS[INDEX_MPLG_SOUP]])


if __name__ == '__main__':
    args_index = 0
    args_index = args_index + 1

    VIDEO_ID = sys.argv[args_index] ; args_index = args_index + 1;
    INPUT_FILE = sys.argv[args_index] ; args_index = args_index + 1;

    # コメントファイルをdictに変換する。
    item_dict = read_comment_json(INPUT_FILE)

    # 取得したコメントファイルのコメントを形態素解析する。
    mplg_dict = morphological_analysis(item_dict)

    # NGにするパターンを取得する。
    # 形態素解析結果が50行以上
    over_length_keys = get_over_length_keys(mplg_dict, 50)
    
    # 類似度が0.8以上の形態素解析をまとめる
    merged_keys = merge_mplg(mplg_dict, 0.8, over_length_keys)

    output_keys = []
    for key in merged_keys:
        # 類似パターンが存在する場合のみ出力する。
        if len(merged_keys[key]) > 0:
            output_keys.append(key)
            
    output_ng_pattern(OUTPUT_NG_PATTERN + '/' + VIDEO_ID, output_keys, mplg_dict)
    