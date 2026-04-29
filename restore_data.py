import json
import collector_utils as utils

def restore_keywords():
    # 1. 뉴스 키워드 복구
    with open(utils.KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        news_kw = json.load(f)
    print(f"Loaded {len(news_kw)} news keywords from local")
    utils.save_keywords_generic("뉴스키워드관리", utils.KEYWORDS_FILE, news_kw)
    print("Saved news keywords to sheet.")

    # 2. 상위노출 키워드 복구
    with open(utils.RANK_KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        rank_kw = json.load(f)
    print(f"Loaded {len(rank_kw)} rank keywords from local")
    utils.save_keywords_generic("상위노출키워드관리", utils.RANK_KEYWORDS_FILE, rank_kw)
    print("Saved rank keywords to sheet.")

if __name__ == '__main__':
    restore_keywords()
