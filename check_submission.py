"""Проверка answer.csv по требованиям сдачи.

Запуск: python check_submission.py path/to/answer.csv path/to/data_dir
"""
import re
import sys

import pandas as pd


def check(answer_path: str, data_dir: str) -> None:
    ans = pd.read_csv(answer_path, dtype=str, keep_default_na=False)
    query_ids = set(pd.read_parquet(f'{data_dir}/benchmark_queries.parquet', columns=['query_id'])['query_id'])
    item_ids = set(pd.read_parquet(f'{data_dir}/benchmark_items.parquet', columns=['item_id'])['item_id'])

    assert list(ans.columns) == ['query_id', 'answer'], f'нужны ровно колонки query_id, answer, а не {list(ans.columns)}'
    assert ans['query_id'].is_unique, 'есть повторы query_id'
    assert set(ans['query_id']) == query_ids, 'набор query_id не совпадает с benchmark_queries (пропуски или лишние)'
    assert ans['query_id'].str.len().eq(16).all(), 'query_id должен быть из 16 символов'

    rows = ans['answer'].str.split()
    assert rows.map(len).le(50).all(), 'в строке больше 50 item_id'
    assert rows.map(lambda r: len(r) == len(set(r))).all(), 'повторы item_id внутри строки'
    used = {i for r in rows for i in r}
    assert used <= item_ids, f'{len(used - item_ids)} item_id нет в benchmark_items'
    assert all(re.fullmatch(r'[0-9a-f]{16}', i) for i in used), 'item_id не в формате 16 символов 0-9a-f'

    print(f'OK: {len(ans)} строк, item_id в строке от {rows.map(len).min()} до {rows.map(len).max()}')


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv) > 1 else 'answer.csv', sys.argv[2] if len(sys.argv) > 2 else 'data')
