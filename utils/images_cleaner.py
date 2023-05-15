import subprocess
from typing import List


def get_none_images() -> List[str]:
    all_images = subprocess.run(['docker', 'images'], check=True, stdout=subprocess.PIPE).stdout
    all_images = all_images.split(b'\n')[1:-1]
    return list(map(
        lambda info: info[2].decode(), 
            filter(
            lambda info: info[0] == b'<none>', 
            map(
                lambda info: info.split(), 
                all_images
            )
        )
    ))


def get_image_containers(images: List[str]) -> List[str]:
    all_containers = subprocess.run(['docker', 'container', 'ls', '--all'], check=True, stdout=subprocess.PIPE).stdout
    all_containers = all_containers.split(b'\n')[1:-1]
    result_containers = list()
    for container in all_containers:
        if container.split()[1].decode() in images:
            result_containers.append(container.split()[0].decode())
    return result_containers


def remove_containers(containers: List[str]):
    subprocess.run(['docker', 'container', 'rm', *containers], check=True)


def remove_images(images: List[str]):
    subprocess.run(['docker', 'image', 'rm', *images], check=True)



def main():
    none_images = get_none_images()
    none_containers = get_image_containers(none_images)
    remove_containers(none_containers)
    remove_images(none_images)


if __name__ == '__main__':
    main()
