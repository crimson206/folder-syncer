from typing import List, Union
import fnmatch


def _filter_path(
    path: str, include: List[str], exclude: List[str]
) -> Union[str, None]:
    # include 리스트가 비어있지 않으면 먼저 확인
    if include:
        if not any(fnmatch.fnmatch(path, pattern) for pattern in include):
            return None

    # exclude 리스트의 패턴과 일치하면 None 반환
    if any(fnmatch.fnmatch(path, pattern) for pattern in exclude):
        return None

    return path


def filter_path(
    path: str, include: Union[str, List[str]], exclude: Union[str, List[str]]
) -> Union[str, None]:
    # include와 exclude를 항상 리스트로 변환
    include_list = [include] if isinstance(include, str) else include
    exclude_list = [exclude] if isinstance(exclude, str) else exclude

    # 빈 문자열이나 None 값은 빈 리스트로 처리
    include_list = [p for p in include_list if p]
    exclude_list = [p for p in exclude_list if p]

    return _filter_path(path, include_list, exclude_list)


def filter_paths(
    paths: List[str], include: Union[str, List[str]], exclude: Union[str, List[str]]
) -> List[str]:

    filtered_paths = [filter_path(path, include, exclude) for path in paths if filter_path(path, include, exclude) is not None]

    return filtered_paths
