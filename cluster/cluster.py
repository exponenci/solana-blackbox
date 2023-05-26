def pure_virtual_function():
    raise RuntimeError('ClusterNode: virtual function must be defined!')


class Cluster:
    def start(self, *args, **kwargs) -> None:
        pure_virtual_function()

    def run_client(self, *args, **kwargs) -> None:
        pure_virtual_function()

    def stop(self, *args, **kwargs) -> None:
        pure_virtual_function()
