from db.Price import Price


def get_name_from_callback(callback):
    article_info = [int(i) for i in callback.data[3:].split(':')]

    if article_info[1] == -1:
        ans = Price.get_items()[article_info[0]]
        return ans.name if type(ans) != str else ans

    elif article_info[2] == -1:
        ans = Price.get_items()[article_info[0]].get_items()[article_info[1]]
        return ans.name if type(ans) != str else ans

    elif article_info[3] == -1:
        ans = Price.get_items()[article_info[0]].get_items()[article_info[1]].get_items()[article_info[2]]
        return ans.name if type(ans) != str else ans

    elif article_info[4] == -1:
        ans = Price.get_items()[article_info[0]].get_items()[article_info[1]].get_items()[article_info[2]].get_items()[article_info[3]]
        return ans.name if type(ans) != str else ans