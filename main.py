from collect_links import CollectLinks
from collect_info import CollectInfo
from list_urls import list_categories
from glob import glob
import csv
import os
import gc


def select_files_in_directories(name_directory: str):
    current_path = f"{os.getcwd()}/{name_directory}/*"
    path_to_files = (
        glob(f"{path_directory}/*", recursive=True)[0]
        for path_directory in glob(current_path, recursive=True)
    )
    return path_to_files


def read_file(category, sub_category) -> list:
    current_path = os.getcwd()
    path_to_file = f'{current_path}/{category}/{sub_category}/{sub_category}.csv'
    with open(path_to_file, 'r') as file:
        head = (
            'Sku', 'Product_url', 'EAN', 'ISBN13', 'ISBN10', 'Title', 'Condition', 'Author', 'Binding_type',
            'Publisher',
            'Category', 'Stock', 'AuthorBiography', 'Summary', 'Reviews', 'Image', 'RRP', 'Price'
        )
        reader = tuple(csv.DictReader(file, head))
        list_data = []
        for data in reader:
            if data['Product_url'] != 'Product_url':
                list_data.append(data)
        return list_data


def main():
    max_connections_to_website = 150

    for category_key, values in list_categories.items():
        for i, url_link in enumerate(values):
            sub_category = f"{category_key}_part_{i}"
            all_links_and_data = CollectLinks(max_connections_to_website, category_key, sub_category, url_link)

            if not all_links_and_data.main():
                break

            del all_links_and_data
            gc.collect()

        for i, path in enumerate(select_files_in_directories(category_key)):
            sub_category = f"{category_key}_part_{i}"
            data = read_file(category_key, sub_category)
            collect_data = CollectInfo(max_connections_to_website, category_key, sub_category, data)
            if not collect_data.main():
                break

            del data
            del collect_data
            gc.collect()


if __name__ == '__main__':
    main()
