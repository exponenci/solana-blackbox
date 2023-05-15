def pure_virtual_function():
    raise RuntimeError('ClusterNode: virtual function must be defined!')


class Cluster:
    def configure(self) -> None:
        pure_virtual_function()

    def start(self) -> None:
        pure_virtual_function()

    def stop(self) -> None:
        pure_virtual_function()

    def clear(self) -> None:
        pure_virtual_function()
