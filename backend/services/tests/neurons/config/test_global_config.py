from backend.services.neurons.config import global_config


class TestRunGlobalConfig:
    def test_it_should_execute_without_errors(self):
        assert global_config.run(global_config.Config()) is None
